from decouple import config

ADMIN_ID = config("ADMIN_ID")
BOT_TOKEN = config("BOT_TOKEN")
OPENWEATHER_API_KEY = config("OPENWEATHER_API_KEY")
WEATHER_URL = config("WEATHER_URL")
HOST = config("HOST")
PORT = int(config("PORT"))
BASE_URL = config("BASE_URL")
WEBHOOK_PATH = f'/{BOT_TOKEN}'
ENVIRONMENT = config("ENVIRONMENT", "development")
USE_WEBHOOK = config("USE_WEBHOOK", cast=bool, default=False)
