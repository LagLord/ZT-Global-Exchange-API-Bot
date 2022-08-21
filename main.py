import hashlib
import json
import time
import keyboard
import websocket
import rel
import os, ssl
import requests

api_key = "abcd"
secretKey = "9000"

tick = ""


def sign(params):
    string = ""
    for key in params:
        string = string + key + "=" + str(params[key]) + "&"
    string = string + "secret_key=" + secretKey
    signature = hashlib.md5(string.encode('utf-8')).hexdigest().upper()
    print(signature)
    return signature


def get_complete_param(amount, ticker, side):
    params = {
        'amount': amount,
        'api_key': api_key,
        'market': ticker + '_USDT',
        'side': side,
    }

    sign_ = sign(params)
    params["sign"] = sign_
    return params


def get_price(ticker):
    res = requests.get("https://www.ztb.im/api/v1/tickers")
    all_coins = json.loads(res.text)
    for coin in all_coins["ticker"]:
        if coin["symbol"] == ticker:
            print(coin)
            return coin["buy"]


def ask_sell(ticker, amount, cost):
    while True:
        price = get_price(tick)
        print(f"Current Profit: {(float(price) * amount) - cost} USD\n"
              f"Would you like to sell your {amount} {ticker} coins?\nIf yes, press 'S' key for a few seconds.")

        if keyboard.is_pressed("s"):
            for i in range(0, 3):
                param = get_complete_param(ticker=ticker, amount=amount, side=1)
                buy_url = "https://www.ztb.im/api/v1/private/trade/market"
                res = requests.post(buy_url, params=param)
                response = json.load(res.text)
                if response["code"] == 0:
                    print("Sold Successfully!")
                    return ask_buy()


def ask_buy(ticker=None, amount=None):
    if ticker is None and amount is None:
        ticker = input("Which coin would you like to buy?\n(Please provide the ticker eg. BTC, ETH): ").upper()
        global tick
        tick = ticker + "_USDT"
        get_price(tick)
        amount = input("How much would you like to buy?: ")

    param = get_complete_param(ticker=ticker, amount=amount, side=2)
    buy_url = "https://www.ztb.im/api/v1/private/trade/market"
    res = requests.post(buy_url, params=param)
    response = json.loads(res.text)
    if response["code"] == 0:
        print("Bought Successfully!")
        cost = float(response["result"]["price"]) * float(amount)
        ask_sell(ticker, amount, cost)

    else:
        print("Something went wrong!\nTrying...")
        ask_buy(ticker, amount)


# while True:
#         price = get_price(tick)
#         print(f"Current Profit:scoins?\nIf yes, press 'S' key.")
#
#         if keyboard.is_pressed("s"):
#             print("PRESSED!")
#             break

ask_buy()
