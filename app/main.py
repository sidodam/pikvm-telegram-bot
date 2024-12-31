import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from token_api import TOKEN, PIKVM_URL, USER, PASSWORD, USER_ID

bot = Bot(token=TOKEN)
dispatcher = Dispatcher()



AUTHORIZED_USERS = [USER_ID]

def is_authorized(user_id):
    """Check if the user is authorized."""
    return user_id in AUTHORIZED_USERS


async def check_authorization(msg: types.Message):
    """Middleware to check if the user is authorized."""
    if not is_authorized(msg.from_user.id):
        print(msg.from_user.id)

        await bot.send_message(
            chat_id=USER_ID,
            text=f"⚠️ Unauthorized access attempt by User ID: {msg.from_user.id}"
        )
        #await msg.reply("uNauthorized.".upper())
        return False
    return True




async def send_request(endpoint, method="GET", params=None):


    url = f"{PIKVM_URL}{endpoint}"
    headers = {
        "X-KVMD-User": USER,
        "X-KVMD-Passwd": PASSWORD
    }

    try:
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers, ssl=False, params=params) as response:
                    response_text = await response.text()
                    response_status = response.status
            elif method == "POST":
                async with session.post(url, headers=headers, ssl=False, params=params) as response:
                    response_text = await response.text()
                    response_status = response.status

            print(f"Request URL: {url}")
            print(f"Headers sent: {headers}")
            print(f"Response Status Code: {response_status}")
            print(f"Response Text: {response_text}")

            if response_status == 200:
                return await response.json()
            else:
                print(f"Failed request. Status code: {response_status}")
                print(f"Response headers: {dict(response.headers)}")
                return {"error": f"HTTP {response_status}"}

    except Exception as e:
        print(f"Error occurred: {e}")
        return {"error": str(e)}

@dispatcher.message(Command("start"))
async def cmd_start(msg: types.Message):

    if not await check_authorization(msg):
        return
    """Handle /start command."""
    reply_text = (
        "/atx_state - Get ATX power state\n\n"
        "/click_power - Short power button press\n\n"
        "/click_long_power - Long power button press\n\n"
        "/click_reset - Reset button press"
    )
    await msg.answer(reply_text)

@dispatcher.message(Command("click_power"))
async def cmd_power_click(msg: types.Message):
    if not await check_authorization(msg):
        return
    """Handle short power button press command."""
    endpoint = "atx/click"
    params = {
        "button": "power",
        "wait": "1"
    }

    result = await send_request(endpoint, method="POST", params=params)

    if isinstance(result, dict) and not result.get("error"):
        reply_text = "Power button clicked successfully."
    else:
        reply_text = f"Failed to click power button. Error: {result}"

    await msg.answer(reply_text)

@dispatcher.message(Command("click_long_power"))
async def cmd_long_power_click(msg: types.Message):
    if not await check_authorization(msg):
        return
    """Handle long power button press command."""
    endpoint = "atx/click"
    params = {
        "button": "power_long",
        "wait": "1"
    }

    result = await send_request(endpoint, method="POST", params=params)

    if isinstance(result, dict) and not result.get("error"):
        reply_text = "Long power button press executed successfully."
    else:
        reply_text = f"Failed to execute long power button press. Error: {result}"

    await msg.answer(reply_text)

@dispatcher.message(Command("click_reset"))
async def cmd_reset_click(msg: types.Message):
    if not await check_authorization(msg):
        return
    """Handle reset button press command."""
    endpoint = "atx/click"
    params = {
        "button": "reset",
        "wait": "1"
    }

    result = await send_request(endpoint, method="POST", params=params)

    if isinstance(result, dict) and not result.get("error"):
        reply_text = "Reset button pressed successfully."
    else:
        reply_text = f"Failed to press reset button. Error: {result}"

    await msg.answer(reply_text)

@dispatcher.message(Command("atx_state"))
async def cmd_atx_state(msg: types.Message):
    if not await check_authorization(msg):
        return
    endpoint = "atx"
    result = await send_request(endpoint)
    print(result)  # debug

    if isinstance(result, dict) and result.get("ok") and "result" in result:
        # Extract state from the nested 'result' dictionary
        power_led = result["result"].get("leds", {}).get("power", False)

        power_state = "ON" if power_led else "OFF"

        reply_text = f"PC Power: {power_state}"
    else:
        reply_text = f"Failed to get ATX state. Error: {result}"

    await msg.answer(reply_text)


async def main():
    # Delete the webhook to skip pending updates
    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())