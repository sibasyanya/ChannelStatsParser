# Telegram Channel Stats Parser 📊

Скрипт на Python для парсинга публичных Telegram-каналов. Парсит количество подписчиков и просмотры последнего поста.
Поддерживает работу через SOCKS5-прокси и экспортирует данные в Google Таблицу. Особенно полезен для владельцев сетей дорвей-каналов с единственной публикацией.

---

## 🚀 Возможности

- Подключение через SOCKS5-прокси
- Авторизация через Telethon (с сохранением сессии)
- Парсинг публичных каналов по ссылкам
- Случайная задержка между запросами (1–5 сек)
- Обработка ошибок и приватных каналов
- Прогресс-бар (`tqdm`)
- Логгирование в `log.txt`
- Экспорт:
  - `output.txt` — локально
  - Google Sheets — с перезаписью листа

---

## 🧩 Установка

```bash
pip install telethon pysocks tqdm gspread oauth2client
```

---

## 🛠 Подготовка

1. Получите `api_id` и `api_hash`:  
   👉 https://my.telegram.org

2. Включите Google Sheets API:  
   👉 https://console.cloud.google.com/

3. Создайте сервисный аккаунт и JSON-файл (`google_creds.json`)  
   👉 Дайте доступ к Google Таблице (как редактор)

4. Скопируйте конфигурационные шаблоны и укажите свои данные:

```bash
cp api_id_api_hash.example.txt api_id_api_hash.txt
cp proxy.example.txt proxy.txt
cp sheet.example.txt sheet.txt
cp input.example.txt input.txt
```

---

## 📦 Использование

1. Укажите ссылки на каналы в `input.txt`, по одной на строку:

```
https://t.me/example_channel
https://t.me/example_channel2
```

2. Запустите скрипт:

```bash
python chanstats.py
```

---

## 📁 Вывод

- `output.txt` — текстовый файл с результатами
- `log.txt` — лог ошибок и процесса
- Google Таблица — с теми же данными (заголовки + замена старых строк)
- anon_proxy.session — сохраненная сессия авторизации в Telegram

---

## 📄 Лицензия

MIT License
