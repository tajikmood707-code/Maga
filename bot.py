import requests
import numpy as np
import pandas as pd
from datetime import datetime
import schedule
import time
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Function to send message to Telegram
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message
        }
        requests.post(url, json=payload, timeout=10)
        logger.info("Message sent to Telegram")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

# Function to fetch real market data from CoinGecko
def fetch_market_data(crypto='bitcoin', days=100):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        prices = [price[1] for price in data['prices']]
        
        return pd.DataFrame({
            'close': prices,
            'timestamp': [datetime.fromtimestamp(price[0]/1000) for price in data['prices']]
        })
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        return None

# Function to calculate technical indicators
def calculate_indicators(data):
    try:
        # Simple Moving Averages
        data['SMA_20'] = data['close'].rolling(window=20).mean()
        data['SMA_50'] = data['close'].rolling(window=50).mean()
        
        # RSI (Relative Strength Index)
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD (Moving Average Convergence Divergence)
        ema_12 = data['close'].ewm(span=12).mean()
        ema_26 = data['close'].ewm(span=26).mean()
        data['MACD'] = ema_12 - ema_26
        data['Signal_Line'] = data['MACD'].ewm(span=9).mean()
        data['MACD_Histogram'] = data['MACD'] - data['Signal_Line']
        
        return data
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return None

# Function to generate trading signals with multiple indicators
def generate_signals(data):
    try:
        if data is None or len(data) < 50:
            return "HOLD", 0
        
        current = data.iloc[-1]
        
        # SMA Crossover Signal
        sma_signal = 0
        if current['SMA_20'] > current['SMA_50']:
            sma_signal = 1  # Bullish
        elif current['SMA_20'] < current['SMA_50']:
            sma_signal = -1  # Bearish
        
        # RSI Signal
        rsi_signal = 0
        if current['RSI'] < 30:
            rsi_signal = 1  # Oversold - BUY
        elif current['RSI'] > 70:
            rsi_signal = -1  # Overbought - SELL
        
        # MACD Signal
        macd_signal = 0
        if current['MACD'] > current['Signal_Line']:
            macd_signal = 1  # Bullish
        else:
            macd_signal = -1  # Bearish
        
        # Combined signal score
        total_signal = sma_signal + rsi_signal + macd_signal
        confidence = abs(total_signal) / 3
        
        if total_signal >= 2:
            return "BUY", confidence
        elif total_signal <= -2:
            return "SELL", confidence
        else:
            return "HOLD", confidence
            
    except Exception as e:
        logger.error(f"Error generating signals: {e}")
        return "HOLD", 0

# Function to validate signals
def validate_signal(signal):
    valid_signals = ["BUY", "SELL", "HOLD"]
    return signal in valid_signals

# Main function to run the trading bot
def run_trading_bot():
    try:
        logger.info("Running trading bot...")
        
        # Fetch market data
        market_data = fetch_market_data('bitcoin', days=100)
        if market_data is None:
            logger.warning("Could not fetch market data")
            return
        
        # Calculate indicators
        market_data = calculate_indicators(market_data)
        if market_data is None:
            logger.warning("Could not calculate indicators")
            return
        
        # Generate signal
        signal, confidence = generate_signals(market_data)
        
        # Validate and send signal
        if validate_signal(signal) and confidence > 0:
            message = f"🤖 Signal Generated\n"
            message += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            message += f"📊 Signal: {signal}\n"
            message += f"💪 Confidence: {confidence*100:.1f}%\n"
            message += f"💰 Current Price: ${market_data['close'].iloc[-1]:.2f}"
            
            send_telegram_message(message)
            logger.info(f"Signal sent: {signal} with confidence {confidence}")
        else:
            logger.info(f"Signal: {signal} (confidence: {confidence})")
            
    except Exception as e:
        logger.error(f"Error in run_trading_bot: {e}")

# Schedule the trading bot to run every hour
schedule.every(1).hour.do(run_trading_bot)

if __name__ == "__main__":
    logger.info("Trading bot started")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Trading bot stopped")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(60)