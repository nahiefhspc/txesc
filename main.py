import os
import re
import sys
import base64
import m3u8
import json
import time
import pytz
import asyncio
import requests
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from urllib.parse import urlparse, parse_qs
from logs import logging
from bs4 import BeautifulSoup
import saini as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

OP_COMMAND = os.environ.get("OP_COMMAND", "drm")
NONOP_COMMAND = os.environ.get("NONOP_COMMAND", "stop")

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")
api_url = "http://master-api-v3.vercel.app/"
api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNzkxOTMzNDE5NSIsInRnX3VzZXJuYW1lIjoi4p61IFtvZmZsaW5lXSIsImlhdCI6MTczODY5MjA3N30.SXzZ1MZcvMp5sGESj0hBKSghhxJ3k1GTWoBUbivUe1I"
token_cp = 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9'
adda_token = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJkcGthNTQ3MEBnbWFpbC5jb20iLCJhdWQiOiIxNzg2OTYwNSIsImlhdCI6MTc0NDk0NDQ2NCwiaXNzIjoiYWRkYTI0Ny5jb20iLCJuYW1lIjoiZHBrYSIsImVtYWlsIjoiZHBrYTU0NzBAZ21haWwuY29tIiwicGhvbmUiOiI3MzUyNDA0MTc2IiwidXNlcklkIjoiYWRkYS52MS41NzMyNmRmODVkZDkxZDRiNDkxN2FiZDExN2IwN2ZjOCIsImxvZ2luQXBpVmVyc2lvbiI6MX0.0QOuYFMkCEdVmwMVIPeETa6Kxr70zEslWOIAfC_ylhbku76nDcaBoNVvqN4HivWNwlyT0jkUKjWxZ8AbdorMLg"
photologo = 'https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png'
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png'
photocp = 'https://tinypic.host/images/2025/03/28/IMG_20250328_133126.jpg'
photozip = 'https://envs.sh/cD_.jpg'

async def show_random_emojis(message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻‍❄️', '☁️', '🚹', '🚺', '🐠', '🦋']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message

# Inline keyboard for start command
BUTTONSCONTACT = InlineKeyboardMarkup([[InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot")]])
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot"),
            InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl"),
        ],
    ]
)

# Image URLs for the random image feature
image_urls = [
    "https://tinypic.host/images/2025/02/07/IMG_20250207_224444_975.jpg",
    "https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png",
]




# Define paths for uploaded file and processed file
UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'


m_file_path = "main.py"


@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

async def decrypt_file_txt(file_path):
    # This function needs to be implemented in the helper module
    # Placeholder for now
    return file_path

@bot.on_message(filters.command([OP_COMMAND]))
async def txt_handler(bot: Client, m: Message):
    editable = await m.reply_text(f"`🔹Hi I am Poweful TXT Downloader📥 Bot.\n🔹Send me the txt file and wait.`")
    input: Message = await bot.listen(editable.chat.id)
    y = await input.download()
    file_name, ext = os.path.splitext(os.path.basename(y))

    if file_name.endswith("_helper"):
        x = await decrypt_file_txt(y)
        await input.delete()
    else:
        x = y 

    path = f"./downloads/{m.chat.id}"
    pdf_count = 0
    img_count = 0
    zip_count = 0
    other_count = 0
    
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        
        links = []
        for i in content:
            if "://" in i:
                url = i.split("://", 1)[1]
                links.append([i.split("://", 1)[0], url])
                if ".pdf" in url:
                    pdf_count += 1
                elif url.endswith((".png", ".jpeg", ".jpg")):
                    img_count += 1
                elif ".zip" in url:
                    zip_count += 1
                else:
                    other_count += 1
        os.remove(x)
    except:
        await m.reply_text("<pre><code>🔹Invalid file input.</code></pre>")
        os.remove(x)
        return
    
    await editable.edit(f"`🔹Total 🔗 links found are {len(links)}\n\n🔹Img : {img_count}  🔹PDF : {pdf_count}\n🔹ZIP : {zip_count}  🔹Other : {other_count}\n\n🔹Send From where you want to download.`")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete()
           
    await editable.edit("`🔹Enter Your Batch Name\n🔹Send 1 for use default.`")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete()
    if raw_text0 == '1':
        b_name = file_name.replace('_', ' ')
    else:
        b_name = raw_text0

    await editable.edit("╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`🦋𝗘𝗟𝗜𝗘𝗦𝗘🦋`]⚡⌋━━➣")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    quality = f"{raw_text2}p"
    await input2.delete()
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
        res = "UN"

    default_thumb_url = "https://files.catbox.moe/g02k3k.jpg"
    # Download the fixed thumbnail
    getstatusoutput(f"wget '{default_thumb_url}' -O 'thumb.jpg'")
    thumb = "thumb.jpg"
    await editable.delete()
    await m.reply_text(f"🎯Target Batch : `{b_name}`")

    failed_count = 0
    count = int(raw_text)
    arg = int(raw_text)
    try:
        for i in range(arg-1, len(links)):
            # URL processing
            Vxy = links[i][1].replace("file/d/", "uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")
            # Ensure no double "https://"
            if not Vxy.startswith("https://"):
                url = "https://" + Vxy
            else:
                url = Vxy

            # Title processing
            title = links[i][0]
            # Split title on "💀"
            parts = title.split("💀")
            name1 = parts[0].strip()
            # raw_text65 is the second part if it exists
            raw_text65 = parts[1].strip() if len(parts) > 1 else ""
            # raw_text97 for the format Name💀code65💀🌚720🌚
            raw_text97 = ""
            if len(parts) > 2:
                # Remove both "🌚" from the third part
                raw_text97 = parts[2].replace("🌚", "").strip()
            else:
                # Fallback for non-matching format
                raw_text97 = "default"  # Or set to "" or another fallback value

            cleaned_name1 = name1.replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'[𝗛𝗔𝗖𝗞𝗛𝗘𝗜𝗦𝗧😈]{cleaned_name1[:60]}'
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Referer': 'http://www.visionias.in/',
                        'Sec-Fetch-Dest': 'iframe',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'cross-site',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36',
                        'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"',
                        'sec-ch-ua-mobile': '?1',
                        'sec-ch-ua-platform': '"Android"'
                    }) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif "studystark.site" in url:
                try:
                    # Add headers to mimic a browser request
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
                        "Accept": "application/json",
                    }
                    print(f"Fetching URL: {url}")  # Debugging
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()  # Raises an error for bad status codes
                    data = response.json()
                    video_url = data.get("video_url", "")
                    print(f"Original video_url: {video_url}")  # Debugging
                    if video_url:
                        # Validate that video_url is a valid URL and contains "master.mpd"
                        if "master.mpd" in video_url and video_url.startswith("https://"):
                            if raw_text97:
                                url = video_url.replace("master.mpd", f"hls/{raw_text97}/main.m3u8")
                            else:
                                # Fallback for empty raw_text97
                                url = video_url.replace("master.mpd", "hls/default/main.m3u8")
                        else:
                            # Fallback if video_url is invalid or doesn't contain "master.mpd"
                            print(f"Warning: video_url '{video_url}' is invalid or does not contain 'master.mpd'")
                            url = video_url  # Or set to "" or another fallback
                    else:
                        print("Warning: video_url is empty")
                        url = ""  # Handle empty video_url
                    print(f"Final URL: {url}")  # Debugging
                except requests.RequestException as e:
                    print(f"Error fetching URL {url}: {e}")
                    url = ""  # Fallback to empty string
                except ValueError as e:
                    print(f"Error parsing JSON from {url}: {e}")
                    url = ""  # Fallback to empty string

            elif "encrypted.m" in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

            elif "pwjarvis.com" in url:
                headers = {
                    "authority": "www.pwjarvis.com",
                    "accept": "*/*",
                    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                    "cache-control": "no-cache",
                    "cookie": "cf_clearance=nC4cEcM0X3WsSWu6kQ8feRZZsFlGkO52ZU3_9OgrRE4-1756788206-1.2.1.1-DOgfOPatw5BeN7X0xH7j8H8Xut0vBpIIhhldZ9QvIdvecugdjdvQeTZRlSnH7tOi8f4ML4yeoZGMzjLwrCiUR.h.gGpBVxRS1RNAdZkVDv2nkHU9ev5Qv23iPze2cVl9Gv.4WuGGidMGn3k8gfewbVSIqmdQG6Zlir98RVyfAY9X60wZFff7d1N_PioI.0oc_9W1SRK.9ccuBW4xvUcuIdURhLnueatfHUbyAUYlAWc; PWS=Fe26.2*1*9c270963cdf469805abaf9e5673167358fd36fba6d7a613797cdcaed3ed6d588*5fY55QYgEqSLF0vSS_Oumg*bAx08VnQVZaBbZiKRQnPSMjWANHMCzQOZSM3TnpHd0uwG1syZL0iZOuzWXsiK4NMrPoCXV6KhFgLbh0w11yy8Sg0Zpua6aSdID3l0SxGdx6uGHQA6UAYyvHTboknVcG6psT9yhQnQfVhYjuLC3-t130eI5w4XZnMTscD2409Hv4*1757902047797*2057847dd4c4bee6d06a92a80c589d420a3929ac57cd37fdab8d1c709e31d863*uImyuHN9VAlJvgpgT7mz-4sHmVTgFVLM44bj09JdLyw~2",
                    "next-router-state-tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22study%22%2C%7B%22children%22%3A%5B%22batches%22%2C%7B%22children%22%3A%5B%5B%22batchID%22%2C%22prayas-2023-617434%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22subjects%22%2C%7B%22children%22%3A%5B%5B%22subjectID%22%2C%22physics-785455%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22topics%22%2C%7B%22children%22%3A%5B%5B%22topicID%22%2C%22jee-mains-revision-333137%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22schedule%22%2C%7B%22children%22%3A%5B%5B%22scheduleId%22%2C%22dedeffe13da404f223b84cb90f4ca72c2c1114d30f41da755f1f36abdd38850e%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2Fstudy%2Fbatches%2Fprayas-2023-617434%2Fsubjects%2Fphysics-785455%2Ftopics%2Fjee-mains-revision-333137%2Fschedule%2Fdedeffe13da404f223b84cb90f4ca72c2c1114d30f41da755f1f36abdd38850e%22%2C%22refetch%22%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D",
                    "pragma": "no-cache",
                    "rsc": "1",
                    "sec-ch-ua": '"Chromium";v="137", "Not/A)Brand";v="24"',
                    "sec-ch-ua-arch": "",
                    "sec-ch-ua-bitness": "",
                    "sec-ch-ua-full-version": "137.0.7337.0",
                    "sec-ch-ua-full-version-list": '"Chromium";v="137.0.7337.0", "Not/A)Brand";v="24.0.0.0"',
                    "sec-ch-ua-mobile": "?1",
                    "sec-ch-ua-model": "211033MI",
                    "sec-ch-ua-platform": "Android",
                    "sec-ch-ua-platform-version": "11.0.0",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
                }
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    match = re.search(r'https://cors\.pwjarvis\.com/[\w\-._~:/?#[\]@!$&\'()*+,;=%]+/master\.mpd', response.text)
                    if match:
                        original_link = match.group()
                        transformed_link = original_link.replace("https://cors.pwjarvis.com", "https://stream.pwjarvis.com")
                        transformed_link = transformed_link.replace("/master.mpd", "/hls/{raw_text97}/main.m3u8")
                        url = transformed_link
                    else:
                        raise Exception("Video link not found in the response")
                else:
                    raise Exception(f"Failed to fetch the page, status code: {response.status_code}")

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
                cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies {cookies_file_path} -f "{ytf}" "{url}" -o "{name}.mp4"'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
            try:
                cc = f'**|🇮🇳| {cleaned_name1}\n\n😎 ℚ𝕦𝕒𝕝𝕚𝕥𝕪 ➠ {raw_text97}p\n\n🧿 𝐁𝐀𝐓𝐂𝐇 ➤ {b_name}\n\nChapterId > {raw_text65}**'
                cc1 = f'**|🇮🇳| {cleaned_name1}\n\n🧿 𝐁𝐀𝐓𝐂𝐇 ➤ {b_name}\n\nChapterId > {raw_text65}**'
                cczip = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**📁 Title :** `{name1}`\n**├── Extention :**  .zip\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** '
                ccimg = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**🖼️ Title :** `{name1}`\n**├── Extention :**   .jpg\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :**'
                ccm = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**🎵 Title :** `{name1}`\n**├── Extention :**  .mp3\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :**'
                cchtml = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**🌐 Title :** `{name1}`\n**├── Extention :** .html\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :**'

                if "drive" in url:
                    ka = await helper.download(url, name)
                    copy = await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc1)
                    count += 1
                    os.remove(ka)
                    time.sleep(1)
                    continue

                elif ".pdf*" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count += 1
                        continue    

                elif ".pdf" in url and ".pdf*" not in url:
                    try:
                        await asyncio.sleep(4)
                        url = url.replace(" ", "%20")
                        scraper = cloudscraper.create_scraper()
                        response = scraper.get(url)
                        if response.status_code == 200:
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)
                            await asyncio.sleep(4)
                            copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        else:
                            await m.reply_text(f"Failed to download PDF: {response.status_code} {response.reason}")
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        count += 1
                        continue              

                elif ".ws" in url and url.endswith(".ws"):
                    await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}", f"{name}.html")
                    time.sleep(1)
                    await bot.send_document(chat_id=m.chat.id, document=f"{name}.html", caption=cchtml)
                    os.remove(f'{name}.html')
                    count += 1
                    time.sleep(5)
                    continue
                            
                elif ".zip" in url:
                    BUTTONSZIP = InlineKeyboardMarkup([[InlineKeyboardButton(text="🎥 ZIP STREAM IN PLAYER", url=f"{url}")]])
                    await bot.send_photo(chat_id=m.chat.id, photo=photozip, caption=cczip, reply_markup=BUTTONSZIP)
                    count += 1
                    time.sleep(1)    
                    continue

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    ext = url.split('.')[-1]
                    cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.{ext}', caption=ccimg)
                    count += 1
                    os.remove(f'{name}.{ext}')
                    time.sleep(1)
                    continue

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    ext = url.split('.')[-1]
                    cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.{ext}', caption=ccm)
                    count += 1
                    os.remove(f'{name}.{ext}')
                    time.sleep(1)
                    continue
                                    

                elif 'drmcdni' in url or 'drm/wv' in url:
                    remaining_links = len(links) - count
                    progress = (count / len(links)) * 100
                    emoji_message = await show_random_emojis(m)
                    Show = f"🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%\n┃\n" \
                           f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                           f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 𝐋𝐢𝐧𝐤𝐬 » {remaining_links}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Dʀᴍ Sᴛᴀʀᴛᴇᴅ...⏳**\n┃\n" \
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 »\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐚𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"📚�	T𝐢𝐭𝐥𝐞 » {name}\n┃\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**\n┃\n" \
                           f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [ELIESE🐦](https://t.me/+MdZ2996M2G43MWFl)"                    
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    await emoji_message.delete()
                    await prog.delete()
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    await asyncio.sleep(1)
                    continue

                else:
                    remaining_links = len(links) - count
                    progress = (count / len(links)) * 100
                    emoji_message = await show_random_emojis(m)
                    Show = f"🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%\n┃\n" \
                           f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                           f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 𝐋𝐢𝐧𝐤𝐬 » {remaining_links}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n┃\n" \
                           f"╰━📚𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"📚�	T𝐢𝐭𝐥𝐞 » {name}\n┃\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**"                    
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await emoji_message.delete()
                    await prog.delete()
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)
                    continue
                
            except Exception as e:
                await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**ID** =>> `{str(count).zfill(3)}`\n\n**Name** - `{name1}`**', disable_web_page_preview=True)
                count += 1
                failed_count += 1
                continue

    except Exception as e:
        await m.reply_text(str(e))
        time.sleep(2)

    await m.reply_text(f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
    await m.reply_text(f"⋅ ─ list index ({raw_text}-{len(links)}) out of range ─ ⋅\n\n✨ **BATCH** » {b_name}✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")
             
bot.run()
