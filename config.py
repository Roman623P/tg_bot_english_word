import os

from dotenv import load_dotenv

dotenv_path = 'D:/Study/University/Cross-platform software tools/Telegram_bot_2/.env'
load_dotenv(dotenv_path)

# Bot and server config
API_TOKEN = os.environ.get('API_TOKEN')
WEB_HOOK_URL = os.environ.get('WEB_HOOK_URL')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{API_TOKEN}'
APP_PORT = os.environ.get('APP_PORT')
APP_HOST = os.environ.get('APP_HOST')

# Database config
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
