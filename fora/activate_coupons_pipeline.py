import asyncio
from fora.utils import get_not_active_coupons
from fora.coupon import Coupon, set_coupons, get_personal_info


from logger import logging


async def retrieve_not_active_coupons():
    personal_info = await get_personal_info()
    personal_info_json = personal_info.json()
    not_active_coupons = get_not_active_coupons(personal_info_json)

    if not not_active_coupons:
        logging.info("No coupons to activate")
        return
    return not_active_coupons


async def activate_coupons(not_active_coupons):
    coupons = []
    for coupon in not_active_coupons:
        coupons.append(Coupon(id=coupon.get('businessCouponId'), is_off=False))

    coupons_response = await set_coupons(coupons)
    logging.info(f"Coupons {str(coupons)} activated")
    return coupons_response
    

async def main():
    not_active_coupons = await retrieve_not_active_coupons()
    if not not_active_coupons:
        return 
    return await activate_coupons(not_active_coupons)


if __name__ == '__main__':
    asyncio.run(main())