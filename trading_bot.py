import requests
import telebot
import time
import numpy as np
import pandas as pd
import talib

# API keys
API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'

# Telegram bot token
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'

# Create a bot instance
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Binance endpoint
BASE_URL = 'https://api.binance.com/api/v3/'

# Function to get historical data

def get_historical_data(symbol, interval='1h', limit=100):
    url = f'{BASE_URL}klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)
    data = response.json()
    return np.array(data)

# Function to calculate technical indicators

def calculate_indicators(data):
    close_prices = data[:, 4].astype(float)
    # MACD
    macd, signal, _ = talib.MACD(close_prices)
    # RSI
    rsi = talib.RSI(close_prices)
    # Bollinger Bands
    upperband, middleband, lowerband = talib.BBANDS(close_prices)
    # EMA
    ema = talib.EMA(close_prices)
    return macd, signal, rsi, upperband, middleband, lowerband, ema

# Function to send Telegram notifications

def send_notification(message):
    bot.send_message(chat_id='YOUR_CHAT_ID', text=message)

# Main trading signal bot loop

def trading_bot():
    while True:
        # Get historical data
        data = get_historical_data('BTCUSDT')
        macd, signal, rsi, upperband, middleband, lowerband, ema = calculate_indicators(data)
        # Trading logic
        if macd[-1] > signal[-1] and rsi[-1] < 30:
            send_notification('Buy signal generated!')
        elif macd[-1] < signal[-1] and rsi[-1] > 70:
            send_notification('Sell signal generated!')
        time.sleep(60)

# Start the trading bot
if __name__ == '__main__':
    trading_bot()