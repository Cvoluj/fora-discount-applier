from aiogram.utils.markdown import html_decoration as hd


def format_coupon_html(coupon: dict) -> str:
    reward = coupon['rewardText']
    if reward:
        reward_text = f"<b>🏆 Винагорода:</b> <code>{coupon['rewardText']}</code>\n"
    else:
        reward_text = ""
    return (
        f"<b>🎯 Акція:</b> <i>{coupon['couponDescription']}</i>\n{reward_text}"
    )