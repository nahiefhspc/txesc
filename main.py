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
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
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
api_token = "03"
token_cp = '01'
adda_token = "02"
photologo = 'https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png'
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png'
photocp = 'https://tinypic.host/images/2025/03/28/IMG_20250328_133126.jpg'
photozip = 'https://envs.sh/cD_.jpg'
log_chat_id = "-1002976562617"

async def show_random_emojis(message: Message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻‍❄️', '☁️', '🚹', '🚺', '🐠', '🦋']
    if message is None:
        print("Error: Message is None in show_random_emojis")
        return None
    try:
        emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
        return emoji_message
    except Exception as e:
        print(f"Error in show_random_emojis: {str(e)}")
        await bot.send_message(log_chat_id, f"Error in show_random_emojis: {str(e)}")
        return None

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
        input_message: Message = await client.listen(m.chat.id, timeout=30)
        if input_message is None:
            await client.send_message(log_chat_id, f"Error: Cookies input timed out for user {m.from_user.id}")
            return

        if not input_message.document or not input_message.document.file_name.endswith(".txt"):
            await m.reply_text("Invalid file type. Please upload a .txt file.")
            return

        downloaded_path = await input_message.download()

        with open(downloaded_path, "r") as uploaded_file:
            cookies_content = uploaded_file.read()

        with open(cookies_file_path, "w") as target_file:
            target_file.write(cookies_content)

        await input_message.reply_text(
            "✅ Cookies updated successfully.\n📂 Saved in `youtube_cookies.txt`."
        )

    except Exception as e:
        await m.reply_text(f"⚠️ An error occurred: {str(e)}")
        await client.send_message(log_chat_id, f"Error in cookies_handler: {str(e)}")

@bot.on_message(filters.command(["t2t"]))
async def text_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    editable = await message.reply_text(f"<blockquote>Welcome to the Text to .txt Converter!\nSend the **text** for convert into a `.txt` file.</blockquote>")
    input_message: Message = await bot.listen(message.chat.id, timeout=30)
    if input_message is None:
        await editable.edit("Error: No text received within timeout.")
        await client.send_message(log_chat_id, f"Error: t2t input timed out for user {user_id}")
        return
    if not input_message.text:
        await message.reply_text("🚨 **error**: Send valid text data")
        return

    text_data = input_message.text.strip()
    await input_message.delete()
    
    await editable.edit("**🔄 Send file name or send /d for filename**")
    inputn: Message = await bot.listen(message.chat.id, timeout=30)
    if inputn is None:
        await editable.edit("Error: No filename received within timeout.")
        await client.send_message(log_chat_id, f"Error: t2t filename input timed out for user {user_id}")
        return
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

UPLOAD_FOLDER = '/path/to/upload/folder'
EDITED_FILE_PATH = '/path/to/save/edited_output.txt'

@bot.on_message(filters.command(["y2t"]))
async def youtube_to_txt(client, message: Message):
    user_id = str(message.from_user.id)
    
    editable = await message.reply_text(
        f"Send YouTube Website/Playlist link for convert in .txt file"
    )

    input_message: Message = await bot.listen(message.chat.id, timeout=30)
    if input_message is None:
        await editable.edit("Error: No YouTube link received within timeout.")
        await client.send_message(log_chat_id, f"Error: y2t input timed out for user {user_id}")
        return
    youtube_link = input_message.text.strip()
    await input_message.delete()
    await editable.delete()

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
            await client.send_message(log_chat_id, f"Error in y2t: {str(e)} for user {user_id}")
            return

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

    txt_file = os.path.join("downloads", f'{title}.txt')
    os.makedirs(os.path.dirname(txt_file), exist_ok=True)
    with open(txt_file, 'w') as f:
        f.write('\n'.join(videos))

    await message.reply_document(
        document=txt_file,
        caption=f'<a href="{youtube_link}">__**Click Here to Open Link**__</a>\n<pre><code>{title}.txt</code></pre>\n'
    )

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
        await client.send_message(log_chat_id, f"Error in mfile_handler: {str(e)}")

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
async def help_command(client: Client, m: Message):
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
        await client.send_message(log_chat_id, f"Error in send_logs: {str(e)}")

async def decrypt_file_txt(file_path):
    return file_path

@bot.on_message(filters.command(["drm"]))
async def txt_handler(bot: Client, m: Message):
    if m is None:
        print("Error: Message is None in txt_handler")
        await bot.send_message(log_chat_id, "Error: Message is None in txt_handler")
        return

    editable = await m.reply_text(f"`🔹Hi I am Poweful TXT Downloader📥 Bot.\n🔹Send me the txt file and wait.`")
    input: Message = await bot.listen(editable.chat.id, timeout=30)
    if input is None:
        await editable.edit("Error: No file received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler file input timed out for user {m.from_user.id}")
        return
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
    except Exception as e:
        await m.reply_text("<pre><code>🔹Invalid file input.</code></pre>")
        await bot.send_message(log_chat_id, f"Error reading file in txt_handler: {str(e)}")
        os.remove(x)
        return
    
    await editable.edit(f"`🔹Total 🔗 links found are {len(links)}\n\n🔹Img : {img_count}  🔹PDF : {pdf_count}\n🔹ZIP : {zip_count}  🔹Other : {other_count}\n\n🔹Send From where you want to download.`")
    input0: Message = await bot.listen(editable.chat.id, timeout=30)
    if input0 is None:
        await editable.edit("Error: No start index received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler start index input timed out for user {m.from_user.id}")
        return
    raw_text = input0.text
    await input0.delete()
           
    await editable.edit("`🔹Enter Your Batch Name\n🔹Send 1 for use default.`")
    input1: Message = await bot.listen(editable.chat.id, timeout=30)
    if input1 is None:
        await editable.edit("Error: No batch name received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler batch name input timed out for user {m.from_user.id}")
        return
    raw_text0 = input1.text
    await input1.delete()
    if raw_text0 == '1':
        b_name = file_name.replace('_', ' ')
    else:
        b_name = raw_text0

    await editable.edit("╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n╰━━⌈⚡[`🦋𝗘𝗟𝗜𝗘𝗦𝗘🦋`]⚡⌋━━➣")
    input2: Message = await bot.listen(editable.chat.id, timeout=30)
    if input2 is None:
        await editable.edit("Error: No resolution received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler resolution input timed out for user {m.from_user.id}")
        return
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
    input3: Message = await bot.listen(editable.chat.id, timeout=30)
    if input3 is None:
        await editable.edit("Error: No name received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler name input timed out for user {m.from_user.id}")
        return
    raw_text3 = input3.text
    await input3.delete()
    if raw_text3 == '1':
        CR = '[𝄟⃝‌🐬🇳‌ɪᴋʜɪʟ𝄟⃝🐬](https://t.me/+MdZ2996M2G43MWFl)'
    else:
        CR = raw_text3

    await editable.edit("🔹Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋\n🔹Send /d for use default\n🔹Send /d1 for lower quality\n🔹Send /d2 for lowest quality")
    input4: Message = await bot.listen(editable.chat.id, timeout=30)
    if input4 is None:
        await editable.edit("Error: No PW token received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler PW token input timed out for user {m.from_user.id}")
        return
    raw_text4 = input4.text
    await input4.delete()

    await editable.edit("🔹Enter Your PW Token 😔 2nd wala Bro\n🔹Send /d for use default")
    input20: Message = await bot.listen(editable.chat.id, timeout=30)
    if input20 is None:
        await editable.edit("Error: No second PW token received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler second PW token input timed out for user {m.from_user.id}")
        return
    raw_text20 = input20.text
    await input20.delete()    

    await editable.edit(f"🔹Send the Video Thumb URL\n🔹Send /d for use default\n\n🔹You can direct upload thumb\n🔹Send **No** for use default")
    input6: Message = await bot.listen(editable.chat.id, timeout=30)
    if input6 is None:
        await editable.edit("Error: No thumb URL received within timeout.")
        await bot.send_message(log_chat_id, f"Error: txt_handler thumb URL input timed out for user {m.from_user.id}")
        return
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
            Vxy = links[i][1].replace("file/d/", "uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")
            if not Vxy.startswith("https://"):
                url = "https://" + Vxy
            else:
                url = Vxy
            title = links[i][0]
            if "💀" in title:
                parts = title.split("💀")
                name1 = parts[0].strip()
                # Check if there's a 🤩 delimiter in the second part
                if len(parts) > 1 and "🤩" in parts[1]:
                    sub_parts = parts[1].split("🤩")
                    raw_text65 = sub_parts[0].strip()
                    if len(sub_parts) > 1:
                        raw_text102 = sub_parts[1].strip()
                else:
                    raw_text65 = parts[1].strip() if len(parts) > 1 else ""
            else:
                name1 = title.strip()

            cleaned_name1 = name1.replace("(", "[").replace(")", "]").replace("_", "").replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'[𝗛𝗔𝗖𝗞𝗛𝗘𝗜𝗦𝗧😈]{cleaned_name1[:60]}'
            
            if "rarestudy" in url:                
                def fetch_with_retries(local_url, headers=None, max_retries=8, timeout=6):
                    for attempt in range(max_retries):
                        try:
                            resp = requests.get(local_url, headers=headers, timeout=timeout)
                            resp.raise_for_status()
                            return resp
                        except requests.RequestException as e:
                            print(f"[Retry {attempt+1}] {e}")
                            if attempt < max_retries - 1:
                                time.sleep(2)
                    return None

                def transform_rarestudy_url(input_url):
                    parsed = urlparse(input_url)
                    if '/media/' in input_url:
                        return input_url.replace('/media/', '/video-data?encoded=')
                    parts = parsed.path.split('/')
                    if 'media' in parts:
                        idx = parts.index('media')
                        encoded = '/'.join(parts[idx+1:])
                        new_query = urlencode({'encoded': encoded})
                        return urlunparse((parsed.scheme, parsed.netloc, '/video-data', '', new_query, ''))
                    return input_url

                token_resp = fetch_with_retries(
                    "https://rarekatoken2.vercel.app/token",
                    headers={'Content-Type': 'application/json'}
                )
                if token_resp:
                    try:
                        session_token = token_resp.json().get("use_token", "raw_text98")
                    except json.JSONDecodeError:
                        session_token = "raw_text98"
                else:
                    session_token = "raw_text98"

                media_headers = {
                    'authority': 'rarestudy.site',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                    'cache-control': 'no-cache',
                    "cookie": f"cf_clearance=cf_clearance=g3z7irdDD_BHTi3MpE6UR1ay4eiXTVG5RkRAMVhKILY-1751948668-1.2.1.1-N72U8xIccTHnfRiJKnZ.6.7mFmGEyNtSKCGzExb012j7Stkj.tPSBic648hLtwqgM.lAlXy0u_JWeAoqL4C3smrGgLTPwHlhVNuf0kxOC5QYDhjj.elN4ZjSoh8doZN1V6BWcl3_eALAXHwzZUwP4Gp9J.fpDzuFCAIonMfPPtVMt4Ib7SiRLoEVsAmP7s6R1XueOqPqYCa9nVygHZBa3MRUsBcwC8SdOEfwy9TiFZE; session={session_token}",
                    'pragma': 'no-cache',
                    'referer': 'https://rarestudy.site/batches',
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
                media_resp = fetch_with_retries(url, headers=media_headers)
                if not media_resp:
                    print("❌ Failed to fetch /media link.")
                    video_url = ""
                else:
                    transformed_url = transform_rarestudy_url(url)
                    print(f"➡ Transformed URL: {transformed_url}")

                    meta_headers = {
                        'authority': 'rarestudy.site',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
                        'cache-control': 'no-cache',
                        "cookie": f"cf_clearance=cf_clearance=g3z7irdDD_BHTi3MpE6UR1ay4eiXTVG5RkRAMVhKILY-1751948668-1.2.1.1-N72U8xIccTHnfRiJKnZ.6.7mFmGEyNtSKCGzExb012j7Stkj.tPSBic648hLtwqgM.lAlXy0u_JWeAoqL4C3smrGgLTPwHlhVNuf0kxOC5QYDhjj.elN4ZjSoh8doZN1V6BWcl3_eALAXHwzZUwP4Gp9J.fpDzuFCAIonMfPPtVMt4Ib7SiRLoEVsAmP7s6R1XueOqPqYCa9nVygHZBa3MRUsBcwC8SdOEfwy9TiFZE; session={session_token}",
                        'pragma': 'no-cache',
                        'referer': 'https://rarestudy.site/batches',
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
                    video_resp = fetch_with_retries(transformed_url, headers=meta_headers)
                    video_url = ""
                    if video_resp:
                        try:
                            data = video_resp.json()
                            video_url = data.get("data", {}).get("url", "")
                        except json.JSONDecodeError:
                            m = re.search(r'"url"\s*:\s*"(?P<u>https?://[^"]+)"', video_resp.text)
                            if m:
                                video_url = m.group('u')

                if not video_url:
                    print("❌ No video URL found.")
                else:
                    print(f"➡ Raw video URL: {video_url}")

                    transformed_video_url = video_url.replace(
                        "https://sec-prod-mediacdn.pw.live",
                        "https://anonymouspwplayer-0e5a3f512dec.herokuapp.com/sec-prod-mediacdn.pw.live"
                    )

                    access_resp = fetch_with_retries(
                        "https://api-accesstoken.vercel.app",
                        headers={'Content-Type': 'application/json'}
                    )
                    access_token = ""
                    if access_resp:
                        try:
                            access_token = access_resp.json().get("access_token", "")
                        except json.JSONDecodeError:
                            pass

                    # Set qualities based on raw_text4
                    if raw_text4 == "/d":
                        qualities = [720, 480, 360, 240]
                    elif raw_text4 == "/d1":
                        qualities = [480, 360, 240]
                    elif raw_text4 == "/d2":
                        qualities = [360, 240]
                    else:
                        qualities = [720, 480, 360, 240]  # Default fallback

                    url_found = ""
                    for q in qualities:
                        hls_url = transformed_video_url.replace("master.mpd", f"hls/{q}/main.m3u8")
                        final_url = f"{hls_url}&token={access_token}"
                        chk = fetch_with_retries(final_url)
                        if chk and chk.status_code == 200 and '#EXTM3U' in chk.text[:200]:
                            url_found = final_url
                            print(f"✅ Working URL ({q}p): {url_found}")
                            break
                        else:
                            print(f"✖ {q}p not available.")

                    if not url_found:
                        fallback_q = qualities[-1]
                        hls_url = transformed_video_url.replace("master.mpd", f"hls/{fallback_q}/main.m3u8")
                        url_found = f"{hls_url}&token={access_token}" if access_token else hls_url
                        print(f"⚠ Using fallback {fallback_q}p: {url_found}")

                    url = url_found

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            elif "embed" in url:
                ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
            else:
                ytf = f"b[height<={raw_text2}][protocol=https]/bv[height<={raw_text2}][protocol=https]+ba/b/bv+ba"

            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
                cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies {cookies_file_path} -f "{ytf}" "{url}" -o "{name}.mp4"'                       
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'                        
            try:
                cc = f'**|🇮🇳| {cleaned_name1}.mkv\n\n😎 𝗤𝘂𝗮𝗹𝗶𝘁𝘆 ➠ {raw_text102}\n\n🧿 𝐁𝐀𝐓𝐂𝐇 ➤ {b_name}\n\nChapterId > {raw_text65}**'
                cc1 = f'**|🇮🇳| {cleaned_name1}.pdf\n\n🧿 𝐁𝐀𝐓𝐂𝐇 ➤ {b_name}\n\nChapterId > {raw_text65}**'
                cczip = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**📁 Title :** `{name1}`\n**├── Extention :**  {CR} .zip\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'
                ccimg = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**🖼️ Title :** `{name1}`\n**├── Extention :**  {CR} .jpg\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'
                ccm = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**🎵 Title :** `{name1}`\n**├── Extention :**  {CR} .mp3\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'
                cchtml = f'[——— ✦ {str(count).zfill(3)} ✦ ———]()\n\n**🌐 Title :** `{name1}`\n**├── Extention :**  {CR} .html\n\n**📚 Course :** {b_name}\n\n**🌟 Extracted By :** {CR}'

                if "drive" in url:
                    ka = await helper.download(url, name)
                    copy = await bot.send_document(chat_id=m.chat.id, document=ka, caption=cc1)
                    count += 1
                    os.remove(ka)
                    await asyncio.sleep(1)
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
                        await asyncio.sleep(e.x)
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
                        await asyncio.sleep(e.x)
                        count += 1
                        continue              

                elif ".ws" in url and url.endswith(".ws"):
                    await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}", f"{name}.html")
                    await asyncio.sleep(1)
                    await bot.send_document(chat_id=m.chat.id, document=f"{name}.html", caption=cchtml)
                    os.remove(f'{name}.html')
                    count += 1
                    await asyncio.sleep(5)
                    continue
                            
                elif ".zip" in url:
                    BUTTONSZIP = InlineKeyboardMarkup([[InlineKeyboardButton(text="🎥 ZIP STREAM IN PLAYER", url=f"{url}")]])
                    await bot.send_photo(chat_id=m.chat.id, photo=photozip, caption=cczip, reply_markup=BUTTONSZIP)
                    count += 1
                    await asyncio.sleep(1)    
                    continue

                elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                    ext = url.split('.')[-1]
                    cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_photo(chat_id=m.chat.id, photo=f'{name}.{ext}', caption=ccimg)
                    count += 1
                    os.remove(f'{name}.{ext}')
                    await asyncio.sleep(1)
                    continue

                elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                    ext = url.split('.')[-1]
                    cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                    download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                    os.system(download_cmd)
                    copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.{ext}', caption=ccm)
                    count += 1
                    os.remove(f'{name}.{ext}')
                    await asyncio.sleep(1)
                    continue
                    
                elif 'encrypted.m' in url:    
                    remaining_links = len(links) - count
                    progress = (count / len(links)) * 100
                    emoji_message = await show_random_emojis(m)
                    if emoji_message is None:
                        await bot.send_message(log_chat_id, f"Error: Failed to show emoji for ID {count}, Name {name1}")
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
                    if emoji_message:
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
                    if emoji_message is None:
                        await bot.send_message(log_chat_id, f"Error: Failed to show emoji for ID {count}, Name {name1}")
                    Show = f"🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%\n┃\n" \
                           f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n" \
                           f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 𝐋𝐢𝐧𝐤𝐬 » {remaining_links}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Dʀᴍ Sᴛᴀʀᴛᴇᴅ...⏳**\n┃\n" \
                           f'┣💃𝐂𝐫𝐞𝐝𝐢𝐴𝐭 » {CR}\n┃\n' \
                           f"╰━📚𝐁𝐚𝐭𝐚𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"📚�	T𝐢𝐭𝐥𝐞 » {name}\n┃\n" \
                           f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" \
                           f"🛑**Send** /stop **to stop process**\n┃\n" \
                           f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [ELIESE🐦](https://t.me/+MdZ2996M2G43MWFl)"                    
                    prog = await m.reply_text(Show, disable_web_page_preview=True)
                    res_file = await helper.decrypt_and_merge_video(mpd, keys_string, path, name, raw_text2)
                    filename = res_file
                    if emoji_message:
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
                    if emoji_message is None:
                        await bot.send_message(log_chat_id, f"Error: Failed to show emoji for ID {count}, Name {name1}")
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
                    if emoji_message:
                        await emoji_message.delete()
                    await prog.delete()
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    await asyncio.sleep(1)
                    continue
                
            except Exception as e:
                if m is not None:
                    await m.reply_text(
                        f'⚠️**Downloading Failed**⚠️\n**ID** =>> `{str(count).zfill(3)}`\n\n**Name** - `{name1}`**',
                        disable_web_page_preview=True
                    )
                else:
                    await bot.send_message(
                        log_chat_id,
                        f"Error: Downloading failed for ID {str(count).zfill(3)}, Name {name1}: {str(e)}"
                    )
                count += 1
                failed_count += 1
                await asyncio.sleep(1)
                continue

    except Exception as e:
        if m is not None:
            await m.reply_text(f"Error: {str(e)}")
        else:
            await bot.send_message(log_chat_id, f"Error in txt_handler: {str(e)}")
        await asyncio.sleep(2)

    if m is not None:
        await m.reply_text(f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
        await m.reply_text(
            f"⋅ ─ list index ({raw_text}-{len(links)}) out of range ─ ⋅\n\n✨ **BATCH** » {b_name}✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅"
        )
    else:
        await bot.send_message(
            log_chat_id,
            f"Error: Cannot send completion message, m is None. Total failed: {failed_count}, Batch: {b_name}"
        )

bot.run()
