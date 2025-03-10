import requests
import pandas as pd
import numpy as np
import time

# Global flags and variables
moving_averages = pd.DataFrame()  # For storing moving averages
candle_size_data = {'bullish': [], 'bearish': []}  # For market pressure calculation


# Function to get historical prices based on the selected market type
def get_historical_prices(symbol, interval='1m', limit=200, market_type='spot'):
    try:
        base_url = (
            'https://fapi.binance.com/fapi/v1/klines'
            if market_type == 'futures' else
            'https://api.binance.com/api/v3/klines'
        )
        symbol = symbol.upper()
        url = f'{base_url}?symbol={symbol}&interval={interval}&limit={limit}'
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful
        data = response.json()

        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                   'close_time', 'quote_asset_volume', 'number_of_trades',
                   'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume',
                   'ignore']
        if len(data[0]) == 12:
            prices = pd.DataFrame(data, columns=columns)
        else:
            prices = pd.DataFrame(data, columns=columns[:len(data[0])])

        prices['timestamp'] = pd.to_datetime(prices['timestamp'], unit='ms')
        prices['close'] = pd.to_numeric(prices['close'])
        prices['open'] = pd.to_numeric(prices['open'])
        prices['high'] = pd.to_numeric(prices['high'])
        prices['low'] = pd.to_numeric(prices['low'])
        return prices
    except Exception as e:
        print(f"Error fetching historical prices: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error


# Function to get the current price and 24-hour high/low based on the selected market type
def get_price_data(symbol, market_type='spot'):
    retries = 3
    while retries > 0:
        try:
            base_url = (
                'https://fapi.binance.com/fapi/v1/ticker/24hr'
                if market_type == 'futures' else
                'https://api.binance.com/api/v3/ticker/24hr'
            )
            symbol = symbol.upper()
            # list of symbol
            # loop list
            url = f'{base_url}?symbol={symbol}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            # implement order obj here
            return {
                'current_price': float(data['lastPrice']),
                'high_price': float(data['highPrice']),
                'low_price': float(data['lowPrice'])
            }
        except Exception as e:
            print(f"Error fetching price data: {e}")
            retries -= 1
            time.sleep(1)  # Wait before retrying
    return {
        'current_price': 0.0,
        'high_price': 0.0,
        'low_price': 0.0
    }


# Function to calculate moving averages
def calculate_moving_averages(prices, periods=[5, 7, 21, 150, 200]):
    global moving_averages
    for period in periods:
        prices[f'MA_{period}'] = prices['close'].rolling(window=period).mean()
    moving_averages = prices
    return prices


# Function to get the current moving average value
def get_current_ma(period):
    global moving_averages
    if not moving_averages.empty:
        return moving_averages[f'MA_{period}'].iloc[-1]
    return None


# Function to calculate market pressure
def calculate_market_pressure(prices):
    global candle_size_data
    sample_size = 10

    if len(prices) < sample_size:
        return {'bullish_avg': 0, 'bearish_avg': 0}

    # Reset candle size data for each calculation
    candle_size_data = {'bullish': [], 'bearish': []}

    for index in range(-sample_size, -1):
        candle = prices.iloc[index]
        candle_size = candle['high'] - candle['low']
        if candle['close'] > candle['open']:
            candle_size_data['bullish'].append(candle_size)
        else:
            candle_size_data['bearish'].append(candle_size)

    bullish_avg = np.mean(candle_size_data['bullish']) if candle_size_data['bullish'] else 0
    bearish_avg = np.mean(candle_size_data['bearish']) if candle_size_data['bearish'] else 0
    return {'bullish_avg': bullish_avg, 'bearish_avg': bearish_avg}


# Function to determine market condition and trend strength
def determine_market_condition(current_price, ma_200, ma_21, ma_7, ma_5):
    # Order the values from highest to lowest
    values = sorted(
        [("Current Price", current_price), ("5-MA", ma_5), ("7-MA", ma_7), ("21-MA", ma_21), ("200-MA", ma_200)],
        key=lambda x: x[1],
        reverse=True
    )

    # Extract just the labels for comparison
    order = [label for label, value in values]

    # Determine market condition
    if order == ["Current Price", "5-MA", "7-MA", "21-MA", "200-MA"] or \
            order == ["5-MA", "Current Price", "7-MA", "21-MA", "200-MA"] or \
            order == ["21-MA", "Current Price", "5-MA", "7-MA", "200-MA"] or \
            order == ["Current Price", "21-MA", "5-MA", "7-MA", "200-MA"] or \
            order == ["21-MA", "Current Price", "5-MA", "7-MA", "200-MA"] or \
            order == ["Current Price", "7-MA", "5-MA", "21-MA", "200-MA"] or \
            order == ["21-MA", "Current Price", "7-MA", "5-MA", "200-MA"] or \
            order == ["Current Price", "21-MA", "7-MA", "5-MA", "200-MA"] or \
            order == ["Current Price", "7-MA", "21-MA", "5-MA", "200-MA"] or \
            order == ["7-MA", "21-MA", "Current Price", "5-MA", "200-MA"] or \
            order == ["Current Price", "5-MA", "21-MA", "7-MA", "200-MA"] or \
            order == ["Current Price", "200-MA", "5-MA", "7-MA", "21-MA"] or \
            order == ["Current Price", "5-MA", "200-MA", "7-MA", "21-MA"] or \
            order == ["Current Price", "5-MA", "7-MA", "200-MA", "21-MA"] or \
            order == ["Current Price", "5-MA", "200-MA", "7-MA", "21-MA"] or \
            order == ["Current Price", "5-MA", "7-MA", "200-MA", "21-MA"] or \
            order == ["Current Price", "21-MA", "200-MA", "5-MA", "7-MA"] or \
            order == ["21-MA", "Current Price", "200-MA", "5-MA", "7-MA"] or \
            order == ["Current Price", "200-MA", "5-MA", "21-MA", "7-MA"] or \
            order == ["5-MA", "Current Price", "7-MA", "200-MA", "21-MA"] or \
            order == ["Current Price", "7-MA", "5-MA", "200-MA", "21-MA"] or \
            order == ["Current Price", "7-MA", "200-MA", "5-MA", "21-MA"] or \
            order == ["Current Price", "200-MA", "21-MA", "5-MA", "7-MA"] or \
            order == ["Current Price", "200-MA", "5-MA", "7-MA", "21-MA"] or \
            order == ["5-MA", "21-MA", "Current Price", "200-MA", "7-MA"] or \
            order == ["21-MA", "Current Price", "200-MA", "7-MA", "5-MA"] or \
            order == ["21-MA", "5-MA", "Current Price", "7-MA", "200-MA"]:
        return "Bullish"

    elif order == ["200-MA", "21-MA", "Current Price", "5-MA", "7-MA"] or \
        order == ["200-MA", "Current Price", "5-MA", "7-MA", "21-MA"] or \
        order == ["200-MA", "5-MA", "Current Price", "7-MA", "21-MA"] or \
        order == ["200-MA", "21-MA", "Current Price", "7-MA", "5-MA"] or \
        order == ["200-MA", "Current Price", "21-MA", "7-MA", "5-MA"] or \
        order == ["200-MA", "Current Price", "5-MA", "21-MA", "7-MA"] or \
        order == ["200-MA", "Current Price", "21-MA", "5-MA", "7-MA"] or \
        order == ["200-MA", "Current Price", "7-MA", "5-MA", "21-MA"] or \
        order == ["21-MA", "200-MA", "Current Price", "5-MA", "7-MA"] or \
        order == ["21-MA", "200-MA", "Current Price", "7-MA", "5-MA"] or \
        order == ["200-MA", "Current Price", "21-MA", "5-MA", "7-MA"] or \
        order == ["200-MA", "Current Price", "7-MA", "21-MA", "5-MA"] or \
        order == ["5-MA", "200-MA", "Current Price", "21-MA", "7-MA"] or \
            order == ["200-MA", "Current Price", "7-MA", "21-MA", "5-MA"]:
        market_condition = "Shortbull"

    elif order == ["21-MA", "7-MA", "5-MA", "Current Price", "200-MA"] or \
            order == ["7-MA", "5-MA", "Current Price", "21-MA", "200-MA"] or \
            order == ["21-MA", "7-MA", "Current Price", "5-MA", "200-MA"] or \
            order == ["5-MA", "7-MA", "Current Price", "21-MA", "200-MA"] or \
            order == ["5-MA", "7-MA", "21-MA", "Current Price", "200-MA"] or \
            order == ["7-MA", "21-MA", "5-MA", "Current Price", "200-MA"] or \
            order == ["21-MA", "5-MA", "7-MA", "Current Price", "200-MA"] or \
            order == ["5-MA", "21-MA", "7-MA", "Current Price", "200-MA"] or \
            order == ["7-MA", "5-MA", "21-MA", "Current Price", "200-MA"] or \
            order == ["7-MA", "21-MA", "5-MA", "Current Price", "200-MA"] or \
            order == ["5-MA", "7-MA", "Current Price", "200-MA", "21-MA"] or \
            order == ["7-MA", "5-MA", "Current Price", "200-MA", "21-MA"] or \
            order == ["7-MA", "5-MA", "Current Price", "200-MA", "21-MA"] or \
            order == ["5-MA", "21-MA", "7-MA", "Current Price", "200-MA"] or \
            order == ["7-MA", "Current Price", "5-MA", "200-MA", "21-MA"] or \
            order == ["5-MA", "7-MA", "Current Price", "21-MA", "200-MA"] or \
            order == ["7-MA", "Current Price", "5-MA", "21-MA", "200-MA"]:
        return "Longbear"

    elif order == ["200-MA", "21-MA", "7-MA", "5-MA", "Current Price"] or \
            order == ["200-MA", "7-MA", "5-MA", "Current Price", "21-MA"] or \
            order == ["200-MA", "21-MA", "7-MA", "Current Price", "5-MA"] or \
            order == ["200-MA", "7-MA", "21-MA", "5-MA", "Current Price"] or \
            order == ["7-MA", "5-MA", "200-MA", "21-MA", "Current Price"] or \
            order == ["7-MA", "200-MA", "5-MA", "21-MA", "Current Price"] or \
            order == ["200-MA", "5-MA", "7-MA", "Current Price", "21-MA"] or \
            order == ["200-MA", "7-MA", "5-MA", "21-MA", "Current Price"] or \
            order == ["21-MA", "200-MA", "7-MA", "5-MA", "Current Price"] or \
            order == ["21-MA", "7-MA", "5-MA", "200-MA", "Current Price"] or \
            order == ["21-MA", "7-MA", "200-MA", "5-MA", "Current Price"] or \
            order == ["200-MA", "21-MA", "5-MA", "7-MA", "Current Price"] or \
            order == ["21-MA", "200-MA", "5-MA", "7-MA", "Current Price"] or \
            order == ["200-MA", "7-MA", "21-MA", "Current Price", "5-MA"] or \
            order == ["200-MA", "5-MA", "7-MA", "21-MA", "Current Price"] or \
            order == ["5-MA", "200-MA", "7-MA", "21-MA", "Current Price"] or \
            order == ["5-MA", "200-MA", "7-MA", "Current Price", "21-MA"] or \
            order == ["5-MA", "7-MA", "200-MA", "Current Price", "21-MA"] or \
            order == ["5-MA", "7-MA", "200-MA", "21-MA", "Current Price"] or \
            order == ["200-MA", "5-MA", "21-MA", "7-MA", "Current Price"] or \
            order == ["7-MA", "5-MA", "200-MA", "Current Price", "21-MA"] or \
            order == ["21-MA", "7-MA", "5-MA", "200-MA", "Current Price"] or \
            order == ["7-MA", "5-MA", "21-MA", "200-MA", "Current Price"] or \
            order == ["7-MA", "21-MA", "5-MA", "200-MA", "Current Price"] or \
            order == ["21-MA", "200-MA", "7-MA", "Current Price", "5-MA"] or \
            order == ["7-MA", "200-MA", "Current Price", "5-MA", "21-MA"] or \
            order == ["21-MA", "5-MA", "200-MA", "7-MA", "Current Price"] or \
            order == ["21-MA", "7-MA", "200-MA", "5-MA", "Current Price"] or \
            order == ["200-MA", "21-MA", "5-MA", "7-MA", "Current Price"] or \
            order == ["200-MA", "5-MA", "7-MA", "Current Price", "21-MA"] or \
            order == ["7-MA", "5-MA", "21-MA", "200-MA", "Current Price"] or \
            order == ["7-MA", "200-MA", "5-MA", "21-MA", "Current Price"] or \
            order == ["200-MA", "7-MA", "Current Price", "5-MA", "21-MA"]:
        market_condition = "Bearish"

    elif order == ["200-MA", "21-MA", "Current Price", "5-MA", "7-MA"] or \
            order == ["200-MA", "Current Price", "5-MA", "7-MA", "21-MA"] or \
            order == ["200-MA", "5-MA", "Current Price", "7-MA", "21-MA"] or \
            order == ["200-MA", "21-MA", "Current Price", "7-MA", "5-MA"] or \
            order == ["200-MA", "Current Price", "21-MA", "7-MA", "5-MA"] or \
            order == ["200-MA", "Current Price", "5-MA", "21-MA", "7-MA"] or \
            order == ["200-MA", "Current Price", "21-MA", "5-MA", "7-MA"] or \
            order == ["200-MA", "Current Price", "7-MA", "5-MA", "21-MA"] or \
            order == ["21-MA", "200-MA", "Current Price", "5-MA", "7-MA"] or \
            order == ["21-MA", "200-MA", "Current Price", "7-MA", "5-MA"] or \
            order == ["200-MA", "Current Price", "21-MA", "5-MA", "7-MA"] or \
            order == ["200-MA", "Current Price", "7-MA", "21-MA", "5-MA"] or \
            order == ["5-MA", "200-MA", "Current Price", "21-MA", "7-MA"] or \
            order == ["200-MA", "Current Price", "7-MA", "21-MA", "5-MA"] or \
            order == ["200-MA", "21-MA", "5-MA", "Current Price", "7-MA"]:
        return "Shortbull"

    else:
        market_condition = "Neutral"

    # Determine trend strength
    if market_condition in ["Bullish", "Shortbull"]:
        if current_price > ma_21 and ma_5 > ma_21 and ma_7 > ma_21:
            trend_strength = "Strong"
        elif current_price < ma_21 and ma_5 < ma_21 and ma_7 < ma_21:
            trend_strength = "Weak"
        elif (current_price > ma_5 > ma_7 > ma_21) or (current_price > ma_7 > ma_5 > ma_21):
            trend_strength = "Strong"
        else:
            trend_strength = "Neutral"

    elif market_condition in ["Bearish", "Longbear"]:
        if current_price < ma_21 and ma_5 < ma_21 and ma_7 < ma_21:
            trend_strength = "Strong"
        elif current_price > ma_21 and ma_5 > ma_21 and ma_7 > ma_21:
            trend_strength = "Weak"
        elif (ma_21 > ma_5 > ma_7 > current_price) or (ma_21 > ma_7 > ma_5 > current_price):
            trend_strength = "Weak"
        else:
            trend_strength = "Neutral"

    else:
        trend_strength = "Neutral"

    return market_condition
