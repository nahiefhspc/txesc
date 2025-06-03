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
import tgcrypto
import subprocess
import concurrent.futures
from math import ceil
from utils import progress_bar
from pyrogram import Client, filters
from pyrogram.types import Message
from io import BytesIO
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import ffmpeg  # Import ffmpeg-python

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# AES Key and IV for decryption
KEY = b'^#^#&@*HDU@&@*()'
IV = b'^@%#&*NSHUE&$*#)'

# Check for FFmpeg installation (required for ffmpeg-python)
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info("FFmpeg is installed and accessible.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("FFmpeg is not installed or not found in PATH. Please install FFmpeg.")
        return False

# Check for mp4decrypt installation (if used)
def check_mp4decrypt():
    try:
        subprocess.run(['mp4decrypt', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info("mp4decrypt is installed and accessible.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.warning("mp4decrypt is not installed or not found in PATH. Required for encrypted video decryption.")
        return False

# Check for yt-dlp installation
def check_ytdlp():
    try:
        subprocess.run(['yt-dlp', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info("yt-dlp is installed and accessible.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.error("yt-dlp is not installed or not found in PATH. Please install yt-dlp.")
        return False

# Check for aria2c installation
def check_aria2c():
    try:
        subprocess.run(['aria2c', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        logging.info("aria2c is installed and accessible.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logging.warning("aria2c is not installed or not found in PATH. Required for fast downloads.")
        return False

# Run dependency checks at startup
if not check_ffmpeg():
    raise RuntimeError("FFmpeg is required but not installed. Please install FFmpeg.")
check_mp4decrypt()  # Optional, only warn if missing
if not check_ytdlp():
    raise RuntimeError("yt-dlp is required but not installed. Please install yt-dlp.")
check_aria2c()  # Optional, only warn if missing

# Decryption function
def dec_url(enc_url):
    enc_url = enc_url.replace("helper://", "")
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    decrypted = unpad(cipher.decrypt(b64decode(enc_url)), AES.block_size)
    return decrypted.decode('utf-8')

# Function to split name & Encrypted URL
def split_name_enc_url(line):
    match = re.search(r"(helper://\S+)", line)
    if match:
        name = line[:match.start()].strip().rstrip(":")
        enc_url = match.group(1).strip()
        return name, enc_url
    return line.strip(), None

# Function to decrypt file URLs
def decrypt_file_txt(input_file):
    output_file = "decrypted_" + input_file
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(input_file, "r", encoding="utf-8") as f, open(output_file, "w", encoding="utf-8") as out:
        for line in f:
            name, enc_url = split_name_enc_url(line)
            if enc_url:
                dec = dec_url(enc_url)
                out.write(f"{name}: {dec}\n")
            else:
                out.write(line.strip() + "\n")
    return output_file

# Get video duration using ffprobe
def duration(filename):
    try:
        probe = ffmpeg.probe(filename)
        duration = float(probe['format']['duration'])
        logging.info(f"Duration of {filename}: {duration} seconds")
        return duration
    except ffmpeg.Error as e:
        logging.error(f"Failed to get duration for {filename}: {str(e)}")
        return 0

# Get MPD and keys from API
def get_mps_and_keys(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        response_json = response.json()
        mpd = response_json.get('MPD')
        keys = response_json.get('KEYS')
        return mpd, keys
    except requests.RequestException as e:
        logging.error(f"Failed to fetch MPD and keys from {api_url}: {str(e)}")
        return None, None

# Execute shell command
def exec(cmd):
    try:
        process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        output = process.stdout
        logging.info(f"Command executed: {cmd}\nOutput: {output}")
        return output
    except subprocess.SubprocessError as e:
        logging.error(f"Command failed: {cmd}\nError: {str(e)}")
        return ""

# Run commands concurrently
def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        logging.info("Waiting for tasks to complete")
        fut = executor.map(exec, cmds)

# Async download for PDFs
async def aio(url, name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(k, mode='wb') as f:
                    await f.write(await resp.read())
                logging.info(f"Downloaded PDF: {k}")
                return k
            logging.error(f"Failed to download PDF from {url}: Status {resp.status}")
            return None

# Async download for PDFs (alternative)
async def download(url, name):
    ka = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                async with aiofiles.open(ka, mode='wb') as f:
                    await f.write(await resp.read())
                logging.info(f"Downloaded PDF: {ka}")
                return ka
            logging.error(f"Failed to download PDF from {url}: Status {resp.status}")
            return None

# Download PDF with requests
async def pdf_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    try:
        r = requests.get(url, allow_redirects=True, stream=True)
        r.raise_for_status()
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    fd.write(chunk)
        logging.info(f"Downloaded PDF: {file_name}")
        return file_name
    except requests.RequestException as e:
        logging.error(f"Failed to download PDF from {url}: {str(e)}")
        return None

# Parse video info
def parse_vid_info(info):
    info = info.strip().split("\n")
    new_info = []
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i = i.strip().split("|")[0].split(" ", 2)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    new_info.append((i[0], i[2]))
            except IndexError:
                pass
    return new_info

# Parse video info into dictionary
def vid_info(info):
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
                    new_info[i[2]] = i[0]
            except IndexError:
                pass
    return new_info

# Decrypt and merge video
async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality="720"):
    try:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        cmd1 = f'yt-dlp -f "bv[height<={quality}]+ba/b" -o "{output_path}/file.%(ext)s" --allow-unplayable-format --no-check-certificate --external-downloader aria2c "{mpd_url}"'
        logging.info(f"Running command: {cmd1}")
        os.system(cmd1)
        avDir = list(output_path.iterdir())
        logging.info(f"Downloaded files: {avDir}")
        logging.info("Decrypting")
        video_decrypted = False
        audio_decrypted = False
        for data in avDir:
            if data.suffix == ".mp4" and not video_decrypted:
                cmd2 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/video.mp4"'
                logging.info(f"Running command: {cmd2}")
                os.system(cmd2)
                if (output_path / "video.mp4").exists():
                    video_decrypted = True
                data.unlink()
            elif data.suffix == ".m4a" and not audio_decrypted:
                cmd3 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/audio.m4a"'
                logging.info(f"Running command: {cmd3}")
                os.system(cmd3)
                if (output_path / "audio.m4a").exists():
                    audio_decrypted = True
                data.unlink()
        if not video_decrypted or not audio_decrypted:
            raise FileNotFoundError("Decryption failed: video or audio file not found.")
        cmd4 = f'ffmpeg -i "{output_path}/video.mp4" -i "{output_path}/audio.m4a" -c copy "{output_path}/{output_name}.mp4"'
        logging.info(f"Running command: {cmd4}")
        os.system(cmd4)
        if (output_path / "video.mp4").exists():
            (output_path / "video.mp4").unlink()
        if (output_path / "audio.m4a").exists():
            (output_path / "audio.m4a").unlink()
        filename = output_path / f"{output_name}.mp4"
        if not filename.exists():
            raise FileNotFoundError("Merged video file not found.")
        cmd5 = f'ffmpeg -i "{filename}" 2>&1 | grep "Duration"'
        duration_info = os.popen(cmd5).read()
        logging.info(f"Duration info: {duration_info}")
        return str(filename)
    except Exception as e:
        logging.error(f"Error during decryption and merging: {str(e)}")
        raise

# Run shell command asynchronously
async def run(cmd):
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        logging.info(f'[{cmd!r} exited with {proc.returncode}]')
        if proc.returncode == 1:
            return False
        if stdout:
            return f'[stdout]\n{stdout.decode()}'
        if stderr:
            return f'[stderr]\n{stderr.decode()}'
    except subprocess.SubprocessError as e:
        logging.error(f"Failed to run command {cmd}: {str(e)}")
        return False

# Old download method
def old_download(url, file_name, chunk_size=1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    try:
        r = requests.get(url, allow_redirects=True, stream=True)
        r.raise_for_status()
        with open(file_name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    fd.write(chunk)
        logging.info(f"Downloaded file: {file_name}")
        return file_name
    except requests.RequestException as e:
        logging.error(f"Failed to download from {url}: {str(e)}")
        return None

# Convert size to human-readable format
def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

# Generate unique filename with timestamp
def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date}_{current_time}.mp4"

# Download video with retries
async def download_video(url, cmd, name):
    global failed_counter
    failed_counter = 0
    download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32"'
    logging.info(download_cmd)
    k = subprocess.run(download_cmd, shell=True)
    if "visionias" in cmd and k.returncode != 0 and failed_counter <= 10:
        failed_counter += 1
        logging.warning(f"Download failed, retrying ({failed_counter}/10)...")
        await asyncio.sleep(5)
        return await download_video(url, cmd, name)
    failed_counter = 0
    try:
        if os.path.isfile(name):
            return name
        elif os.path.isfile(f"{name}.webm"):
            return f"{name}.webm"
        name = name.split(".")[0]
        if os.path.isfile(f"{name}.mkv"):
            return f"{name}.mkv"
        elif os.path.isfile(f"{name}.mp4"):
            return f"{name}.mp4"
        elif os.path.isfile(f"{name}.mp4.webm"):
            return f"{name}.mp4.webm"
        logging.error(f"Downloaded video not found: {name}")
        return name
    except FileNotFoundError as exc:
        logging.error(f"File not found: {name}: {str(exc)}")
        return f"{name}.mp4"

# Send document
async def send_doc(bot: Client, m: Message, cc, ka, cc1, prog, count, name):
    try:
        reply = await m.reply_text(
            f"**★彡 ᵘᵖˡᵒᵃᵈⁱⁿᵍ 彡★ ...⏳**\n\n📚𝐓𝐢𝐭𝐥𝐞 » `{name}`\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ ELIESE🐦"
        )
        await asyncio.sleep(1)
        start_time = time.time()
        await bot.send_document(ka, caption=cc1)
        count += 1
        await reply.delete(True)
        os.remove(ka)
        logging.info(f"Uploaded and deleted document: {ka}")
        await asyncio.sleep(3)
        return count
    except Exception as e:
        logging.error(f"Failed to send document {ka}: {str(e)}")
        await m.reply_text(f"Error uploading document: {str(e)}")
        return count

# Decrypt file in-place
def decrypt_file(file_path, key):
    if not os.path.exists(file_path):
        logging.error(f"File not found for decryption: {file_path}")
        return False
    try:
        with open(file_path, "r+b") as f:
            num_bytes = min(28, os.path.getsize(file_path))
            with mmap.mmap(f.fileno(), length=num_bytes, access=mmap.ACCESS_WRITE) as mmapped_file:
                for i in range(num_bytes):
                    mmapped_file[i] ^= ord(key[i]) if i < len(key) else i
        logging.info(f"File decrypted successfully: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to decrypt file {file_path}: {str(e)}")
        return False

# Download and decrypt video
async def download_and_decrypt_video(url, cmd, name, key):
    video_path = await download_video(url, cmd, name)
    if video_path:
        decrypted = decrypt_file(video_path, key)
        if decrypted:
            logging.info(f"File decrypted successfully: {video_path}")
            return video_path
        else:
            logging.error(f"Failed to decrypt {video_path}")
            return None
    logging.error(f"Failed to download video: {name}")
    return None

# Updated send_vid function using ffmpeg-python
async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog):
    try:
        # Create temporary file names
        trimmed_filename = f"trimmed_{filename}"
        thumbnail_filename = f"{filename}.jpg"
        
        # Log input file details
        logging.info(f"Processing video: {filename}")
        if not os.path.exists(filename):
            raise FileNotFoundError(f"Input video file not found: {filename}")
        
        # Get original duration
        original_duration = int(duration(filename))
        logging.info(f"Original video duration: {original_duration} seconds")
        
        # Trim the video starting at 10 seconds with re-encoding
        logging.info(f"Trimming video: {filename} -> {trimmed_filename}")
        result = subprocess.run(
            f'ffmpeg -i "{filename}" -ss 00:00:10 -c:v libx264 -c:a aac -preset fast "{trimmed_filename}"',
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5-minute timeout
        )
        if result.returncode != 0:
            logging.error(f"FFmpeg trimming failed: {result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stderr)
        logging.info(f"Trimmed video created: {trimmed_filename}")
        
        # Verify trimmed file
        if not os.path.exists(trimmed_filename):
            raise FileNotFoundError(f"Trimmed video file not created: {trimmed_filename}")
        trimmed_duration = int(duration(trimmed_filename))
        logging.info(f"Trimmed video duration: {trimmed_duration} seconds")
        if trimmed_duration >= original_duration:
            logging.warning(f"Trimmed duration ({trimmed_duration}s) not less than original ({original_duration}s)")
        
        # Generate thumbnail
        logging.info(f"Generating thumbnail: {trimmed_filename} -> {thumbnail_filename}")
        result = subprocess.run(
            f'ffmpeg -i "{trimmed_filename}" -ss 00:00:00 -vframes 1 "{thumbnail_filename}"',
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logging.error(f"Thumbnail generation failed: {result.stderr}")
            thumbnail_filename = None
            pass  # Reply might not be defined if an early error occurs
