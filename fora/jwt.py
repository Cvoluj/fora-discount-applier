import base64
import json
from pprint import pprint
import time

def base64url_decode(input_str):
    padding = '=' * (-len(input_str) % 4)
    return base64.urlsafe_b64decode(input_str + padding)

def decode_jwt(token):
    header_b64, payload_b64, _ = token.split('.')
    
    header = json.loads(base64url_decode(header_b64))
    payload = json.loads(base64url_decode(payload_b64))
    
    return {
        'header': header,
        'payload': payload
    }

def is_expired(eit: int) -> bool:
    current_time = int(time.time())
    return int(eit) < current_time


if __name__ == '__main__':
    jwt_token = 'your.jwt.token'
    decoded = decode_jwt(jwt_token)
    pprint(decoded['payload'])  # or decoded['header']
