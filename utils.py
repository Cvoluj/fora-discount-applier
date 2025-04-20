import os
import json
from dotenv import load_dotenv
load_dotenv()
USER_DATA_FILE = os.getenv("USER_DATA_FILE")


def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


async def check_auth(message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    if user_id not in user_data or not user_data[user_id].get("authenticated", False):
        await message.reply("You are not authenticated. Please start with /start.")
        return False
    return True