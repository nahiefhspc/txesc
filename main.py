import os
import re
import sys
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

@bot.on_message(filters.command("cookies") & filters.private)
async def cookies_handler(client: Client, m: Message):
    await m.reply_text(
        "Please upload the cookies file (.txt format).",
        quote=True
    )

    try:
        # Wait for the user to send the cookies file
        input_message: Message = await client.listen(m.chat.id)

        # Validate the uploaded file
        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        # Download the cookies file
        downloaded_path = await input_message.download()

        # Read the content of the uploaded file
        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        # Replace the content of the target cookies file
        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )

    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    # Inform the user to send the text data and its desired file name
    editable = await message.reply_text(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(message.chat.id)
    if not input_message.text:
        await message.reply_text("🚨 **error**: Send valid text data")
        return

    text_data = input_message.text.strip()
    await input_message.delete()
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id)
    raw_textn = inputn.text
    await inputn.delete()
    await editable.delete()

    if raw_textn == '/d':
        custom_file_name = 'txt_file'
    else:
        custom_file_name = raw_textn

    txt_file = os.path.join("downloads", f'{custom_file_name}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write(text_data)
        
    await message.reply_document(document=txt_file, caption=f"`{custom_file_name}.txt`\n\nYou can now download your content! 📥")
    os.remove(txt_file)

# Define paths for uploaded file and processed file
UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

@bot.on_message(filters.command(["y2t"]))
async def youtube_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    
    editable = await message.reply_text(
        f"Send YouTube Website/Playlist link for convert in .txt file"
    )

    input_message: Message = await bot.listen(message.chat.id)
    youtube_link = input_message.text.strip()
    await input_message.delete()
    await editable.delete()

    # Fetch the YouTube information using yt-dlp with cookies
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'force_generic_extractor': True,
        'forcejson': True,
        'cookies': cookies_file_path
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(youtube_link, download=False)
            if 'entries' in result:
                title = result.get('title', 'youtube_playlist')
            else:
                title = result.get('title', 'youtube_video')
        except yt_dlp.utils.DownloadError as e:
            await message.reply_text(
                f"<pre><code>🚨 Error occurred {str(e)}</code></pre>"
            )
            return

    # Extract the YouTube links
    videos = []
    if 'entries' in result:
        for entry in result['entries']:
            video_title = entry.get('title', 'No title')
            url = entry.get('url', '')
            videos.append(f"{video_title}: {url}")
    else:
        video_title = result.get('title', 'No title')
        url = result.get('url', '')
        videos.append(f"{video_title}: {url}")

    # Create and save the .txt file with the custom name
    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    # Send the generated text file to the user with a pretty caption
    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<pre><code>{title}.txt</code></pre>\n'
    )

    # Remove the temporary text file after sending
    os.remove(txt_file)

m_file_path = "main.py"

@bot.on_message(filters.command("mfile") & filters.private)
async def getmfile_handler(client: Client, m: Message):
    try:
        await client.send_document(
            chat_id=m.chat.id,
            document=m_file_path,
            caption="Here is the `main.py` file."
        )
    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")

@bot.on_message(filters.command(["stop"]))
async def restart_handler(_, m: Message):
    await m.reply_text("**ˢᵗᵒᵖᵖᵉᵈ ᵇᵃᵇʸ**", True)
    os.execl(sys.executable, sys.executable, *sys.argv)
        
@bot.on_message(filters.command(["start"]))
async def start_command(bot: Client, message: Message):
    random_image_url = random.choice(image_urls)
    caption = (
        "𝐇𝐞𝐥𝐥𝐨 𝐃𝐞𝐚𝐫 👋!\n\n➠ 𝐈 𝐚𝐦 𝐚 𝐓𝐞𝐱𝐭 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐫 𝐁𝐨𝐭\n\n➠ Can Extract Videos & PDFs From Your Text File and Upload to Telegram!\n\n➠ For Guide Use Command /help 📖\n\n➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : 𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎 🦁"
    )
    await bot.send_photo(
        chat_id=message.chat.id,
        photo=random_image_url,
        caption=caption,
        reply_markup=keyboard
    )

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    chat_id = message.chat.id
    await message.reply_text(f"<blockquote>The ID of this chat id is:</blockquote>\n`{chat_id}`")

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    text = (
        f"╭────────────────╮\n"
        f"│✨ **__Your Telegram Info__**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}`\n"
        f"├🔹**User ID :** @{update.from_user.username if update.from_user.username else 'None'}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    
    await update.reply_text(        
        text=text,
        disable_web_page_preview=True,
        reply_markup=BUTTONSCONTACT
    )

@bot.on_message(filters.command(["help"]))
async def txt_handler(client: Client, m: Message):
    await bot.send_message(m.chat.id, text=(
        f"🎉Congrats! You are using 𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎:\n\n"
        f"✦**Available Commands Here**✦\n\n"
        f"┣⪼01. /start - To Alive Check Bot \n"
        f"┣⪼02. /drm - for extract txt file\n"
        f"┣⪼03. /y2t - YouTube to .txt Convert\n"
        f"┣⪼04. /t2t - text to .txt Convert\n"
        f"┣⪼05. /logs - To see Bot Working Logs\n"
        f"┣⪼06. /cookies - To update YT cookies.\n"
        f"┣⪼07. /id - Know chat/group/channel ID.\n"
        f"┣⪼08. /info - Your information.\n"
        f"┣⪼09. /stop - Stop the Running Task. 🚫\n"
        f"╰⪼🔗  Direct Send Link For Extract (with https://)\n\n"
        f"**If you have any questions, feel free to ask [𝙎𝘼𝙄𝙉𝙄 𝘽𝙊𝙏𝙎🐦](https://t.me/+MdZ2996M2G43MWFl)! 💬**\n"
    ))

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

@bot.on_message(filters.command(["drm"]))
async def txt_handler(bot: Client, m: Message):
    editable = await m.reply_text(f"`🔹Hi I am Poweful TXT Downloader📥 Bot.\n🔹Send me the txt file and wait.`")
    input: Message = await bot.listen(editable.chat.id)
    y = await input.download()
    await input.delete()
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

    await editable.edit("`🔹Enter Your Name\n🔹Send 1 for use default`")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete()
    if raw_text3 == '1':
        CR = '[𝄟⃝‌🐬🇳‌ɪᴋʜɪʟ𝄟⃝🐬](https://t.me/+MdZ2996M2G43MWFl)'
    else:
        CR = raw_text3

    await editable.edit("🔹Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋\n🔹Send /d for use default")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete()

    await editable.edit(f"🔹Send the Video Thumb URL\n🔹Send /d for use default\n\n🔹You can direct upload thumb\n🔹Send **No** for use default")
    input6: Message = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete()

    if input6.photo:
        thumb = await input6.download()
    elif raw_text6.startswith(("http://", "https://")):
        getstatusoutput(f"wget '{raw_text6}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    elif raw_text6.lower() == "no" or raw_text6 == "/d":
        thumb = photoyt
    else:
        thumb = raw_text6
    await editable.delete()
    await m.reply_text(f"🎯Target Batch : `{b_name}`")

    failed_count = 0
    count = int(raw_text)
    arg = int(raw_text)
    try:
        for i in range(arg-1, len(links)):
            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            link0 = "https://" + Vxy

            name1 = links[i][0].replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'[𝗛𝗔𝗖𝗞𝗛𝗘𝗜𝗦𝗧😈]{name1[:60]}'
            
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

            elif "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'

            elif "https://cpvod.testbook.com/" in url:
                url = url.replace("https://cpvod.testbook.com/","https://media-cdn.classplusapp.com/drm/")
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = await helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "classplusapp.com/drm/" in url:
                url = 'https://dragoapi.vercel.app/classplus?link=' + url
                mpd, keys = await helper.get_mps_and_keys(url)
                url = mpd
                keys_string = " ".join([f"--key {key}" for key in keys])

            elif "tencdn.classplusapp" in url:
                headers = {
                    'Host': 'api.classplusapp.com',
                    'x-access-token': f'{token_cp}',
                    'user-agent': 'Mobile-Android',
                    'app-version': '1.4.37.1',
                    'api-version': '18',
                    'device-id': '5d0d17ac8b3c9f51',
                    'device-details': '2848b866799971ca_2848b8667a33216c_SDK-30',
                    'accept-encoding': 'gzip'
                }
                params = (('url', f'{url}'))
                response = requests.get('https://api.classplusapp.com/cams/uploader/video/jw-signed-url', headers=headers, params=params)
                url = response.json()['url']  

            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': f'{token_cp}'}).json()['url']
            
            elif 'media-cdn.classplusapp.com' in url or 'media-cdn-alisg.classplusapp.com' in url or 'media-cdn-a.classplusapp.com' in url: 
                headers = {'x-access-token': f'{token_cp}', "X-CDN-Tag": "empty"}
                response = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                url = response.json()['url']

            elif "rarestudy22" in url:
                # Inline retry function
                def fetch_with_retries(local_url, headers=None, max_retries=3):
                    for attempt in range(max_retries):
                        try:
                            response = requests.get(local_url, headers=headers, timeout=10)
                            response.raise_for_status()
                            return response
                        except requests.RequestException as e:
                            print(f"[Retry {attempt+1}] Error fetching {local_url}: {e}")
                            if attempt < max_retries - 1:
                                time.sleep(2)
                    return None

                # Step 1: Transform URL
                transformed_url = url.replace("/media/", "/video-data?encoded=")

                # Step 2: Headers
                headers = {
                    'authority': 'rarestudy22-e3c80f6989c8.herokuapp.com',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    'cookie': 'cf_clearance=cf_clearance=g3z7irdDD_BHTi3MpE6UR1ay4eiXTVG5RkRAMVhKILY-1751948668-1.2.1.1-N72U8xIccTHnfRiJKnZ.6.7mFmGEyNtSKCGzExb012j7Stkj.tPSBic648hLtwqgM.lAlXy0u_JWeAoqL4C3smrGgLTPwHlhVNuf0kxOC5QYDhjj.elN4ZjSoh8doZN1V6BWcl3_eALAXHwzZUwP4Gp9J.fpDzuFCAIonMfPPtVMt4Ib7SiRLoEVsAmP7s6R1XueOqPqYCa9nVygHZBa3MRUsBcwC8SdOEfwy9TiFZE; session=.eJxlkktz4kgQhP8L59mJqu6ufsyN5WWxixTYMgJdHCCwEQhMYDBGG_vfN3siZi4bcOnuqsovs_RP5-W0OR-Wx83x0vlxOV833zqv9fFtcz6d6-Pl5fK-3xw7PzrsRchqImWMYxFPzI4845JdMKJEWWZlhYJo75U2lozTgQPh77R2lrQOwYnV8cTimbXBFAnOkFFWKeOVN0pb69kTOUXiNDkxPngDDVKkgohzgTVJUHhnx95CLxhPHtOtC0LOWYseh2LCtRgdwIn50FUqKIy3ULLWWS9OwOQUUMRZbRSOcBl8tKSc1yJWhIPC2bHygcDKilhjFhtmGDJshAAKIksON0opATA7FZmUdkEzzAYKBrUARRYG1GBxRmM4EjUWQibANmlUMbL2DoFoVEcjAU0OPBYUTKSRimOQehNzdAazDMWgA3qF0C4W-XtsxCDKYEk0hmJlzlG0o60JXtCEsdGDh4jRQmyCxs-hA3oehiz8w1aAoCaLjSEA7FxH6CjrPPxIYMuWFHLFp-FB4bEgyNkQ4E2Fn9vGR6S08t4jFoXNOBstolMDRQNQpPOt8-ub29zHtJl366we_zXjaf13b7xdjap4Tp7bhNN6HL6jqNk8oGg30Gk-NZO2e0_7z9fJbs9o2C_mj9tkd3JJE05lL7HJbqHL_uC-aAdt1m8OZf9xX-7-3JaHCZfFsMmeko_kOGvL-fi6KLhJdu91lg8k63dN2q9uk_h-KE_VMaX8MLyUT5i5H8p6nr4n9a1ejYbteiDbVfEcQafQb1a92BPupRpel_PTdj1qPld1YsH-uiymqEugnbRZnjZlvufyMKzTdqqy0UBnxfQr6--jeV0W43aJeZGpGm2lUs2u0muE8rVd9mS3UhTrfnM__69mHPDerIrhaRWzOJanxWEo1WhIZXHjtH0zWb7tloq3y-J2XahwiZ6qQ_go55M6az7qtEjuqRrvs3zBWX96L5HzBJxpu92lh9khaQhe0891IVQdmwf0chW19k0WZ60fmtvPzJpZ_jhL6tenW70shgTer7R9pskOi-1P-XX6vZ2baryYkuT33vjprF5SM--PzmXylvcSGV2um-6nPBz_uKaTzr__Ab-HS_k.aJAfrA.0E6XZoJJY8XVrMc2xhanrHjcqRg',
                    'pragma': 'no-cache',
                    'referer': 'https://rarestudy22-e3c80f6989c8.herokuapp.com/batches',
                    'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                    'sec-ch-ua-arch': '""',
                    'sec-ch-ua-bitness': '""',
                    'sec-ch-ua-full-version': '"137.0.7337.0"',
                    'sec-ch-ua-full-version-list': '"Chromium";v="137.0.7337.0", "Not/A)Brand";v="24.0.0.0"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-model': '"211033MI"',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-ch-ua-platform-version': '"11.0.0"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36'
                }

                # Step 3: Fetch video metadata with retries
                video_response = fetch_with_retries(transformed_url, headers)
                if video_response:
                    try:
                        video_data = video_response.json()
                        video_url = video_data.get("data", {}).get("url", "")
                    except json.JSONDecodeError:
                        print("❌ Invalid JSON in video metadata.")
                        video_url = ""
                else:
                    video_url = ""

                if video_url:
                    # Step 4: Replace domain
                    transformed_video_url = video_url.replace(
                        "https://sec-prod-mediacdn.pw.live",
                        "https://anonymouspwplayerr-f996115ea61a.herokuapp.com/sec-prod-mediacdn.pw.live"
                    )

                    # Step 5: Get token with retry
                    token_response = fetch_with_retries("https://api-accesstoken.vercel.app", headers={"Content-Type": "application/json"})
                    if token_response:
                        try:
                            token_data = token_response.json()
                            access_token = token_data.get("access_token", "")
                        except json.JSONDecodeError:
                            print("❌ Invalid JSON in token API response.")
                            access_token = ""
                    else:
                        access_token = ""

                    # Step 6: Build final HLS URL
                    if access_token:
                        hls_url = transformed_video_url.replace("master.mpd", "hls/720/main.m3u8")
                        url = f"{hls_url}&token={access_token}"
                    else:
                        print("❌ Access token missing, skipping transformation.")
                else:
                    print("❌ Video URL missing, skipping transformation.")

            elif url.startswith("https://streamfiles.eu.org/play.php"):
                max_retries = 10
                retry_delay = 2
                real_url = None
                try:
                    parsed_url = urllib.parse.urlparse(url)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    video_url = query_params.get('video_url', [''])[0]
                    video_title = urllib.parse.unquote(query_params.get('title', ['Unknown Title'])[0])
                    video_poster = query_params.get('poster', [''])[0]
                    video_id = query_params.get('video_id', [''])[0]
                    subject_id = query_params.get('subject_id', [''])[0]
                    batch_id = query_params.get('batch_id', [''])[0]

                    try:
                        decoded_url = base64.b64decode(video_url).decode('utf-8')
                        print(f"Decoded video_url for {video_title}: {decoded_url}")
                    except Exception as e:
                        print(f"Failed to decode video_url for {video_title}: {e}")
                        decoded_url = None

                    play_url = (
                        f"https://streamfiles.eu.org/play.php"
                        f"?video_url={urllib.parse.quote(video_url)}"
                        f"&title={urllib.parse.quote(video_title)}"
                        f"&poster={video_poster}"
                        f"&video_type=pw"
                        f"&video_id={video_id}"
                        f"&subject_id={subject_id}"
                        f"&batch_id={batch_id}"
                    )

                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Accept": "application/json"
                    }
                    cookies = {
                        "_clck": "1hjjwnc|2|fw3|0|1967",
                        "verified_task": "dHJ1ZQ==",
                        "countdown_end_time": "MTc0ODc0OTI5NTc3Ng==",
                        "auth_token": f"{raw_text4}"
                    }

                    async with aiohttp.ClientSession() as session:
                        for attempt in range(max_retries):
                            try:
                                async with session.get(play_url, headers=headers, cookies=cookies) as response:
                                    if response.status == 200:
                                        soup = BeautifulSoup(await response.text(), 'html.parser')
                                        input_group = soup.find('div', class_='input-group')
                                        if input_group:
                                            extracted = input_group.find('input', {'id': 'video_url'})
                                            if extracted and extracted['value']:
                                                real_url = extracted['value']
                                                print(f"Successfully extracted real_url for {video_title}: {real_url}")
                                                break
                                            print(f"No video URL found in input tag for {video_title}")
                                        else:
                                            print(f"No input-group div found in play page for {video_title}")
                                    else:
                                        print(f"Attempt {attempt + 1} failed for {play_url}: Status {response.status}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(retry_delay)
                            except aiohttp.ClientError as e:
                                print(f"Attempt {attempt + 1} failed: {e}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(retry_delay)
                            except Exception as e:
                                print(f"Unexpected error on attempt {attempt + 1}: {e}")
                                if attempt < max_retries - 1:
                                    await asyncio.sleep(retry_delay)
                        else:
                            print(f"Failed to extract real_url for {video_title} after {max_retries} retries")
                            real_url = decoded_url if decoded_url else None
                except Exception as e:
                    print(f"Error processing streamfiles URL {url}: {e}")
                    real_url = decoded_url if decoded_url else None

                if real_url:
                    max_retries = 3
                    retry_delay = 2
                    for attempt in range(max_retries):
                        try:
                            base_path = real_url.split('?')[0].replace('master.mpd', '')
                            query_params = real_url.split('?')[1] if '?' in real_url else ''
                            new_url = f"{base_path}hls/720/main.m3u8" + (f"?{query_params}" if query_params else '')
                            new_url = new_url.replace(
                                "https://sec-prod-mediacdn.pw.live",
                                "https://anonymouspwplayerr-f996115ea61a.herokuapp.com/sec-prod-mediacdn.pw.live"
                            )
                            api_url = "https://api-accesstoken.vercel.app"
                            headers = {"Content-Type": "application/json"}
                            async with aiohttp.ClientSession() as session:
                                async with session.get(api_url, headers=headers) as response:
                                    if response.status == 200:
                                        response_data = await response.json()
                                        if 'access_token' in response_data:
                                            url = f"{new_url}&token={response_data['access_token']}"
                                            print(f"Generated new_url with token: {url}")
                                            break
                                        else:
                                            url = f"{new_url}"
                                            print(f"No access_token in API response, using: {url}")
                                            break
                                    else:
                                        print(f"API request failed, status: {response.status}")
                                        if attempt < max_retries - 1:
                                            await asyncio.sleep(retry_delay)
                                        continue
                        except aiohttp.ClientError as e:
                            print(f"Attempt {attempt + 1} failed: {e}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                            continue
                        except Exception as e:
                            print(f"Unexpected error on attempt {attempt + 1}: {e}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(retry_delay)
                            continue
                    else:
                        url = f"{new_url}"

            elif url.startswith("https://rarestudy.site/media"):
                async def fetch_url(session: ClientSession, url: str, retries: int = 30, delay: float = 2.0) -> str:
                    for attempt in range(1, retries + 1):
                        try:
                            async with session.get(url, timeout=10) as response:
                                if response.status >= 500:
                                    raise aiohttp.ClientError(f"Server error: {response.status}")
                                response.raise_for_status()
                                return await response.text()
                        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                            if attempt == retries:
                                raise Exception(f"Failed after {retries} attempts: {e}")
                            print(f"Attempt {attempt} failed: {e}. Retrying in {delay * attempt} seconds...")
                            await asyncio.sleep(delay * attempt)

                try:
                    async with aiohttp.ClientSession() as session:
                        script_content = await fetch_url(session, url)
                        match = re.search(r'const videoData = (\{.*?\});', script_content, re.DOTALL)
                        if match:
                            video_data_str = match.group(1)
                            video_data = json.loads(video_data_str)
                            real_url = video_data.get('url', '')
                            if not real_url:
                                print("No URL found in videoData")
                                real_url = None
                        else:
                            print("videoData object not found in response")
                            real_url = None
                        if real_url:
                            max_retries = 30
                            retry_delay = 2
                            for attempt in range(max_retries):
                                try:
                                    base_path = real_url.split('?')[0].replace('master.mpd', '')
                                    query_params = real_url.split('?')[1] if '?' in real_url else ''
                                    new_url = f"{base_path}hls/720/main.m3u8" + (f"?{query_params}" if query_params else '')
                                    new_url = new_url.replace(
                                        "https://sec-prod-mediacdn.pw.live",
                                        "https://anonymousrajputplayer-9ab2f2730a02.herokuapp.com/sec-prod-mediacdn.pw.live"
                                    )
                                    api_url = "https://api-accesstoken.vercel.app"
                                    headers = {"Content-Type": "application/json"}
                                    async with session.get(api_url, headers=headers) as response:
                                        if response.status == 200:
                                            response_data = await response.json()
                                            if 'access_token' in response_data:
                                                url = f"{new_url}&token={response_data['access_token']}"
                                                print(f"Generated new_url with token: {url}")
                                                break
                                            else:
                                                url = f"{new_url}"
                                                print(f"No access_token in API response, using: {url}")
                                                break
                                        else:
                                            print(f"API request failed, status: {response.status}")
                                            if attempt < max_retries - 1:
                                                await asyncio.sleep(retry_delay)
                                            continue
                                except aiohttp.ClientError as e:
                                    print(f"Attempt {attempt + 1} failed: {e}")
                                    if attempt < max_retries - 1:
                                        await asyncio.sleep(retry_delay)
                                    continue
                                except Exception as e:
                                    print(f"Unexpected error on attempt {attempt + 1}: {e}")
                                    if attempt < max_retries - 1:
                                        await asyncio.sleep(retry_delay)
                                    continue
                            else:
                                url = f"{new_url}"
                except Exception as e:
                    print(f"Error processing rarestudy URL {url}: {e}")
                    real_url = None

            elif "encrypted.m" in url:
                appxkey = url.split('*')[1]
                url = url.split('*')[0]

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
                cc = f'**|🇮🇳| {name1}.mkv\n\n🧿 𝐁𝐀𝐓𝐂𝐇 ➤ {b_name}**'
                cc1 = f'**|🇮🇳| {name1}.pdf\n\n🧿 𝐁𝐀𝐓𝐂𝐇 ➤ {b_name}**'
                cczip = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**📁 Title :** `{name1}`\n**├── Extention :**  {CR} .zip\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'
                ccimg = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🖼️ Title :** `{name1}`\n**├── Extention :**  {CR} .jpg\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'
                ccm = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🎵 Title :** `{name1}`\n**├── Extention :**  {CR} .mp3\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'
                cchtml = f'[——— ✦ {str(count).zfill(3)} ✦ ———]({link0})\n\n**🌐 Title :** `{name1}`\n**├── Extention :**  {CR} .html\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'

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
                    
                elif 'encrypted.m' in url:    
                    remaining_links = len(links) - count
                    progress = (count / len(links)) * 100
                    emoji_message = await show_random_emojis(m)
                    Show = f"🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%\n┃\n" \
                           f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                           f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 𝐋𝐢𝐧𝐤𝐬 » {remaining_links}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Eɴᴄʀʏᴘᴛᴇᴅ Sᴛᴀʀᴛᴇᴅ...⏳**\n┃\n" \
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"📚�	T𝐢𝐭𝐥𝐞 » {name}\n┃\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**\n┃\n" \
                           f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [ELIESE🐦](https://t.me/+MdZ2996M2G43MWFl)"                    
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.download_and_decrypt_video(url, cmd, name, appxkey)
                    filename = res_file
                    await emoji_message.delete()
                    await prog.delete()
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    await asyncio.sleep(1)
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
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n" \
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
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 » {CR}\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"📚�	T𝐢𝐭𝐥𝐞 » {name}\n┃\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**\n┃\n" \
                           f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [ELIESE🐦](https://t.me/+MdZ2996M2G43MWFl)"                    
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
                await m.reply_text(f'⚠️**Downloading Failed**⚠️\n**Name** =>> `{str(count).zfill(3)} {name1}`\n**Url** =>> {link0}', disable_web_page_preview=True)
                count += 1
                failed_count += 1
                continue

    except Exception as e:
        await m.reply_text(str(e))
        time.sleep(2)

    await m.reply_text(f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
    await m.reply_text(f"⋅ ─ list index ({raw_text}-{len(links)}) out of range ─ ⋅\n\n✨ **BATCH** » {b_name}✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")
             
bot.run()
