import os
from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv


from formatter import format_coupon_html
from fora.coupon import get_personal_info
from fora.utils import read_config, save_to_json_file
from utils import check_auth, load_user_data, save_user_data
from fora.activate_coupons_pipeline import retrieve_not_active_coupons, activate_coupons
load_dotenv()


bot = Bot(token=os.getenv("TELEGRAM_API_KEY"))
dp = Dispatcher()


user_expecting_password = {}
user_expecting_token = {}
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Set Token"), KeyboardButton(text="Activate Coupons")]
    ],
    resize_keyboard=True
)


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id in user_data and user_data[user_id].get("blocked", False):
        await message.reply("You are blocked due to too many failed attempts.")
        return

    user_data[user_id] = {"attempts": 0, "authenticated": False, "blocked": False}
    save_user_data(user_data)
    user_expecting_password[user_id] = True
    await message.reply("Welcome! Please enter the password to continue. You have 3 attempts.")


async def check_password(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()

    if user_id not in user_data:
        await message.reply("Please start the bot with /start.")
        return
    
    if user_expecting_password.get(user_id) is not True:
        await message.reply("Please start the bot with /start.")

    if user_data[user_id].get("blocked", False):
        await message.reply("You are blocked due to too many failed attempts.")
        return

    if user_data[user_id].get("authenticated", False):
        return

    if message.text == read_config()['password']:
        user_data[user_id]["authenticated"] = True
        user_data[user_id]["attempts"] = 0
        del user_expecting_password[user_id]
        save_user_data(user_data)
        await message.reply("Password correct! You can now use bot.", reply_markup=keyboard)
    else:
        user_data[user_id]["attempts"] += 1
        if user_data[user_id]["attempts"] >= 3:
            user_data[user_id]["blocked"] = True
            await message.reply("You have exceeded the number of attempts. You are now blocked.")
        else:
            attempts_left = 3 - user_data[user_id]["attempts"]
            await message.reply(f"Incorrect password. {attempts_left} attempts left.")
        save_user_data(user_data)

async def check_token(message: types.Message):
    user_id = str(message.from_user.id)

    if len(message.text) > 50 and "." in message.text:
        save_to_json_file("config.json", "fora_access_token", message.text)
        await message.answer("Token saved successfully!", reply_markup=keyboard)
    else:
        await message.answer("Please use the buttons below:", reply_markup=keyboard)
    del user_expecting_token[user_id]

@dp.message(F.text == "Set Token")
async def set_token(message: types.Message):
    is_auth = await check_auth(message)
    if not is_auth:
        return

    user_id = str(message.from_user.id)
    user_expecting_token[user_id] = True
    await message.answer("Please send me your JWT token. I'll store it for future use.")

async def send_coupons(message: types.Message, coupons: list):
    coupons_formatted = list(map(
        format_coupon_html,
        coupons
    ))
    coupons_formatted = "\n".join(coupons_formatted)

    await message.answer(
        text=coupons_formatted,
        parse_mode='HTML',
        disable_web_page_preview=False  # Ensures image shows
    )

@dp.message(F.text == "Activate Coupons")
async def activate_coupons_handler(message: types.Message):
    is_auth = await check_auth(message)
    if not is_auth:
        return
    
    if not read_config().get("fora_access_token"):
        await message.answer("Please set your token first using the 'Set Token' button.")
        return
    
    try:
        not_active_coupons = await retrieve_not_active_coupons()
        if not not_active_coupons:
            await message.answer("All coupons already activated")
        else:
            await activate_coupons(not_active_coupons)
        
        personal_info = await get_personal_info()
        await send_coupons(message, personal_info.json()['personalInfo']['Coupons'][0]['activCoupons'])
    except Exception as e:
        await message.answer(f"Error activating coupons: {str(e)}")

@dp.message(F.text)
async def handle_text_messages(message: types.Message):
    user_id = str(message.from_user.id)    
    if user_id in user_expecting_password.keys():
        await check_password(message)
        return
    

    is_auth = await check_auth(message)
    if not is_auth:
        return

    if user_id in user_expecting_token.keys():
        await check_token(message)
        return
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
