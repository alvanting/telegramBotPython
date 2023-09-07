import random
import urllib
import hashlib

import telebot
import requests

# 创建Telegram bot对象
bot = telebot.TeleBot('6316125267:AAFVViglW41nbjZX56cUtyHwBM18-viDNLQ')

is_running = False


@bot.message_handler(commands=['start'])
def start(message):
    global is_running
    if not is_running:
        is_running = True
        response = "成功启动 GLOPayBot"
        bot.send_message(chat_id=message.chat.id, text=response)
    else:
        response = "GLOPayBot 已经在运行中"
        bot.send_message(chat_id=message.chat.id, text=response)


@bot.message_handler(commands=['end'])
def end(message):
    global is_running
    if is_running:
        is_running = False
        response = "成功结束 GLOPayBot"
        bot.send_message(chat_id=message.chat.id, text=response)
    else:
        response = "GLOPayBot 未在运行中"
        bot.send_message(chat_id=message.chat.id, text=response)


@bot.message_handler(commands=['payin'])
def payin(message):
    if not is_running:
        response = "GLOPayBot 未在运行中"
        bot.send_message(chat_id=message.chat.id, text=response)
        return

    command_parts = message.text.split()[1:]
    if len(command_parts) > 0:
        agent_order_id = command_parts[0]

        payin_response = call_payin_post_api(agent_order_id)

        if payin_response.get("version") is None:
            response = "请核实订单号"
        else:
            agent_order_id = payin_response["agentOrderId"]
            jnet_order_id = payin_response["jnetOrderId"]
            pay_amt = payin_response["payAmt"]
            pay_result = payin_response["payResult"]
            response = "商户订单号: {}\n我方订单号: {}\n实际支付金额: {}\n订单结果: {}".format(
                agent_order_id, jnet_order_id, pay_amt, pay_result)
    else:
        response = "请输入 /payin {你的订单号}"

    bot.send_message(chat_id=message.chat.id, text=response)


def call_payin_post_api(agent_order_id):
    version = "1.0"
    agentId = "test03"
    key = "91738ecdb3f02865e988f39263587ad5"

    sign_string = f"{version}|{agentId}|{agent_order_id}|{key}"
    sign = hashlib.md5(sign_string.encode()).hexdigest()

    request = {
        "version": version,
        "agentId": agentId,
        "agentOrderId": agent_order_id,
        "sign": sign
    }

    api_url = "https://ndP1DAb.easy-game.vip/gateway/query/"

    url_params = urllib.parse.urlencode(request)
    url = api_url + "?" + url_params

    try:
        response = requests.get(url).json()
    except requests.exceptions.RequestException as e:
        print("API request failed:", str(e))
        response = {
            "agentOrderId": None,
            "payMessage": None
        }

    return response


@bot.message_handler(commands=['payout'])
def payout(message):
    if not is_running:
        response = "GLOPayBot 未在运行中"
        bot.send_message(chat_id=message.chat.id, text=response)
        return

    command_parts = message.text.split()[1:]
    if len(command_parts) > 0:
        agent_order_id = command_parts[0]

        payout_response = call_payout_post_api(agent_order_id)

        if payout_response.get("version") is None:
            response = "请核实订单号"
        else:
            agent_order_id = payout_response["agentOrderId"]
            amount = payout_response["amount"]
            payee_result = payout_response["payeeResult"]
            payee_name = payout_response["payeeName"]
            payee_account = payout_response["payeeAccount"]
            response = "商户订单号: {}\n付款金额: {}\n订单结果: {}\n收款人姓名: {}\n收款人账号: {}".format(
                agent_order_id, amount, payee_result, payee_name, payee_account)
    else:
        response = "请输入 /payout {你的订单号}"

    bot.send_message(chat_id=message.chat.id, text=response)


def call_payout_post_api(agent_order_id):
    version = "1.0"
    agentId = "test03"
    key = "91738ecdb3f02865e988f39263587ad5"

    sign_string = f"{version}|{agentId}|{agent_order_id}|{key}"
    sign = hashlib.md5(sign_string.encode()).hexdigest()

    request = {
        "version": version,
        "agentId": agentId,
        "agentOrderId": agent_order_id,
        "sign": sign
    }

    api_url = "https://ndP1DAb.easy-game.vip/withdraw/query/"

    url_params = urllib.parse.urlencode(request)
    url = api_url + "?" + url_params

    try:
        response = requests.get(url).json()
    except requests.exceptions.RequestException as e:
        print("API request failed:", str(e))
        response = {
            "agentOrderId": None,
            "payoutAmt": None,
            "payoutResult": None
        }

    return response


@bot.message_handler(commands=['balance'])
def balance(message):
    if not is_running:
        response = "GLOPayBot 未在运行中"
        bot.send_message(chat_id=message.chat.id, text=response)
        return

    balance_response = call_balance_post_api()

    if balance_response.get("retCode") != "0000":
        response = "请核实订单号"
    else:
        available_balance = balance_response["availableBalance"]
        balance = balance_response["balance"]
        response = "可用余额: {}\n余额: {}".format(available_balance, balance)

    bot.send_message(chat_id=message.chat.id, text=response)


@bot.message_handler(func=lambda message: True)
def unknown_command(message):
    response = "请输入正确指令"
    bot.send_message(chat_id=message.chat.id, text=response)


def call_balance_post_api():
    version = "1.0"
    agentId = "test03"
    key = "91738ecdb3f02865e988f39263587ad5"

    random_num = str(random.randint(0, 9999999999999999)).zfill(16)
    sign_string = f"{version}|{agentId}|{random_num}|{key}"
    sign = hashlib.md5(sign_string.encode()).hexdigest()

    request = {
        "version": version,
        "agentId": agentId,
        "random": random_num,
        "sign": sign
    }

    api_url = "https://ndP1DAb.easy-game.vip/withdraw/balanceQuery/"

    url_params = urllib.parse.urlencode(request)
    url = api_url + "?" + url_params

    try:
        response = requests.get(url).json()
    except requests.exceptions.RequestException as e:
        print("API request failed:", str(e))
        response = {
            "balanceAmt": None
        }

    return response


if __name__ == '__main__':
    bot.polling()
