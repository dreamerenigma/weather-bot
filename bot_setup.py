from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from middleware.middleware import ResetStateMiddleware
from register_handlers import register_handlers


def create_bot():
    """Создаем бота Telegram и возвращаем его вместе с VK API клиентом"""
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot


def create_dispatcher():
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage, middlewares=[ResetStateMiddleware()])
    register_handlers(dispatcher)
    return dispatcher
