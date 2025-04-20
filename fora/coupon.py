from dataclasses import dataclass
import os
from copy import deepcopy
from dotenv import load_dotenv
from curl_cffi import AsyncSession, Response
from fora.utils import read_config, get_kyiv_time
load_dotenv()
config = read_config()


@dataclass
class Coupon:
    id: int
    is_off: bool = False

    def __repr__(self):
        return str(self.id)

coupon_headers = {
    'Host': 'api.mob.fora.ua',
    'Accept': 'application/json',
    'Authorization': None,
    'user-info': os.getenv("FORA_USER_INFO"),
    'masterPass-info': '{"MasterPassCardsCount":"0"}',
    'devicetime': None,
    'Cache-Control': 'no-cache',
    'Accept-Language': 'en-US;q=1.0, uk-UA;q=0.9, ru-UA;q=0.8',
    'User-Agent': 'Fora/1.73.5 (ua.fora.app; build:1; iOS 18.1.1) Alamofire/5.4.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
}

coupon_json_data = {
    'Method': 'SetCouponsToApply_V2',
    'Data': {
        'couponChangeItems': [
            # fill with coupons
        ],
    },
}


personal_info_headers = {
    'Host': 'api.mob.fora.ua',
    'Accept': 'application/json',
    'Authorization': None,
    'user-info': os.getenv("FORA_USER_INFO"),
    'masterPass-info': '{"MasterPassCardsCount":"0"}',
    'devicetime': None,
    'Cache-Control': 'no-cache',
    'Accept-Language': 'en-US;q=1.0, uk-UA;q=0.9, ru-UA;q=0.8',
    'User-Agent': 'Fora/1.73.5 (ua.fora.app; build:1; iOS 18.1.1) Alamofire/5.4.4',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
}

personal_info_json_data = {
    'Method': 'GetPersonalInfo_V6',
    'Data': {
        'forceUpdate': True,
    },
}


async def set_coupons(coupons: list[Coupon]) -> Response:
    deepcopy_json_data = deepcopy(coupon_json_data)
    deepcopy_headers = deepcopy(coupon_headers)

    deepcopy_headers['devicetime'] = get_kyiv_time()
    deepcopy_headers['Authorization'] = f'Token {config.get("fora_access_token")}'

    deepcopy_json_data['Data']['couponChangeItems'].extend([
        {"businessCouponId": coupon.id, "isOff": coupon.is_off}
        for coupon in coupons
    ])

    session = AsyncSession(headers=deepcopy_headers)
    return await session.post(
        "https://api.mob.fora.ua/api/2.0/exec/FZGlobal",
        json=deepcopy_json_data
    )

async def get_personal_info() -> Response:
    headers = deepcopy(personal_info_headers)
    headers['devicetime'] = get_kyiv_time()
    headers['Authorization'] = f'Token {config.get("fora_access_token")}'

    session = AsyncSession(headers=headers)
    return await session.post('https://api.mob.fora.ua/api/2.0/exec/FZGlobal', json=personal_info_json_data)
