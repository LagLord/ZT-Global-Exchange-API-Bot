import hashlib
import json
import time
import keyboard
import os, ssl
import requests

api_key = "abcd"
secretKey = "9000"

tick = ""
CRED = '\033[91m'
CGREEN = '\33[32m'
CEND = '\33[0m'


def sign(params):
    string = ""
    for key in params:
        string = string + key + "=" + str(params[key]) + "&"
    string = string + "secret_key=" + secretKey
    signature = hashlib.md5(string.encode('utf-8')).hexdigest().upper()
    print(signature)
    return signature


def get_complete_param(ticker, side=None, amount=None):
    if amount is None and side is None:
        params = {
            'amount': amount,
            'api_key': api_key,
            'market': ticker + '_USDT',
            'side': side,
        }
    else:
        params = {
            'api_key': api_key,
        }

    sign_ = sign(params)
    params["sign"] = sign_
    return params


def get_user_assets(ticker):
    param = get_complete_param(ticker=ticker)
    buy_url = "https://www.ztb.im/api/v1/private/user"
    res = requests.post(buy_url, params=param)
    response = json.loads(res.text)
    if response["code"] == 0:
        amount = response["result"][ticker]["available"]
        return amount
    else:
        get_user_assets(ticker)


def get_price(ticker):
    res = requests.get("https://www.ztb.im/api/v1/tickers")
    all_coins = json.loads(res.text)
    for coin in all_coins["ticker"]:
        if coin["symbol"] == ticker:
            # print(coin)
            return coin["buy"]


def ask_sell(ticker, amount, cost):
    while True:
        price = get_price(tick)
        change = (float(price) * amount) - cost
        print(f"Current Profit: {change} USD.\n"
              f"Would you like to sell your {amount} {ticker} coins?\nIf yes, press 'S' key for a few seconds.")

        if keyboard.is_pressed("s"):
            for i in range(0, 3):
                param = get_complete_param(ticker=ticker, amount=amount, side=1)
                buy_url = "https://www.ztb.im/api/v1/private/trade/market"
                res = requests.post(buy_url, params=param)
                response = json.loads(res.text)
                print(response)
                if response["code"] == 0:
                    print("Sold Successfully!")
                    return ask_buy()


def ask_buy(ticker=None, amount=None):
    global tick
    if ticker is None and amount is None:
        amount = input(f"How much would you like to buy?: ")
        ticker = input("Which coin would you like to buy?\n(Please provide the ticker eg. BTC, ETH): ").upper()

        tick = ticker + "_USDT"
        get_price(tick)

    param = get_complete_param(ticker=ticker, amount=amount, side=2)
    buy_url = "https://www.ztb.im/api/v1/private/trade/market"
    res = requests.post(buy_url, params=param)
    response = json.loads(res.text)
    # print(response)
    if response["code"] == 0:
        print(f"Bought Successfully!")
        cost = float(amount)
        ask_sell(ticker, get_user_assets(ticker), cost)

    else:
        print("Something went wrong!\nTrying...")
        ask_buy(ticker, amount)


# while True:
#         tick = "AVAX_USDT"
#         price = get_price(tick)
#         print(f"Current Price: {type(price)}\nIf yes, press 'S' key.")
#
#         if keyboard.is_pressed("s"):
#             print("PRESSED!")
#             break

ask_buy()
