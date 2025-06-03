import subprocess
import os
import logging
from pyrogram import Client
from pyrogram.types import Message

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Assuming human_readable_size and duration are defined elsewhere
def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

def duration(filename):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        return float(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.error(f"Failed to get duration for {filename}: {str(e)}")
        return 0

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
        else:
            logging.info(f"Thumbnail created: {thumbnail_filename}")
        
        # Delete progress message
        await prog.delete(True)
        reply = await m.reply_text(
            f"**★彡 ᵘᵖˡᵒᵃᵈⁱⁿᵍ 彡★ ...⏳**\n\n📚𝐓𝐢𝐭𝐥𝐞 » `{name}`\n\n✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ ELIESE🦁"
        )
        
        # Set thumbnail
        if thumb == "/d":
            thumbnail = thumbnail_filename if os.path.exists(thumbnail_filename) else None
        else:
            thumbnail = thumb
        
        # Check file size (Telegram limit: 2GB)
        file_size = os.path.getsize(trimmed_filename)
        if file_size > 2 * 1024 * 1024 * 1024:  # 2GB
            raise ValueError(f"Trimmed video exceeds Telegram's 2GB limit: {human_readable_size(file_size)}")
        
        start_time = time.time()
        
        # Upload video
        try:
            await m.reply_video(
                trimmed_filename,
                caption=cc,
                supports_streaming=True,
                height=720,
                width=1280,
                thumb=thumbnail,
                duration=trimmed_duration,
                progress=progress_bar,
                progress_args=(reply, start_time)
            )
            logging.info(f"Uploaded video: {trimmed_filename}")
        except Exception as e:
            logging.warning(f"Video upload failed, trying document: {str(e)}")
            await m.reply_document(
                trimmed_filename,
                caption=cc,
                progress=progress_bar,
                progress_args=(reply, start_time)
            )
            logging.info(f"Uploaded document: {trimmed_filename}")
    except FileNotFoundError as e:
        logging.error(f"File error: {str(e)}")
        await m.reply_text(f"Error: {str(e)}")
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg processing failed: {e.stderr}")
        await m.reply_text(f"Error processing video: FFmpeg failed - {e.stderr}")
    except Exception as e:
        logging.error(f"Error in send_vid: {str(e)}")
        await m.reply_text(f"Error uploading video: {str(e)}")
    finally:
        # Clean up files (keep original for debugging)
        for file in [trimmed_filename, thumbnail_filename]:
            if file and os.path.exists(file):
                try:
                    os.remove(file)
                    logging.info(f"Deleted file: {file}")
                except OSError as e:
                    logging.error(f"Failed to delete file {file}: {str(e)}")
        try:
            await reply.delete(True)
        except NameError:
            pass  # Reply might not be defined if an early error occurs
