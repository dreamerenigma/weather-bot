from aiogram import Router, types
from aiogram.filters import Command
from ban_words import ban_words
from filters.filters import ProfanityFilter, handle_profanity
from handlers.bot_handlers import start_handler

router = Router()

profanity_filter = ProfanityFilter(ban_words)


async def start_command(message: types.Message):
    await start_handler(message)


async def help_command(message: types.Message):
    await start_handler(message)


def register_handlers_common(dp):
    router.message.register(start_command, Command(commands=["start"]))
    router.message.register(help_command, Command(commands=["help"]))
    router.message(profanity_filter)(handle_profanity)
    dp.include_router(router)
