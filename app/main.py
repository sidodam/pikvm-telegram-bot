import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from token_api import TOKEN , PIKVM_URL , USER , PASSWORD



bot = Bot(token=TOKEN)
dispatcher = Dispatcher()


def send_request(endpoint, method="GET", params=None):
    global response
    url = f"{PIKVM_URL}{endpoint}"
    headers = {
        "X-KVMD-User": USER,
        "X-KVMD-Passwd": PASSWORD
    }

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, verify=False, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, verify=False, params=params)

        print(f"Request URL: {url}")
        print(f"Headers sent: {headers}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed request. Status code: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            return {"error": f"HTTP {response.status_code}"}

    except Exception as e:
        print(f"Error occurred: {e}")
        return {"error": str(e)}


@dispatcher.message(Command("start"))
async def cmd_start(msg: types.Message):
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
    """Handle short power button press command."""
    endpoint = "atx/click"
    params = {
        "button": "power",
        "wait": "1"
    }

    result = send_request(endpoint, method="POST", params=params)

    if isinstance(result, dict) and not result.get("error"):
        reply_text = "Power button clicked successfully."
    else:
        reply_text = f"Failed to click power button. Error: {result}"

    await msg.answer(reply_text)


@dispatcher.message(Command("click_long_power"))
async def cmd_long_power_click(msg: types.Message):
    """Handle long power button press command."""
    endpoint = "atx/click"
    params = {
        "button": "power_long",
        "wait": "1"
    }

    result = send_request(endpoint, method="POST", params=params)

    if isinstance(result, dict) and not result.get("error"):
        reply_text = "Long power button press executed successfully."
    else:
        reply_text = f"Failed to execute long power button press. Error: {result}"

    await msg.answer(reply_text)


@dispatcher.message(Command("click_reset"))
async def cmd_reset_click(msg: types.Message):
    """Handle reset button press command."""
    endpoint = "atx/click"
    params = {
        "button": "reset",
        "wait": "1"
    }

    result = send_request(endpoint, method="POST", params=params)

    if isinstance(result, dict) and not result.get("error"):
        reply_text = "Reset button pressed successfully."
    else:
        reply_text = f"Failed to press reset button. Error: {result}"

    await msg.answer(reply_text)


@dispatcher.message(Command("atx_state"))
async def cmd_atx_state(msg: types.Message):
    endpoint = "atx"
    result = send_request(endpoint)
    print(result) # debug

    if isinstance(result, dict) and result.get("ok") and "result" in result:
        # Extract state from the nested 'result' dictionary
        power_led = result["result"].get("leds", {}).get("power", False)

        power_state = "ON" if power_led else "OFF"

        reply_text = f"PC Power: {power_state}"
    else:
        reply_text = f"Failed to get ATX state. Error: {result}"

    await msg.answer(reply_text)



async def main():
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())