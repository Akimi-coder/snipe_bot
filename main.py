import json

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client
from telebot import types
import config
import wallet
from dbhelper import DBHelper
import pickle
from bip_utils import Bip44Coins
from telebot import util
from telebot import types
from telebot.async_telebot import AsyncTeleBot
import asyncio
from telebot.states.asyncio.context import StateContext
from telebot.states import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage
from telebot import async_telebot, asyncio_filters, types
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import requests
import time
from datetime import datetime
from account import Account,Token
from saver import read_accounts_excel,save_accounts_exel

snipe_accounts = [Account("TAtXnRm1ucJX6qtNepe5AVETZj1EMVAzgp"),Account("TDjz1ejk5UvJYf4Pr4WyF8cbX92kf4J91Q"),Account("TQDqbryLfMQX7H7Cbk7S923Z3oh74QBUkm"),Account("TC9uWfp4EqrgueUdLucRsA2JKRvFgUg7Ry"),
                  Account("TLKeRosFeG2ABA6Jj8xAY1JoRV5VLa2HHB"),Account("TQxFaKhto3xCmAkLGEoA9o6eDZv6u2CnsT"),Account("THAWBpfdhtDZFXMr1z3YDRiPz6NhWcisEC",favorite="Yes"),Account("TE4G5PA9LihNn9q2B7roJ27psYex9DwKQw"),
                  Account("TXygjTCv67v9HjwDATqWr3ZqrYibezNj3X"),Account("TCbRSgCRvQaVPeYf7aUo8P1Jt31akrKK6p"),Account("TNVijKu7sN26jRwffHdCv7qe9JJndRpjNP")]


accounts_address = ["TDjz1ejk5UvJYf4Pr4WyF8cbX92kf4J91Q","TJcfSYBEeFUCNNnf3umjk88XnbKDGBEnf8","TQDqbryLfMQX7H7Cbk7S923Z3oh74QBUkm",]
last_transaction = []

state_storage = StateMemoryStorage()
bot = AsyncTeleBot(config.TOKEN,state_storage=state_storage)
db = DBHelper()

api_id = 25724955
api_hash = 'b3f2846720a10ad68b5bf5d68d8b71b0'
app = Client("me_client", api_id, api_hash)

class MyStates(StatesGroup):
    channel_username = State()

def format_price(price):
    formatted_price = f"{price:.8f}"
    formatted_price = formatted_price.rstrip('0').rstrip('.')
    return formatted_price

async def get_price(token,address):
    response = requests.get(f"https://api-v2.sunpump.meme/pump-api/token/{token}")
    price_json = response.json()
    price = float(format_price(price_json["data"]["priceInTrx"]))
    print(f"{address}:{token} {price}")
    return price

@bot.message_handler(commands=['start'])
async def start_command(message,state: StateContext):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Create solana wallet", callback_data="create_solana_wallet"))
    db.setup()
    await bot.send_message(
        message.chat.id,
        'Hello, this is a fast swap crypto bot\n\nCreate wallet to continue...',
        reply_markup=keyboard,
    )

@bot.message_handler(commands=['show'])
async def show_command(message,state: StateContext):
    for account in snipe_accounts:
        await bot.send_message(
            message.chat.id,
            f"{account.address}:",
        )
        for token in account.tokens:
            price = await get_price(token.address,account.address)
            token.current_price = price
            profit_percent = ((token.current_price - token.buy_price) / token.buy_price) * 100
            token.percent = profit_percent
            await bot.send_message(
                message.chat.id,
                f"{token.address}: |{format_price(token.current_price)}| |{profit_percent}|",
            )

@bot.message_handler(commands=['show_balance'])
async def show_command(message,state: StateContext):
    for account in snipe_accounts:
        await bot.send_message(
            message.chat.id,
            f"{account.address}: {account.balance}",
        )


async def has_token_info(message,type,transaction,address):
    if not transaction["token_info"]:
        time = datetime.fromtimestamp(transaction["block_timestamp"] / 1000).strftime(
            '%H:%M:%S')
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"In {time} {type}| {address} |\n"
                 f"https://tronscan.org/#/transaction/{transaction["transaction_id"]}/internal-transactions")
        return False
    else:
        return True

async def snipe_address(message):
    for account in snipe_accounts:
        url = f'https://api.trongrid.io/v1/accounts/{account.address}/transactions/trc20'
        params = {
            'limit': 1,
        }
        response = requests.get(url, params=params)
        transactions_array = response.json()['data']
        for transaction in transactions_array:
            if not transaction in last_transaction:
                last_transaction.append(transaction)
                if transaction['type'] == "Transfer":
                    if transaction["from"] == account.address:
                        if await has_token_info(message, "SELL", transaction,account.address):
                            token = Token(transaction["token_info"]["address"])
                            if token in account.tokens:
                                f_token = account.find_token(transaction["token_info"]["address"])
                                f_token.buy_time = datetime.fromtimestamp(
                                    transaction["block_timestamp"] / 1000).strftime(
                                    '%H:%M:%S')
                                price = await get_price(f_token.address,account.address)
                                f_token.current_price = price
                                value = (int(transaction["value"]) / (10 ** int(transaction["token_info"]["decimals"])))
                                if value > f_token.value:
                                    value = f_token.value
                                value_price = value * f_token.current_price
                                account.balance += value_price
                                account.remove_token(f_token)
                                await bot.send_message(
                                    chat_id=message.chat.id,
                                    text=f"In {f_token.buy_time}| {account.address} |:SELL {transaction["token_info"]} {price} | {transaction["value"]} | for {value_price} TRX")
                    else:
                        if await has_token_info(message, "BUY", transaction,account.address):
                            address = transaction["token_info"]["address"]
                            price = await get_price(address,account.address)
                            token = Token(address)
                            b_time = datetime.fromtimestamp(transaction["block_timestamp"] / 1000).strftime(
                                '%H:%M:%S')
                            if not token in account.tokens:
                                token.buy_time = b_time
                                token.buy_price = price
                                token.value = int(transaction["value"]) / (
                                            10 ** int(transaction["token_info"]["decimals"]))
                                value_price = token.value * token.buy_price
                                account.balance -= value_price
                                account.tokens.append(token)
                                address = account.address
                                if account.favorite == "Yes":
                                    address = f"<b>{account.address}</b>"
                                await bot.send_message(
                                    chat_id=message.chat.id,
                                    text=f"In {token.buy_time}| {address} |:BUY {transaction["token_info"]} {price} | {transaction["value"]} | for {value_price} TRX")
                            else:
                                f_token = account.find_token(transaction["token_info"]["address"])
                                f_token.buy_time = b_time
                                f_token.buy_price = (f_token.buy_price + price) / 2
                                value = int(transaction["value"]) / (10 ** int(transaction["token_info"]["decimals"]))
                                f_token.value += value
                                value_price = value * price
                                account.balance -= value_price
                                await bot.send_message(
                                    chat_id=message.chat.id,
                                    text=f"In {f_token.buy_time}| {account.address} |:BUY {transaction["token_info"]} {price} | {transaction["value"]} | for {value_price} TRX")

async def snipe_channel(message):
    pass

@bot.message_handler(state=MyStates.channel_username)
async def start_snipe(message,state: StateContext):
    await state.add_data(channel_username=message.text)
    async with state.data() as data:
        name = data.get("channel_username")
    await bot.send_message(
        chat_id=message.chat.id,
        parse_mode='Markdown',
        text=name)
    await app.start()
    while True:
        try:
            await snipe_channel(message)
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        await asyncio.sleep(1)

@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call,state: StateContext):
    await bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == "create_solana_wallet":
        address = ""
        if db.contains_user(call.message.from_user.id):
            address = db.get_address_by_user_id(call.message.from_user.id)
        else:
            crypto_wallet = wallet.Wallet(Bip44Coins.SOLANA)
            mnemonic, address, pk = crypto_wallet.create_solana_wallet()
            db.add_user(call.message.from_user.id, address, pk)

        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Buy", callback_data="buy_button"),
                     InlineKeyboardButton("Snipe", callback_data="snipe_button"))
        keyboard.add(InlineKeyboardButton("Home", callback_data="home_button"))

        message = f"Your address: `{address}`"
        await bot.send_message(
            chat_id=call.message.chat.id,
            parse_mode='Markdown',
            text=message,
            reply_markup=keyboard)

    elif call.data == "snipe_button":
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Snipe tg channel", callback_data="snipe_tg_channel"),
                     InlineKeyboardButton("Snipe address", callback_data="snipe_address"))
        await bot.send_message(
            chat_id=call.message.chat.id,
            parse_mode='Markdown',
            text="What you do?",
            reply_markup=keyboard)
    elif call.data == "snipe_tg_channel":
        await state.set(MyStates.channel_username)
        await bot.send_message(
            chat_id=call.message.chat.id,
            parse_mode='Markdown',
            text="Send channel username")
    elif call.data == "snipe_address":
        for account in snipe_accounts:
            url = f'https://api.trongrid.io/v1/accounts/{account.address}/transactions/trc20'
            params = {
                'limit': 1,
            }
            response = requests.get(url, params=params)
            transactions_array = response.json()['data']
            for transaction in transactions_array:
                if not transaction in last_transaction:
                    last_transaction.append(transaction)
        while True:
            try:
                await snipe_address(call.message)
            except Exception as e:
                print(f"Произошла ошибка: {e}")
            await asyncio.sleep(1)


bot.add_custom_filter(asyncio_filters.StateFilter(bot))
bot.add_custom_filter(asyncio_filters.IsDigitFilter())
bot.add_custom_filter(asyncio_filters.TextMatchFilter())

from telebot.states.asyncio.middleware import StateMiddleware

bot.setup_middleware(StateMiddleware(bot))
if __name__ == '__main__':
    asyncio.run(bot.infinity_polling())