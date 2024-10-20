from aiogram import Dispatcher
from filters.filters import register_handlers_filter
from handlers import common
from handlers.bot_handlers import router


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков команд и текстовых сообщений."""
    common.register_handlers_common(dp)
    register_handlers_filter(dp)
    dp.include_router(router)
