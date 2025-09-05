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
import cloudscraper
from base64 import b64encode, b64decode
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import saini as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from subprocess import getstatusoutput
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import random
import logging

# Configure logging
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Bot configuration
OP_COMMAND = os.environ.get("OP_COMMAND", "drm")
NONOP_COMMAND = os.environ.get("NONOP_COMMAND", "stop")
cookies_file_path = os.getenv("cookies_file_path", "youtube_cookies.txt")
api_url = "http://master-api-v3.vercel.app/"
api_token = "hhxJ3k1GTWoBUbivUe1I"
photologo = 'https://tinypic.host/images/2025/02/07/DeWatermark.ai_1738952933236-1.png'
photoyt = 'https://tinypic.host/images/2025/03/18/YouTube-Logo.wine.png'
photocp = 'https://tinypic.host/images/2025/03/28/IMG_20250328_133126.jpg'
photozip = 'https://envs.sh/cD_.jpg'

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Inline keyboard for start command
keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="📞 Contact", url="https://t.me/saini_contact_bot"),
            InlineKeyboardButton(text="🛠️ Help", url="https://t.me/+3k-1zcJxINYwNGZl"),
        ],
    ]
)

# Random emoji display
async def show_random_emojis(message):
    emojis = ['🐼', '🐶', '🐅', '⚡️', '🚀', '✨', '💥', '☠️', '🥂', '🍾', '📬', '👻', '👀', '🌹', '💀', '🐇', '⏳', '🔮', '🦔', '📖', '🦁', '🐱', '🐻‍❄️', '☁️', '🚹', '🚺', '🐠', '🦋']
    emoji_message = await message.reply_text(' '.join(random.choices(emojis, k=1)))
    return emoji_message

# Placeholder for text file decryption
async def decrypt_file_txt(file_path):
    # Implement actual decryption if needed
    return file_path

# State dictionary to track user input stages
user_states = {}

@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    try:
        with open("logs.txt", "rb") as file:
            sent = await m.reply_text("**📤 Sending you ....**")
            await m.reply_document(document=file)
            await sent.delete()
    except Exception as e:
        await m.reply_text(f"Error sending logs: {e}")

@bot.on_message(filters.command([OP_COMMAND]))
async def txt_handler(bot: Client, m: Message):
    user_id = m.from_user.id
    user_states[user_id] = {"stage": "awaiting_file", "message_id": m.id}
    await m.reply_text(
        f"`🔹Hi I am Powerful TXT Downloader📥 Bot.\n🔹Send me the txt file and wait.`",
        quote=True
    )

@bot.on_message(filters.document | filters.text)
async def handle_user_input(bot: Client, m: Message):
    user_id = m.from_user.id
    if user_id not in user_states:
        return

    state = user_states[user_id]["stage"]
    chat_id = m.chat.id
    message_id = user_states[user_id]["message_id"]

    try:
        if state == "awaiting_file" and m.document:
            # Handle text file
            y = await m.download()
            file_name, ext = os.path.splitext(os.path.basename(y))

            if file_name.endswith("_helper"):
                x = await decrypt_file_txt(y)
                await m.delete()
            else:
                x = y

            path = f"./downloads/{chat_id}"
            pdf_count = img_count = zip_count = other_count = 0

            # Parse text file
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
                await bot.send_message(chat_id, f"<pre><code>🔹Invalid file input: {e}</code></pre>")
                os.remove(x)
                del user_states[user_id]
                return

            user_states[user_id] = {
                "stage": "awaiting_index",
                "message_id": message_id,
                "file_name": file_name,
                "links": links,
                "path": path,
                "pdf_count": pdf_count,
                "img_count": img_count,
                "zip_count": zip_count,
                "other_count": other_count
            }
            await bot.send_message(
                chat_id,
                f"`🔹Total 🔗 links found are {len(links)}\n\n🔹Img : {img_count}  🔹PDF : {pdf_count}\n"
                f"🔹ZIP : {zip_count}  🔹Other : {other_count}\n\n🔹Send From where you want to download.`"
            )

        elif state == "awaiting_index" and m.text:
            raw_text = m.text
            await m.delete()
            file_name = user_states[user_id]["file_name"]
            links = user_states[user_id]["links"]
            path = user_states[user_id]["path"]
            user_states[user_id]["raw_text"] = raw_text
            user_states[user_id]["stage"] = "awaiting_batch_name"
            await bot.send_message(
                chat_id,
                "`🔹Enter Your Batch Name\n🔹Send 1 for use default.`"
            )

        elif state == "awaiting_batch_name" and m.text:
            raw_text0 = m.text
            await m.delete()
            file_name = user_states[user_id]["file_name"]
            b_name = file_name.replace('_', ' ') if raw_text0 == '1' else raw_text0
            user_states[user_id]["b_name"] = b_name
            user_states[user_id]["stage"] = "awaiting_resolution"
            await bot.send_message(
                chat_id,
                "╭━━━━❰ᴇɴᴛᴇʀ ʀᴇꜱᴏʟᴜᴛɪᴏɴ❱━━➣ \n"
                "┣━━⪼ send `144`  for 144p\n┣━━⪼ send `240`  for 240p\n┣━━⪼ send `360`  for 360p\n"
                "┣━━⪼ send `480`  for 480p\n┣━━⪼ send `720`  for 720p\n┣━━⪼ send `1080` for 1080p\n"
                "╰━━⌈⚡[`🦋𝗘𝗟𝗜𝗘𝗦𝗘🦋`]⚡⌋━━➣"
            )

        elif state == "awaiting_resolution" and m.text:
            raw_text2 = m.text
            await m.delete()
            quality = f"{raw_text2}p"
            try:
                res = {
                    "144": "256x144",
                    "240": "426x240",
                    "360": "640x360",
                    "480": "854x480",
                    "720": "1280x720",
                    "1080": "1920x1080"
                }.get(raw_text2, "UN")
            except Exception:
                res = "UN"

            default_thumb_url = "https://files.catbox.moe/g02k3k.jpg"
            getstatusoutput(f"wget '{default_thumb_url}' -O 'thumb.jpg'")
            thumb = "thumb.jpg"
            await bot.send_message(chat_id, f"🎯Target Batch : `{user_states[user_id]['b_name']}`")

            failed_count = count = int(user_states[user_id]["raw_text"])
            arg = int(user_states[user_id]["raw_text"])
            links = user_states[user_id]["links"]
            path = user_states[user_id]["path"]
            b_name = user_states[user_id]["b_name"]

            for i in range(arg - 1, len(links)):
                Vxy = links[i][1].replace("file/d/", "uc?export=download&id=").replace(
                    "www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing", "")
                url = f"https://{Vxy}" if not Vxy.startswith("https://") else Vxy

                # Parse title
                title = links[i][0]
                raw_text97 = name1 = raw_text65 = ""
                if "🌚" in title and "💀" in title:
                    try:
                        parts = title.split("🌚")
                        if len(parts) >= 3:
                            raw_text97 = parts[1].strip()
                            remaining = parts[2].split("💀")
                            if len(remaining) >= 3:
                                name1 = remaining[0].strip()
                                raw_text65 = remaining[1].strip()
                            else:
                                name1 = remaining[0].strip() if remaining else title.strip()
                    except IndexError:
                        name1 = title.strip()
                else:
                    name1 = title.strip()

                cleaned_name1 = name1.replace("(", "[").replace(")", "]").replace("_", "").replace(
                    "\t", "").replace(":", "").replace("/", "").replace("+", "").replace(
                    "#", "").replace("|", "").replace("@", "").replace("*", "").replace(
                    ".", "").replace("https", "").replace("http", "").strip()
                name = f'[𝗛𝗔𝗖𝗞𝗛𝗘𝗜𝗦𝗧😈]{cleaned_name1[:60]}'

                # Initialize keys_string for DRM videos
                keys_string = ""

                # Handle specific URL types
                if "visionias" in url:
                    async with ClientSession() as session:
                        async with session.get(url, headers={
                            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
                            match = re.search(r"(https://.*?playlist.m3u8.*?)\"", text)
                            url = match.group(1) if match else url

                elif "studystark.site" in url:
                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        data = response.json()
                        video_url = data.get("video_url", "")
                        key_id = data.get("key_id", "")  # IV
                        key_value = data.get("key_value", "")  # Key
                        if video_url:
                            if video_url.endswith("master.mpd"):
                                mpd_url = video_url.replace("master.mpd", f"hls/{raw_text97}/main.m3u8")
                            else:
                                base_url = video_url.rsplit("/", 1)[0]
                                mpd_url = f"{base_url}/hls/{raw_text97}/main.m3u8"
                            if key_id and key_value:
                                try:
                                    key_hex = b64decode(key_value).hex()
                                    iv_hex = b64decode(key_id).hex()
                                    keys_string = f"--key 1:{key_hex}:{iv_hex}"
                                except Exception as e:
                                    logging.error(f"Error decoding key/IV for {url}: {e}")
                                    keys_string = ""
                            else:
                                keys_string = ""
                            url = mpd_url
                        else:
                            logging.error(f"Error: video_url is empty for {url}")
                            url = ""
                    except Exception as e:
                        logging.error(f"Error processing studystark.site URL {url}: {e}")
                        url = ""
                        keys_string = ""

                elif "pwjarvis.com" in url:
                    headers = {
                        "authority": "www.pwjarvis.com",
                        "accept": "*/*",
                        "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                        "cache-control": "no-cache",
                        "cookie": "cf_clearance=nC4cEcM0X3WsSWu6kQ8feRZZsFlGkO52ZU3_9OgrRE4-1756788206-1.2.1.1-DOgfOPatw5BeN7X0xH7j8H8Xut0vBpIIhhldZ9QvIdvecugdjdvQeTZRlSnH7tOi8f4ML4yeoZGMzjLwrCiUR.h.gGpBVxRS1RNAdZkVDv2nkHU9ev5Qv23iPze2cVl9Gv.4WuGGidMGn3k8gfewbVSIqmdQG6Zlir98RVyfAY9X60wZFff7d1N_PioI.0oc_9W1SRK.9ccuBW4xvUcuIdURhLnueatfHUbyAUYlAWc; PWS=Fe26.2*1*9c270963cdf469805abaf9e5673167358fd36fba6d7a613797cdcaed3ed6d588*5fY55QYgEqSLF0vSS_Oumg*bAx08VnQVZaBbZiKRQnPSMjWANHMCzQOZSM3TnpHd0uwG1syZL0iZOuzWXsiK4NMrPoCXV6KhFgLbh0w11yy8Sg0Zpua6aSdID3l0SxGdx6uGHQA6UAYyvHTboknVcG6psT9yhQnQfVhYjuLC3-t130eI5w4XZnMTscD2409Hv4*1757902047797*2057847dd4c4bee6d06a92a80c589d420a3929ac57cd37fdab8d1c709e31d863*uImyuHN9VAlJvgpgT7mz-4sHmVTgFVLM44bj09JdLyw~2",
                        "next-router-state-tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22study%22%2C%7B%22children%22%3A%5B%22batches%22%2C%7B%22children%22%3A%5B%5B%22batchID%22%2C%22prayas-2023-617434%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22subjects%22%2C%7B%22children%22%3A%5B%5B%22subjectID%22%2C%22physics-785455%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22topics%22%2C%7B%22children%22%3A%5B%5B%22topicID%22%2C%22jee-mains-revision-333137%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22schedule%22%2C%7B%22children%22%3A%5B%5B%22scheduleId%22%2C%22dedeffe13da404f223b84cb90f4ca72c2c1114d30f41da755f1f36abdd38850e%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%2C%22%2Fstudy%2Fbatches%2Fprayas-2023-617434%2Fsubjects%2Fphysics-785455%2Ftopics%2Fjee-mains-revision-333137%2Fschedule%2Fdedeffe13da404f223b84cb90f4ca72c2c1114d30f41da755f1f36abdd38850e%22%2C%22refetch%22%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D%7D%5D",
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
                            transformed_link = original_link.replace(
                                "https://cors.pwjarvis.com", "https://stream.pwjarvis.com"
                            ).replace("/master.mpd", f"/hls/{raw_text97}/main.m3u8")
                            url = transformed_link
                        else:
                            raise Exception("Video link not found in the response")
                    else:
                        raise Exception(f"Failed to fetch the page, status code: {response.status_code}")

                # Determine yt-dlp format
                if "youtu" in url:
                    ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
                elif "embed" in url:
                    ytf = f"bestvideo[height<={raw_text2}]+bestaudio/best[height<={raw_text2}]"
                else:
                    ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

                # Construct yt-dlp command
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
                        if ka:
                            await bot.send_document(chat_id=chat_id, document=ka, caption=cc1)
                            count += 1
                            os.remove(ka)
                        await asyncio.sleep(1)
                        continue

                    elif ".pdf*" in url:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        subprocess.run(download_cmd, shell=True, check=True)
                        await bot.send_document(chat_id=chat_id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                        continue

                    elif ".pdf" in url and ".pdf*" not in url:
                        url = url.replace(" ", "%20")
                        scraper = cloudscraper.create_scraper()
                        response = scraper.get(url)
                        if response.status_code == 200:
                            with open(f'{name}.pdf', 'wb') as file:
                                file.write(response.content)
                            await asyncio.sleep(4)
                            await bot.send_document(chat_id=chat_id, document=f'{name}.pdf', caption=cc1)
                            count += 1
                            os.remove(f'{name}.pdf')
                        else:
                            await bot.send_message(chat_id, f"Failed to download PDF: {response.status_code} {response.reason}")
                        continue

                    elif ".ws" in url and url.endswith(".ws"):
                        await helper.pdf_download(f"{api_url}utkash-ws?url={url}&authorization={api_token}", f"{name}.html")
                        await bot.send_document(chat_id=chat_id, document=f"{name}.html", caption=cchtml)
                        os.remove(f'{name}.html')
                        count += 1
                        await asyncio.sleep(5)
                        continue

                    elif ".zip" in url:
                        BUTTONSZIP = InlineKeyboardMarkup([[InlineKeyboardButton(text="🎥 ZIP STREAM IN PLAYER", url=f"{url}")]])
                        await bot.send_photo(chat_id=chat_id, photo=photozip, caption=cczip, reply_markup=BUTTONSZIP)
                        count += 1
                        await asyncio.sleep(1)
                        continue

                    elif any(ext in url for ext in [".jpg", ".jpeg", ".png"]):
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        subprocess.run(download_cmd, shell=True, check=True)
                        await bot.send_photo(chat_id=chat_id, photo=f'{name}.{ext}', caption=ccimg)
                        count += 1
                        os.remove(f'{name}.{ext}')
                        await asyncio.sleep(1)
                        continue

                    elif any(ext in url for ext in [".mp3", ".wav", ".m4a"]):
                        ext = url.split('.')[-1]
                        cmd = f'yt-dlp -o "{name}.{ext}" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        subprocess.run(download_cmd, shell=True, check=True)
                        await bot.send_document(chat_id=chat_id, document=f'{name}.{ext}', caption=ccm)
                        count += 1
                        os.remove(f'{name}.{ext}')
                        await asyncio.sleep(1)
                        continue

                    elif 'drmcdni' in url or 'drm/wv' in url or 'studystark.site' in url:
                        remaining_links = len(links) - count
                        progress = (count / len(links)) * 100
                        emoji_message = await show_random_emojis(m)
                        Show = (
                            f"🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%\n┃\n"
                            f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n"
                            f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 𝐋𝐢𝐧𝐤𝐬 » {remaining_links}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Dʀᴍ Sᴛᴀʀᴛᴇᴅ...⏳**\n┃\n"
                            f'┣💃𝐂𝐫𝐞𝐝𝐢𝐭 »\n┃\n'
                            f"╰━📚𝐁𝐚𝐭𝐚𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📚�	T𝐢𝐭𝐥𝐞 » {name}\n┃\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🛑**Send** /stop **to stop process**\n┃\n"
                            f"╰━✦𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ [ELIESE🐦](https://t.me/+MdZ2996M2G43MWFl)"
                        )
                        prog = await bot.send_message(chat_id, Show, disable_web_page_preview=True)
                        try:
                            res_file = await helper.decrypt_and_merge_video(url, keys_string, path, name, raw_text2)
                            filename = res_file
                            await emoji_message.delete()
                            await prog.delete()
                            await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                            count += 1
                        except Exception as e:
                            await bot.send_message(chat_id, f"Failed to process DRM video {name}: {e}")
                            count += 1
                            failed_count += 1
                        await asyncio.sleep(1)
                        continue

                    else:
                        remaining_links = len(links) - count
                        progress = (count / len(links)) * 100
                        emoji_message = await show_random_emojis(m)
                        Show = (
                            f"🚀𝐏𝐫𝐨𝐠𝐫𝐞𝐬𝐬 » {progress:.2f}%\n┃\n"
                            f"┣🔗𝐈𝐧𝐝𝐞𝐱 » {count}/{len(links)}\n┃\n"
                            f"╰━🖇️𝐑𝐞𝐦𝐚𝐢𝐧 𝐋𝐢𝐧𝐤𝐬 » {remaining_links}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"**⚡Dᴏᴡɴʟᴏᴀᴅɪɴɢ Sᴛᴀʀᴛᴇᴅ...⏳**\n┃\n"
                            f"╰━📚𝐁𝐚𝐭𝐚𝐜𝐡 𝐍𝐚𝐦𝐞 » {b_name}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📚�	T𝐢𝐭𝐥𝐞 » {name}\n┃\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🛑**Send** /stop **to stop process**"
                        )
                        prog = await bot.send_message(chat_id, Show, disable_web_page_preview=True)
                        try:
                            res_file = await helper.download_video(url, cmd, name)
                            filename = res_file
                            await emoji_message.delete()
                            await prog.delete()
                            await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                            count += 1
                        except Exception as e:
                            await bot.send_message(chat_id, f"Failed to download video {name}: {e}")
                            count += 1
                            failed_count += 1
                        await asyncio.sleep(1)
                        continue

                except FloodWait as e:
                    await bot.send_message(chat_id, f"FloodWait: {e}")
                    await asyncio.sleep(e.x)
                    count += 1
                    continue
                except Exception as e:
                    await bot.send_message(chat_id, f'⚠️**Downloading Failed**⚠️\n**ID** =>> `{str(count).zfill(3)}`\n\n**Name** - `{name1}`**', disable_web_page_preview=True)
                    count += 1
                    failed_count += 1
                    continue

            await bot.send_message(chat_id, f"⋅ ─ Total failed links is {failed_count} ─ ⋅")
            await bot.send_message(chat_id, f"⋅ ─ list index ({raw_text}-{len(links)}) out of range ─ ⋅\n\n✨ **BATCH** » {b_name}✨\n\n⋅ ─ DOWNLOADING ✩ COMPLETED ─ ⋅")
            del user_states[user_id]

        else:
            await bot.send_message(chat_id, f"Expected {state}, but received incorrect input.")
    except Exception as e:
        await bot.send_message(chat_id, f"Error: {e}")
        if user_id in user_states:
            del user_states[user_id]

bot.run()
