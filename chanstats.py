import re
import time
import random
import logging
import os
from tqdm import tqdm
import socks
from telethon.sync import TelegramClient
from telethon.errors import FloodWaitError, ChannelInvalidError, ChannelPrivateError
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetHistoryRequest

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===== Базовая директория (где лежит сам скрипт) =====
base_dir = os.path.dirname(os.path.abspath(__file__))

def load_config(file_name, separator=":"):
    file_path = os.path.join(base_dir, file_name)
    with open(file_path, "r", encoding="utf-8") as f:
        line = f.readline().strip()
        parts = line.split(separator)
        return [part.strip() for part in parts]

# ===== Конфигурация =====
api_id, api_hash = load_config("api_id_api_hash.txt")
api_id = int(api_id)
proxy_host, proxy_port, proxy_user, proxy_pass = load_config("proxy.txt")
proxy = (socks.SOCKS5, proxy_host, int(proxy_port), True, proxy_user, proxy_pass)
sheet_name, worksheet_name = load_config("sheet.txt")

google_json_keyfile = os.path.join(base_dir, 'projectyandexmess00001-1629a5334389.json')
input_file = os.path.join(base_dir, 'input.txt')
output_file = os.path.join(base_dir, 'output.txt')
log_file = os.path.join(base_dir, 'log.txt')

# ===== Логгирование =====
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s - %(message)s')

# ===== Google Sheets =====
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(google_json_keyfile, scope)
gclient = gspread.authorize(credentials)
sheet = gclient.open(sheet_name).worksheet(worksheet_name)

# ===== Запуск Telethon-клиента =====
session_file = os.path.join(base_dir, 'anon_proxy.session')
with TelegramClient(session_file, api_id, api_hash, proxy=proxy) as client:
    with open(input_file, 'r', encoding='utf-8') as f:
        links = [line.strip() for line in f if line.strip()]

    results = [["Название канала", "Ссылка", "Подписчики", "Просмотры"]]

    for link in tqdm(links, desc="Обработка каналов"):
        match = re.search(r't\.me/([^/]+)', link)
        if not match:
            logging.warning(f'Невалидная ссылка: {link}')
            results.append(["[НЕВАЛИДНАЯ ССЫЛКА]", link, "–", "–"])
            continue

        username = match.group(1)

        try:
            channel = client.get_entity(username)
            full = client(GetFullChannelRequest(channel))
            stats = full.full_chat
            name = channel.title
            subscribers = stats.participants_count

            history = client(GetHistoryRequest(
                peer=channel,
                limit=1,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))

            last_msg = history.messages[0] if history.messages else None
            views = last_msg.views if last_msg and last_msg.views is not None else 0

            results.append([name, link, subscribers, views])
            logging.info(f'✅ {name} | Подписчики: {subscribers} | Просмотры: {views}')

        except (ChannelPrivateError, ChannelInvalidError) as e:
            logging.error(f'🔒 Канал недоступен: {link} ({str(e)})')
            results.append(["[ПРИВАТНЫЙ/НЕСУЩ.]", link, "–", "–"])
        except FloodWaitError as e:
            logging.warning(f'⏳ FloodWait: пауза {e.seconds} сек...')
            time.sleep(e.seconds)
        except Exception as e:
            error_msg = str(e)
            logging.exception(f'❌ Ошибка для {link}: {error_msg}')
            results.append([f"[ОШИБКА: {error_msg[:30]}]", link, "–", "–"])
        finally:
            time.sleep(random.randint(1, 5))

    with open(output_file, 'w', encoding='utf-8') as f:
        for row in results[1:]:
            f.write(';'.join(str(x) for x in row) + '\n')

    sheet.clear()
    sheet.update(range_name='A1', values=results)

    logging.info('🎯 Готово! Данные записаны в Google Таблицу и в output.txt')
    print("✅ Скрипт завершён. Данные сохранены.")
