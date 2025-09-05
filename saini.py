import os
import asyncio
import subprocess
import time
import random
import logging
from pyrogram import Client
from pyrogram.types import Message
from subprocess import getstatusoutput
import yt_dlp
import requests
import cloudscraper

# Configure logging
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

studystark_cookies_path = os.getenv("studystark_cookies_path", "studystark_cookies.txt")

async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality):
    """
    Download, decrypt, and merge a DRM-protected video using yt-dlp, mp4decrypt, and ffmpeg.
    """
    try:
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Minimal yt-dlp options to mimic 1DM's behavior
        ydl_opts = {
            'format': f'bv[height<={quality}]+ba/b',
            'outtmpl': f'{output_path}/file.%(ext)s',
            'allow_unplayable_formats': True,
            'nocheckcertificate': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36'
            },
            'cookiefile': studystark_cookies_path,  # Optional, in case cookies are needed
            'retries': 5,
            'fragment_retries': 5,
            'retry_sleep': lambda n: 2 ** n * random.uniform(0.8, 1.2),
            'verbose': True  # Enable verbose logging for debugging
        }

        logging.info(f"Starting yt-dlp download for {mpd_url} with options: {ydl_opts}")
        # Add delay to avoid rate limiting
        await asyncio.sleep(2)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([mpd_url])

        video_file = f"{output_path}/file.mp4"
        audio_file = f"{output_path}/file.m4a"
        decrypted_video = f"{output_path}/video.mp4"
        decrypted_audio = f"{output_path}/audio.mp4"
        output_file = f"{output_path}/{output_name}.mp4"

        # Decrypt video if it exists
        if os.path.exists(video_file):
            cmd = f'mp4decrypt {keys_string} --show-progress "{video_file}" "{decrypted_video}"'
            logging.info(f"Decrypting video: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
        else:
            logging.error(f"Video file not found: {video_file}")
            raise Exception(f"Video file not downloaded: {video_file}")

        # Decrypt audio if it exists
        if os.path.exists(audio_file):
            cmd = f'mp4decrypt {keys_string} --show-progress "{audio_file}" "{decrypted_audio}"'
            logging.info(f"Decrypting audio: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
        else:
            logging.warning(f"Audio file not found: {audio_file}, proceeding with video only")

        # Merge video and audio, or use video only if audio is missing
        if os.path.exists(decrypted_video):
            if os.path.exists(decrypted_audio):
                cmd = f'ffmpeg -i "{decrypted_video}" -i "{decrypted_audio}" -c:v copy -c:a copy "{output_file}"'
                logging.info(f"Merging video and audio: {cmd}")
                subprocess.run(cmd, shell=True, check=True)
            else:
                cmd = f'ffmpeg -i "{decrypted_video}" -c:v copy "{output_file}"'
                logging.info(f"Copying video only: {cmd}")
                subprocess.run(cmd, shell=True, check=True)
        else:
            raise Exception("Decrypted video file not created")

        # Clean up intermediate files
        for file in [video_file, audio_file, decrypted_video, decrypted_audio]:
            if os.path.exists(file):
                os.remove(file)

        if os.path.exists(output_file):
            logging.info(f"Output file created: {output_file}")
            return output_file
        else:
            raise Exception("Failed to create output file")

    except Exception as e:
        logging.error(f"Error in decrypt_and_merge_video: {e}")
        raise

async def download(url, name):
    """
    Download a file (e.g., from Google Drive) using cloudscraper.
    """
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if response.status_code == 200:
            output_file = f"{name}.pdf"  # Assuming PDF for Drive links
            with open(output_file, 'wb') as file:
                file.write(response.content)
            logging.info(f"Downloaded file: {output_file}")
            return output_file
        else:
            logging.error(f"Failed to download {url}: {response.status_code} {response.reason}")
            return None
    except Exception as e:
        logging.error(f"Error in download: {e}")
        return None

async def pdf_download(url, output_name):
    """
    Download a PDF from a specific API endpoint.
    """
    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url)
        if response.status_code == 200:
            with open(output_name, 'wb') as file:
                file.write(response.content)
            logging.info(f"Downloaded PDF: {output_name}")
            return output_name
        else:
            logging.error(f"Failed to download PDF from {url}: {response.status_code} {response.reason}")
            return None
    except Exception as e:
        logging.error(f"Error in pdf_download: {e}")
        return None

async def download_video(url, cmd, name):
    """
    Download a non-DRM video using yt-dlp.
    """
    try:
        output_file = f"{name}.mp4"
        logging.info(f"Executing command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
        if os.path.exists(output_file):
            logging.info(f"Downloaded video: {output_file}")
            return output_file
        else:
            raise Exception("Failed to download video")
    except Exception as e:
        logging.error(f"Error in download_video: {e}")
        raise

async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog):
    """
    Send the video to Telegram with a thumbnail and caption.
    """
    try:
        # Get video duration
        duration = 0
        cmd = f'ffmpeg -i "{filename}" 2>&1 | grep Duration | awk "{{print $2}}" | tr -d ,'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        if output:
            h, m, s = output.split(':')
            duration = int(h) * 3600 + int(m) * 60 + float(s)

        # Generate thumbnail if not provided
        thumb_path = thumb if os.path.exists(thumb) else f"{name}_thumb.jpg"
        if not os.path.exists(thumb_path):
            cmd = f'ffmpeg -i "{filename}" -ss 00:00:10 -vframes 1 -vf "scale=320:240" "{thumb_path}"'
            logging.info(f"Generating thumbnail: {cmd}")
            subprocess.run(cmd, shell=True, check=True)

        # Send video
        await bot.send_video(
            chat_id=m.chat.id,
            video=filename,
            caption=cc,
            thumb=thumb_path,
            duration=int(duration),
            supports_streaming=True
        )

        # Clean up
        for file in [filename, thumb_path]:
            if os.path.exists(file):
                os.remove(file)

        logging.info(f"Video sent successfully: {filename}")
    except Exception as e:
        logging.error(f"Error in send_vid: {e}")
        raise
