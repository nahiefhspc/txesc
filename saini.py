import os
import re
import time
import mmap
import datetime
import aiohttp
import aiofiles
import asyncio
import logging
import requests
import subprocess
import concurrent.futures
from math import ceil
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
from pyrogram import Client
from pyrogram.types import Message

# Utility function to get video duration using ffprobe
def duration(filename):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", filename
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        return float(result.stdout)
    except Exception as e:
        logging.error(f"Error getting duration for {filename}: {e}")
        return 0

# Function to fetch MPD and keys from an API (placeholder)
def get_mps_and_keys(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        response_json = response.json()
        mpd = response_json.get('MPD')
        keys = response_json.get('KEYS')
        return mpd, keys
    except Exception as e:
        logging.error(f"Error fetching MPD and keys: {e}")
        return None, None

# Execute a command and capture output
def exec(cmd):
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = process.stdout.decode()
        logging.info(output)
        return output
    except Exception as e:
        logging.error(f"Error executing command {cmd}: {e}")
        return str(e)

# Run multiple commands concurrently
def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        logging.info("Waiting for tasks to complete")
        fut = executor.map(exec, cmds)

# Async download for PDFs
async def download(url, name):
    ka = f'{name}.pdf'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(ka, mode='wb') as f:
                        await f.write(await resp.read())
                    return ka
                else:
                    logging.error(f"Failed to download {url}: Status {resp.status}")
                    return None
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return None

# Async download for PDFs with chunked streaming
async def pdf_download(url, file_name, chunk_size=1024 * 10):
    try:
        if os.path.exists(file_name):
            os.remove(file_name)
        r = requests.get(url, allow_redirects=True, stream=True)
        r.raise_for_status()
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    fd.write(chunk)
        return file_name
    except Exception as e:
        logging.error(f"Error downloading PDF {url}: {e}")
        return None

# Parse video info from yt-dlp output
def vid_info(info):
    try:
        info = info.strip().split("\n")
        new_info = {}
        temp = []
        for i in info:
            i = str(i)
            if "[" not in i and '---' not in i:
                while "  " in i:
                    i = i.replace("  ", " ")
                i = i.strip().split("|")[0].split(" ", 3)
                try:
                    if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                        temp.append(i[2])
                        new_info.update({f'{i[2]}': f'{i[0]}'})
                except:
                    pass
        return new_info
    except Exception as e:
        logging.error(f"Error parsing video info: {e}")
        return {}

# Decrypt and merge M3U8 video
async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality="720"):
    try:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Download video and audio streams
        cmd1 = (
            f'yt-dlp -f "bv[height<={quality}]+ba/b" -o "{output_path}/file.%(ext)s" '
            f'--allow-unplayable-format --no-check-certificate --external-downloader aria2c "{mpd_url}"'
        )
        logging.info(f"Running command: {cmd1}")
        subprocess.run(cmd1, shell=True, check=True)

        # List downloaded files
        avDir = list(output_path.iterdir())
        logging.info(f"Downloaded files: {avDir}")
        logging.info("Decrypting")

        video_decrypted = False
        audio_decrypted = False

        # Decrypt video and audio
        for data in avDir:
            if data.suffix == ".mp4" and not video_decrypted:
                cmd2 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/video.mp4"'
                logging.info(f"Running command: {cmd2}")
                subprocess.run(cmd2, shell=True, check=True)
                if (output_path / "video.mp4").exists():
                    video_decrypted = True
                data.unlink()
            elif data.suffix == ".m4a" and not audio_decrypted:
                cmd3 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/audio.m4a"'
                logging.info(f"Running command: {cmd3}")
                subprocess.run(cmd3, shell=True, check=True)
                if (output_path / "audio.m4a").exists():
                    audio_decrypted = True
                data.unlink()

        if not video_decrypted or not audio_decrypted:
            raise FileNotFoundError("Decryption failed: video or audio file not found.")

        # Merge video and audio
        cmd4 = (
            f'ffmpeg -i "{output_path}/video.mp4" -i "{output_path}/audio.m4a" '
            f'-c copy "{output_path}/{output_name}.mp4"'
        )
        logging.info(f"Running command: {cmd4}")
        subprocess.run(cmd4, shell=True, check=True)

        # Clean up temporary files
        if (output_path / "video.mp4").exists():
            (output_path / "video.mp4").unlink()
        if (output_path / "audio.m4a").exists():
            (output_path / "audio.m4a").unlink()

        filename = output_path / f"{output_name}.mp4"
        if not filename.exists():
            raise FileNotFoundError("Merged video file not found.")

        # Get duration
        cmd5 = f'ffmpeg -i "{filename}" 2>&1 | grep "Duration"'
        duration_info = subprocess.run(cmd5, shell=True, capture_output=True, text=True).stdout
        logging.info(f"Duration info: {duration_info}")

        return str(filename)

    except Exception as e:
        logging.error(f"Error during decryption and merging: {str(e)}")
        raise

# Async command execution
async def run(cmd):
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        if proc.returncode == 1:
            return False
        if stdout:
            return f'[stdout]\n{stdout.decode()}'
        if stderr:
            return f'[stderr]\n{stderr.decode()}'
    except Exception as e:
        logging.error(f"Error running command {cmd}: {e}")
        return False

# Download video using yt-dlp
async def download_video(url, cmd, name):
    global failed_counter
    failed_counter = 0
    download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
    logging.info(download_cmd)
    try:
        subprocess.run(download_cmd, shell=True, check=True)
        if os.path.isfile(name):
            return name
        elif os.path.isfile(f"{name}.webm"):
            return f"{name}.webm"
        name_base = name.split(".")[0]
        for ext in [".mkv", ".mp4", ".mp4.webm"]:
            if os.path.isfile(f"{name_base}{ext}"):
                return f"{name_base}{ext}"
        raise FileNotFoundError(f"No video file found for {name}")
    except Exception as e:
        logging.error(f"Error downloading video {url}: {e}")
        if "visionias" in cmd and failed_counter <= 10:
            failed_counter += 1
            await asyncio.sleep(5)
            return await download_video(url, cmd, name)
        raise

# Send video to Telegram
async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog):
    try:
        subprocess.run(
            f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 "{filename}.jpg"',
            shell=True, check=True
        )
        await prog.delete(True)
        reply = await m.reply_text(f"**Generate Thumbnail:**\n{name}")
        thumbnail = f"{filename}.jpg" if thumb == "/d" else thumb
        dur = int(duration(filename))
        start_time = time.time()

        try:
            await m.reply_video(
                filename,
                caption=cc,
                supports_streaming=True,
                height=720,
                width=1280,
                thumb=thumbnail,
                duration=dur,
                progress=progress_bar,
                progress_args=(reply, start_time)
            )
        except Exception:
            await m.reply_document(
                filename,
                caption=cc,
                progress=progress_bar,
                progress_args=(reply, start_time)
            )
        await reply.delete(True)
    except Exception as e:
        logging.error(f"Error sending video {filename}: {e}")
        await m.reply_text(f"Error sending video: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(f"{filename}.jpg"):
            os.remove(f"{filename}.jpg")

# Decrypt a file (XOR-based, not used for M3U8)
def decrypt_file(file_path, key):
    try:
        if not os.path.exists(file_path):
            return False
        with open(file_path, "r+b") as f:
            num_bytes = min(28, os.path.getsize(file_path))
            with mmap.mmap(f.fileno(), length=num_bytes, access=mmap.ACCESS_WRITE) as mmapped_file:
                for i in range(num_bytes):
                    mmapped_file[i] ^= ord(key[i]) if i < len(key) else i
        return True
    except Exception as e:
        logging.error(f"Error decrypting file {file_path}: {e}")
        return False

# Human-readable file size
def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

# Generate timestamped filename
def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date} {current_time}.mp4"
