import re
import time
import requests
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
import io
from aiogram.types import BufferedInputFile
from config import OPENWEATHER_API_KEY, WEATHER_URL
from database.database import get_default_city, set_default_city, create_connection
from filters.filters import bot
from PIL import Image
from handlers.messages import description_mapping, weather_images
from keyboards.keyboards import inline_keyboard
from states.states import BotForm

router = Router()


async def start_handler(message: types.Message):
    image_path = 'assets/weather-bot-logo.png'
    user_id = message.from_user.id

    try:
        with Image.open(image_path) as img:
            img = img.resize((325, 325))
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)

        photo = BufferedInputFile(img_byte_arr.getvalue(), filename="weather-bot-logo.png")

        await message.answer_photo(
            photo=photo,
            caption=(
                "Привет! Я бот, который расскажет тебе о погоде.\n"
                "Выберите действие: \n\n"
                "Этот бот был создан с помощью [@DialogiusBot](tg://user?id=7605038110)"
            ).replace("!", "\\!").replace(".", "\\."),
            reply_markup=inline_keyboard(user_id=user_id),
            parse_mode='MarkdownV2'
        )

    except FileNotFoundError:
        print(f"Error: The file {image_path} was not found.")
        await bot.send_message(message.chat.id, "Извините, изображение не найдено.")
    except Exception as e:
        print(f"Error: {e}")
        await bot.send_message(message.chat.id, "Извините, произошла ошибка при загрузке изображения.")


@router.callback_query(lambda c: c.data in ["weather_in", "default_weather", "change_city"])
async def callback_query_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()

    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id

    conn = create_connection()
    cursor = conn.cursor()

    if callback_query.data == "weather_in":
        await bot.send_message(chat_id, 'Введите название города:')
        await state.set_state(BotForm.waiting_for_city.state)

    elif callback_query.data == "default_weather":
        city = get_default_city(user_id, cursor)
        if city:
            await send_weather_by_city(bot, callback_query.message, city, state)
        else:
            await bot.send_message(chat_id, "Введите город по умолчанию:")
            await state.set_state(BotForm.waiting_for_new_city.state)

    elif callback_query.data == "change_city":
        await bot.send_message(chat_id, 'Введите новый город по умолчанию:')
        await state.set_state(BotForm.waiting_for_new_city.state)

    cursor.close()
    conn.close()


@router.message(BotForm.waiting_for_city)
async def city_input_handler(message: types.Message, state: FSMContext):
    city = message.text
    await send_weather_by_city(bot, message, city, state)
    await state.clear()


@router.callback_query(lambda c: c.data == "default_weather")
async def default_weather_handler(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id

    await callback_query.answer()
    await bot.send_message(chat_id, 'Введите город по умолчанию:')
    await state.set_state(BotForm.waiting_for_new_city)


@router.message(BotForm.waiting_for_new_city)
async def new_city_input_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    city = message.text

    print(f"Setting new default city for user {user_id}: {city}")

    set_default_city(user_id, city)

    await message.answer(f'Город по умолчанию успешно установлен на {city}.')
    await state.clear()


def get_weather(city):
    print(f"Fetching weather data for: {city}")
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }

    print(f"Requesting URL: {WEATHER_URL} with params: {params}")

    for attempt in range(3):
        try:
            response = requests.get(WEATHER_URL, params=params, timeout=60)
            response.raise_for_status()
            if response.status_code == 200:
                data = response.json()
                weather = {
                    'city': data['name'],
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': data['wind']['speed'],
                    'clouds': data['clouds']['all'],
                }
                return weather
            else:
                print(f"Error: Received status code {response.status_code}")
                return None
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            return None
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
            time.sleep(5)
        except requests.exceptions.Timeout:
            print("Timeout occurred, retrying...")
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    print("Failed to get a response after multiple attempts.")
    return None


def normalize_description(description):
    normalized = re.sub(r'\s+', ' ', description).strip()
    return normalized.lower()


def escape_markdown_v2(text):
    special_characters = ["_", "*", "[", "]", "(", ")", "~", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special_characters:
        text = text.replace(char, f'\\{char}')
    return text


async def send_weather_by_city(bot, message, city, state: FSMContext):
    weather = get_weather(city)

    print(f"Weather data received: {weather}")

    if weather:
        weather_description = normalize_description(weather.get('description', ''))
        print(f"Normalized Weather Description: {weather_description}")

        mapped_description = description_mapping.get(weather_description.lower(), None)
        image_path = weather_images.get(mapped_description, None)

        response_message = escape_markdown_v2(
            (
                f"Погода в городе {weather.get('city')}:\n"
                f"Температура: {weather.get('temperature')}°C\n"
                f"Описание: {weather_description}\n"
                f"Влажность: {weather.get('humidity')}%\n"
                f"Давление: {weather.get('pressure')} мм рт. ст.\n"
                f"Скорость ветра: {weather.get('wind_speed')} м/с\n"
                f"Облачность: {weather.get('clouds')}%\n"
            )
        )

        if image_path:
            try:
                with Image.open(image_path) as img:
                    img = img.resize((200, 200))
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)

                    input_file = BufferedInputFile(img_byte_arr.getvalue(), filename="weather-bot-logo.png")

                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=input_file,
                        caption=response_message,
                        parse_mode='MarkdownV2'
                    )
            except Exception as e:
                print(f"Error sending image: {e}")
                await bot.send_message(message.chat.id, "Не удалось отправить изображение.")
        else:
            await bot.send_message(message.chat.id, response_message, parse_mode='MarkdownV2')
    else:
        response_message = 'Извините, я не смог найти информацию о погоде для этого города. Пожалуйста, введите название города снова:'
        await bot.send_message(message.chat.id, response_message)
        await state.set_state(BotForm.waiting_for_city)


def send_weather(message: types.Message):
    city = message.text
    send_weather_by_city(bot, message, city)
