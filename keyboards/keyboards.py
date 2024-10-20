from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.database import create_connection, get_default_city


def inline_keyboard(user_id):
    conn = create_connection()
    cursor = conn.cursor()

    default_city = get_default_city(user_id, cursor)

    cursor.close()
    conn.close()

    if default_city:
        default_weather_text = f"Погода в городе: {default_city}"
    else:
        default_weather_text = "Погода в городе по умолчанию"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Погода в...", callback_data="weather_in")],
            [InlineKeyboardButton(text=default_weather_text, callback_data="default_weather")],
            [InlineKeyboardButton(text="Изменить город по умолчанию", callback_data="change_city")]
        ]
    )
    return keyboard
