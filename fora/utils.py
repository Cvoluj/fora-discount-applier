import json
import os
import pytz
from datetime import datetime
kyiv_tz = pytz.timezone('Europe/Kyiv')


def get_not_active_coupons(response):
    return [coupon for coupon in response['personalInfo']['Coupons'][0]['activCoupons'] if coupon.get('isOff') == 1]


def read_config():
    with open("config.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_kyiv_time():
    kyiv_now = datetime.now(kyiv_tz)
    return kyiv_now.strftime('%Y-%m-%dT%H:%M:%SZ')


def read_json_file(file):
    if os.path.exists(file):
        with open(file, 'r') as file:
            return json.load(file)
    return None


def save_to_json_file(filename, key, value):
    data = read_json_file(filename)
    print(data)
    data[key] = value
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == '__main__':
    print(get_kyiv_time())