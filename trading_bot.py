import requests
import numpy as np
import pandas as pd
from datetime import datetime
import schedule
import time

# Telegram Bot Token and Chat ID
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

# Function to send message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    requests.post(url, json=payload)

# Function to generate trading signals
def generate_signals(data):
    # Example: Simple moving average crossover strategy
    data['SMA_20'] = data['close'].rolling(window=20).mean()
    data['SMA_50'] = data['close'].rolling(window=50).mean()

    if data['SMA_20'].iloc[-1] > data['SMA_50'].iloc[-1]:
        return "BUY"
    elif data['SMA_20'].iloc[-1] < data['SMA_50'].iloc[-1]:
        return "SELL"
    else:
        return "HOLD"

# Function to validate signals
def validate_signal(signal):
    valid_signals = ["BUY", "SELL", "HOLD"]
    return signal in valid_signals

# Function to fetch market data (mocked, should be replaced with real data source)
def fetch_market_data():
    # Replace with real market data fetching
    return pd.DataFrame({
        'close': np.random.rand(100) * 100  # Mocked price data
    })

# Main function to run the trading bot
def run_trading_bot():
    market_data = fetch_market_data()
    signal = generate_signals(market_data)

    if validate_signal(signal):
        message = f"Signal generated at {datetime.now()}: {signal}"
        send_telegram_message(message)
    else:
        print("Invalid signal generated. No action taken.")

# Schedule the trading bot to run every minute
schedule.every(1).minute.do(run_trading_bot)

while True:
    schedule.run_pending()
    time.sleep(1)