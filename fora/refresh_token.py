import os
from copy import deepcopy
from dotenv import load_dotenv
from curl_cffi import AsyncSession


from fora.jwt import decode_jwt, is_expired
from fora.utils import get_kyiv_time, read_config, save_to_json_file
from logger import logging
load_dotenv()


jwt_headers = {
    'Host': 'api.mob.fora.ua',
    'Accept': 'application/json',
    'Authorization': None,
    'user-info': os.getenv("FORA_USER_INFO"),
    'masterPass-info': '{"MasterPassCardsCount":"0"}',
    'Accept-Language': 'en-US;q=1.0, uk-UA;q=0.9, ru-UA;q=0.8',
    'devicetime': None,
    'User-Agent': 'Fora/1.73.5 (ua.fora.app; build:1; iOS 18.1.1) Alamofire/5.4.4',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/json',
}

jwt_json_data = {
    'Data': {},
    'Method': 'RefreshToken',
}

async def safe_refresh_token(current_access_token, current_refresh_token):
    is_access_expired = is_expired(decode_jwt(current_access_token)['payload']['exp'])
    is_refresh_expired = is_expired(decode_jwt(current_refresh_token)['payload']['exp'])

    if not is_access_expired:
        logging.info("Access token not expired")
        return {
            "is_access_expired": is_access_expired,
            "is_refresh_expired": is_refresh_expired
        }    

    headers = deepcopy(jwt_headers)
    headers['Authorization'] = f"Token {current_refresh_token}"
    headers['devicetime'] = get_kyiv_time()
    
    logging.info("Access Token renewal")
    session = AsyncSession(headers=headers)
    response = await session.post(
        'https://api.mob.fora.ua/api/2.0/exec/FZGlobal',
        json=jwt_json_data
    )
    response_json = response.json()
    access_token = response_json['tokens']['accessToken']['value']
    refresh_token = response_json['tokens']['refreshToken']['value']

    save_to_json_file(
        "config.json",
        "fora_access_token",
        access_token
    )
    save_to_json_file(
        "config.json",
        "fora_refresh_token",
        refresh_token
    )
    
    return {
        "response": response.json(),
        "is_access_expired": is_access_expired,
        "is_refresh_expired": is_refresh_expired
    }


if __name__ == '__main__':
    import asyncio
    asyncio.run(safe_refresh_token(read_config()['fora_access_token'], read_config()['fora_refresh_token']))
