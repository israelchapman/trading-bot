import logging
import queue
import time
import requests
import json
import os
import common
import pandas as pd
from openpyxl import Workbook
import uuid
from projector import Projector
from dictator import Dictator
from config import Config

VALIDATOR_queue = queue.Queue()

EXCEL_FILE = "trade_log.xlsx"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

executor_logger = logging.getLogger("executor")
SETTINGS_FILE = "settings.json"


# Ensure the file exists before writing
if not os.path.exists(EXCEL_FILE):
    wb = Workbook()
    ws = wb.active
    ws.title = "Trade Log"
    wb.save(EXCEL_FILE)


def clear_last_trade_id():
    """Remove the last trade ID from settings.json."""
    try:
        with open(SETTINGS_FILE, 'r') as file:
            settings = json.load(file)

        settings.pop("last_trade_id", None)  # Remove the key if it exists

        with open(SETTINGS_FILE, 'w') as file:
            json.dump(settings, file, indent=4)

    except (FileNotFoundError, json.JSONDecodeError):
        pass  # Ignore if file doesn't exist or is empty


def generate_trade_id(active_open_queue):
    """Generate or reuse a trade ID based on active trade status."""
    if active_open_queue.empty() or "0" in list(active_open_queue.queue):
        trade_id = str(uuid.uuid4())  # Generate a new unique ID
        save_trade_id(trade_id)  # Save the new trade ID
        executor_logger.info(f"generating TID and saving")
        return trade_id
    else:
        executor_logger.info(f"using saved TID")
        return get_last_trade_id()  # Reuse the last trade ID if needed


def get_last_trade_id():
    """Retrieve the last trade ID from settings.json."""
    try:
        with open(SETTINGS_FILE, 'r') as file:
            settings = json.load(file)
            executor_logger.info(f"getting saved TID")
        return settings.get("last_trade_id", "")
    except (FileNotFoundError, json.JSONDecodeError):
        return ""


def save_trade_id(trade_id):
    """Save a new trade ID to settings.json."""
    try:
        with open(SETTINGS_FILE, 'r') as file:
            settings = json.load(file)
            executor_logger.info(f"def save_trade_id saving TID")
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}

    settings["last_trade_id"] = trade_id  # Store the unique trade ID

    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file, indent=4)


def load_settings():
    """Load profit margin and risk loss margin from settings.json."""
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        return settings.get("return_percentage", 0), settings.get("loss_risk_percentage", 0), settings.get("interval", 0)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        executor_logger.error(f"Error loading settings: {e}")
        return 0, 0, 0  # Default to 0 if settings file is missing or corrupted


def log_trade_to_excel(trade_id, symbol, trade_type, price, market_type, status, market_condition, ma_200, ma_21, ma_7, ma_5):
    """
    Log trade details into an Excel spreadsheet.

    Args:
        trade_id (str): trade unique id
        symbol (str): Trading pair (e.g., BTCUSDT).
        trade_type (str): Type of trade (market_buy, market_sell, limit_buy, limit_sell).
        price (float): Execution price.
        market_type (str): Spot or Futures.
        status (str): 'Opened' or 'Closed'.
        market_condition (str): Market condition at the time of trade execution.
        ma_200 (float): Value of the ma_200 moving average.
        ma_21 (float): Value of the ma_21 moving average.
        ma_7 (float): Value of the ma_7 moving average.
        ma_5 (float): Value of the ma_5 moving average.
    """

    # Load profit margin and risk loss margin from settings.json
    return_percentage, loss_risk_percentage, interval = load_settings()

    trade_data = {
        "Trade ID": [trade_id],  # Add the unique trade ID
        "Timestamp": [time.strftime('%Y-%m-%d %H:%M:%S')],
        "Symbol": [symbol],
        "Trade Type": [trade_type],
        "Price": [price],
        "Market Type": [market_type],
        "Status": [status],  # 'Opened' or 'Closed'
        "Market Condition": [market_condition],  # e.g., Bullish, Bearish, Neutral
        "ma_200": [ma_200],
        "ma_21": [ma_21],
        "ma_7": [ma_7],
        "ma_5": [ma_5],
        "return percentage": [return_percentage],  # New column
        "loss risk percentage": [loss_risk_percentage],  # New column
        "interval": [interval]
    }

    df_new = pd.DataFrame(trade_data)

    try:
        if os.path.exists(EXCEL_FILE):
            # Load existing data
            existing_data = pd.read_excel(EXCEL_FILE, sheet_name="Trade Log")

            # Append new data
            updated_data = pd.concat([existing_data, df_new], ignore_index=True)

            # Save back to file
            with pd.ExcelWriter(EXCEL_FILE, engine="openpyxl", mode="w") as writer:
                updated_data.to_excel(writer, index=False, sheet_name="Trade Log")
        else:
            # Create new file if it does not exist
            df_new.to_excel(EXCEL_FILE, index=False, sheet_name="Trade Log")

    except PermissionError:
        executor_logger.info("Error logging trade to Excel: File is open. Close it and try again.")
    except Exception as e:
        executor_logger.info(f"Error logging trade to Excel: {e}")
    else:
        executor_logger.info(f"Trade logged to Excel: {trade_type} at {price}")


def get_current_price(symbol, market_type='spot'):
    retries = 3
    while retries > 0:
        try:
            base_url = (
                'https://fapi.binance.com/fapi/v1/ticker/24hr'
                if market_type == 'futures' else
                'https://api.binance.com/api/v3/ticker/24hr'
            )
            symbol = symbol.upper()
            url = f'{base_url}?symbol={symbol}'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return float(data['lastPrice'])
        except Exception as e:
            executor_logger.error(f"Error fetching price data: {e}")
            retries -= 1
            time.sleep(1)  # Wait before retrying
    return 0.0  # Return a default price if failed


def save_trade_price(symbol, trade_type, current_price, market_type):
    """Save only the latest executed trade price in settings.json"""
    return_percentage, loss_risk_percentage, interval = load_settings()  # Load interval
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    # Save only the latest trade
    data["trades"] = {
        "symbol": symbol,
        "trade_type": trade_type,
        "price": current_price,
        "market_type": market_type,
        "interval": interval
    }

    with open(SETTINGS_FILE, "w") as file:
        json.dump(data, file, indent=4)

    executor_logger.info(f"Trade saved: {symbol} | {trade_type} | {current_price} | Interval: {interval}")


def load_last_trade_price():
    """Load the last trade price from settings.json"""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            try:
                data = json.load(file)
                if "trades" in data and data["trades"]:
                    return data["trades"]["price"]
            except json.JSONDecodeError:
                executor_logger.warning("Failed to decode JSON while loading last trade price.")
                return None
    return None


def calculate_200_percentage(symbol, ma_200):
    """Calculate the percentage difference between a moving average and the price."""
    price = get_current_price(symbol)
    if price:
        percentage = round(((ma_200 - price) / price) * 100, 2)
        #executor_logger.debug(f"Calculated percentage: {percentage}% for MA:200, Price: {price}")
        return percentage
    return None


def calculate_21_percentage(symbol, ma_21):
    """Calculate the percentage difference between a moving average and the price."""
    price = get_current_price(symbol)
    if price:
        percentage = round(((ma_21 - price) / price) * 100, 2)
        #executor_logger.debug(f"Calculated percentage: {percentage}% for MA:21, Price: {price}")
        return percentage
    return None


def calculate_7_percentage(symbol, ma_7):
    """Calculate the percentage difference between a moving average and the price."""
    price = get_current_price(symbol)
    if price:
        percentage = round(((ma_7 - price) / price) * 100, 2)
        #executor_logger.debug(f"Calculated percentage: {percentage}% for MA:7, Price: {price}")
        return percentage
    return None


def calculate_5_percentage(symbol, ma_5):
    """Calculate the percentage difference between a moving average and the price."""
    price = get_current_price(symbol)
    if price:
        percentage = round(((ma_5 - price) / price) * 100, 2)
        #executor_logger.debug(f"Calculated percentage: {percentage}% for MA:5, Price: {price}")
        return percentage
    return None


def execute_trade(trade_type, signal_queue, active_open_queue, active_sell_queue, symbol, market_type, market_condition, ma_200, ma_21, ma_7, ma_5):
    executor_logger.debug(f"Attempting to execute trade with trade type: {trade_type}")

    # Load the last saved trade price from settings.json
    settings = common.load_settings()  # Load settings as a dictionary
    interval = settings.get("interval")  # Extract interval safely
    current_price = get_current_price(symbol, market_type)  # Get last recorded trade price

    if interval is None:
        executor_logger.error("Interval not found in settings.json. Check configuration.")

    if current_price is None:
        executor_logger.warning(f"No saved trade price found in settings.json for {symbol}. Fetching live price.")
        current_price = get_current_price(symbol, market_type)  # Fallback to live price

    # Only pause monitoring if active_open_queue value is "0"
    if active_open_queue.empty() or "0" in list(active_open_queue.queue):
        signal_queue.put("PAUSE")
        executor_logger.info("Monitoring paused while trade is being executed.")
    else:
        executor_logger.info("Monitoring not paused: active trade already exists.")

    import hotkey

    def can_execute_trade(activity_queue):
        try:
            VALIDATOR_queue.put("PLAY")
            # Check if an active trade is already in progress (queue check)
            with activity_queue.mutex:
                if "1" in list(activity_queue.queue):
                    executor_logger.info("Trade execution blocked: Active trade already in progress.")
                    return False  # Block execution if trade is active

            # ADD BOT2 CHECKING LOGIC HERE (dictator_output.xlsx check)
            file_path = "dictator_output.xlsx"
            try:
                df = pd.read_excel(file_path)
            except Exception as e:
                executor_logger.error(f"Error reading dictator_output.xlsx: {e}")
                return True  # If file cannot be read, allow trade to continue

            # Ensure required columns exist
            required_columns = ["Symbol", "Trade Type", "Price", "Market Type", "interval", "ma_200_percentage",
                                "ma_21_percentage", "ma_7_percentage", "ma_5_percentage"]
            if not all(col in df.columns for col in required_columns):
                executor_logger.error("dictator_output.xlsx is missing required columns.")
                return True  # Allow trade to continue if columns are missing

            # Check if current trade matches any entry in the Excel file
            match = df[
                (df["Symbol"] == symbol) &
                (df["Trade Type"] == trade_type) &
                (df["Market Type"] == market_type) &
                (df["interval"] == interval) &
                (df["ma_200_percentage"] == calculate_200_percentage(symbol, ma_200)) &
                (df["ma_21_percentage"] == calculate_21_percentage(symbol, ma_21)) &
                (df["ma_7_percentage"] == calculate_7_percentage(symbol, ma_7)) &
                (df["ma_5_percentage"] == calculate_5_percentage(symbol, ma_5))
                ]

            if not match.empty:
                executor_logger.info(
                    f"Trade execution blocked: Matching entry found in dictator_output.xlsx for {trade_type} at {current_price}")
                # ADD QUEUE SIGNAL TO STOP CLOSING TRADE
                VALIDATOR_queue.put("PAUSE")
                executor_logger.info(f"validator queue:{VALIDATOR_queue}")
                return False  # Block trade if a match is found

            return True  # Allow trade if no match is found

        except Exception as e:
            executor_logger.error(f"Error checking trade queue and dictator_output.xlsx: {e}")
            return False  # In case of any error, prevent execution

    if trade_type in ['limit_buy', 'market_buy']:
        if can_execute_trade(active_open_queue):
            current_price = get_current_price(symbol, market_type)  # Get current price

            if trade_type == 'limit_buy':
                hotkey.limit_buy_trade()
            else:  # market_buy
                hotkey.market_buy_trade()

            trade_id = generate_trade_id(active_open_queue)  # Generate a unique ID
            log_trade_to_excel(trade_id, symbol, trade_type, current_price, market_type, "Opened", market_condition,
                               ma_200, ma_21, ma_7, ma_5)  # Log trade
            # Completely clear the queue
            with active_open_queue.mutex:
                active_open_queue.queue.clear()

            active_open_queue.put("1")  # Mark open trade as active
            executor_logger.info(f"Current active_open_queue: {list(active_open_queue.queue)}")
            save_trade_price(symbol, trade_type, current_price, market_type)  # Save trade data

        else:
            executor_logger.info(f"Trade execution blocked: {trade_type} already active.")

    elif trade_type in ['limit_sell', 'market_sell']:
        if can_execute_trade(active_open_queue):
            current_price = get_current_price(symbol, market_type)  # Get current price

            if trade_type == 'limit_sell':
                hotkey.limit_sell_trade()
            else:  # market_sell
                hotkey.market_sell_trade()

            trade_id = generate_trade_id(active_open_queue)  # Generate a unique ID
            log_trade_to_excel(trade_id, symbol, trade_type, current_price, market_type, "Opened", market_condition,
                               ma_200, ma_21, ma_7, ma_5)  # Log trade
            # Completely clear the queue
            with active_open_queue.mutex:
                active_open_queue.queue.clear()

            active_open_queue.put("1")  # Mark sell trade as active
            executor_logger.info(f"Current active_open_queue: {list(active_open_queue.queue)}")
            save_trade_price(symbol, trade_type, current_price, market_type)  # Save trade data

        else:
            executor_logger.info(f"Trade execution blocked: {trade_type} already active.")

    if active_open_queue.empty():
        executor_logger.warning("No active trade in queue. Exiting check_and_close_trade.")
        return  # No active open trade

    settings = common.load_settings()  # Use common module to load settings
    executor_logger.info("Settings loaded successfully.")

    last_trade_data = settings.get("trades", {})
    last_trade_price = last_trade_data.get("price", None)
    trade_type = last_trade_data.get("trade_type", "")

    if last_trade_price is None:
        executor_logger.warning("No last trade price found. Exiting trade closure check.")
        return

    executor_logger.info(f"Last trade price: {last_trade_price}, Trade type: {trade_type}")

    profit_margin = float(settings.get("return_percentage", 0)) / 100
    loss_margin = float(settings.get("loss_risk_percentage", 0)) / 100

    if trade_type == 'market_buy':
        profit_threshold = last_trade_price * (1 + profit_margin)
        loss_threshold = last_trade_price * (1 - loss_margin)
    else:
        profit_threshold = last_trade_price * (1 - profit_margin)
        loss_threshold = last_trade_price * (1 + loss_margin)

    executor_logger.info(f"Profit target: {profit_threshold}, Loss limit: {loss_threshold}")
    executor_logger.info(f"current price: {current_price}")

    # ADD SOMETHING LIKE A QUEUE TO STOP EXECUTION IF OPEN TRADE IS BLOCK BY DICTATOR
    if trade_type == 'market_buy':
        if not VALIDATOR_queue.empty():
            value = VALIDATOR_queue.queue[0]  # Peek at the first item without removing it
            if value != "PAUSE":
                if current_price >= profit_threshold:
                    # If a trade needs to be closed, pause monitoring
                    signal_queue.put("PAUSE")
                    executor_logger.info("Monitoring paused while closing trade.")
                    executor_logger.info(f"Closing buy trade: Profit target reached at {profit_threshold}")
                    hotkey.close_market_buy_trade()

                    executor_logger.info("Executed close_market_buy_trade().")
                    executor_logger.info("Clearing active trade queue before resetting status.")
                    trade_id = generate_trade_id(active_open_queue)  # Generate a unique ID

                    log_trade_to_excel(trade_id, symbol, trade_type, current_price, market_type, "Closed",
                                       market_condition,
                                       ma_200, ma_21, ma_7, ma_5)  # Log trade
                    clear_last_trade_id()  # Clear the last trade ID after retrieving it

                    projector = Projector()  # This creates the instance
                    dictator = Dictator()


                    executor_logger.info(f"dictator instance created: {dictator}")
                    executor_logger.info(f"Projector instance created: {projector}")

                    try:
                        executor_logger.info("Calling calculate_profit_loss method.")  # Ensure method is called
                        projector.calculate_profit_loss()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during trade execution 1: {e}")

                    try:
                        executor_logger.info("Calling filter_open_trades method.")  # Ensure method is called
                        dictator.filter_open_trades()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during trade execution 2: {e}")

                    try:
                        executor_logger.info("Calling confid method.")  # Ensure method is called
                        executor_logger.info(f"Calling config method with ma_200={ma_200} (type: {type(ma_200)}), "
                                             f"ma_21={ma_21} (type: {type(ma_21)}), "
                                             f"ma_7={ma_7} (type: {type(ma_7)}), "
                                             f"ma_5={ma_5} (type: {type(ma_5)})")  # Log input values
                        Config.fetch_trade_data()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during config trade execution: {e}")

                    while not active_open_queue.empty():
                        # Completely clear the queue
                        with active_open_queue.mutex:
                            active_open_queue.queue.clear()
                    active_open_queue.put("0")  # Mark trade as inactive

                    executor_logger.info(f"Current active_open_queue: {list(active_open_queue.queue)}")
                    executor_logger.info("Trade marked as inactive.")
                    # Send a signal to resume monitoring
                    signal_queue.put("RESUME")
                    executor_logger.info("Monitoring resumed after trade execution.")
                elif current_price <= loss_threshold:
                    # If a trade needs to be closed, pause monitoring
                    signal_queue.put("PAUSE")
                    executor_logger.info("Monitoring paused while closing trade.")
                    executor_logger.info(f"Closing buy trade: Loss limit reached at {loss_threshold}")
                    hotkey.close_market_buy_trade()

                    executor_logger.info("Executed close_market_buy_trade().")
                    executor_logger.info("Clearing active trade queue before resetting status.")
                    trade_id = generate_trade_id(active_open_queue)  # Generate a unique ID

                    log_trade_to_excel(trade_id, symbol, trade_type, current_price, market_type, "Closed",
                                       market_condition,
                                       ma_200, ma_21, ma_7, ma_5)  # Log trade
                    clear_last_trade_id()  # Clear the last trade ID after retrieving it

                    projector = Projector()  # This creates the instance
                    dictator = Dictator()


                    executor_logger.info(f"dictator instance created: {dictator}")
                    executor_logger.info(f"Projector instance created: {projector}")

                    try:
                        executor_logger.info("Calling calculate_profit_loss method.")  # Ensure method is called
                        projector.calculate_profit_loss()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during trade execution: {e}")

                    try:
                        executor_logger.info("Calling filter_open_trades method.")  # Ensure method is called
                        dictator.filter_open_trades()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during trade execution: {e}")

                    try:
                        executor_logger.info("Calling config method.")  # Ensure method is called
                        executor_logger.info(f"Calling config method with ma_200={ma_200} (type: {type(ma_200)}), "
                                             f"ma_21={ma_21} (type: {type(ma_21)}), "
                                             f"ma_7={ma_7} (type: {type(ma_7)}), "
                                             f"ma_5={ma_5} (type: {type(ma_5)})")  # Log input values
                        Config.fetch_trade_data()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during config trade execution: {e}")

                    while not active_open_queue.empty():
                        # Completely clear the queue
                        with active_open_queue.mutex:
                            active_open_queue.queue.clear()
                    active_open_queue.put("0")  # Mark trade as inactive

                    executor_logger.info(f"Current active_open_queue: {list(active_open_queue.queue)}")
                    executor_logger.info("Trade marked as inactive.")
                    # Send a signal to resume monitoring
                    signal_queue.put("RESUME")
                    executor_logger.info("Monitoring resumed after trade execution.")
                else:
                    executor_logger.info("Trade closure conditions not met for buy trade. No action taken.")
                    return  # No need to close trade

    elif trade_type == 'market_sell':
        if not VALIDATOR_queue.empty():
            value = VALIDATOR_queue.queue[0]  # Peek at the first item without removing it
            if value != "PAUSE":
                executor_logger.info(f"validator queue:{VALIDATOR_queue}")

                if current_price <= profit_threshold:
                    # If a trade needs to be closed, pause monitoring
                    signal_queue.put("PAUSE")
                    executor_logger.info("Monitoring paused while closing trade.")
                    executor_logger.info(f"Closing sell trade: Profit target reached at {profit_threshold}")
                    hotkey.close_market_sell_trade()

                    executor_logger.info("Executed close_market_sell_trade().")
                    executor_logger.info("Clearing active trade queue before resetting status.")
                    trade_id = generate_trade_id(active_open_queue)  # Generate a unique ID

                    log_trade_to_excel(trade_id, symbol, trade_type, current_price, market_type, "Closed",
                                       market_condition,
                                       ma_200, ma_21, ma_7, ma_5)  # Log trade
                    clear_last_trade_id()  # Clear the last trade ID after retrieving it

                    projector = Projector()  # This creates the instance
                    dictator = Dictator()


                    executor_logger.info(f"dictator instance created: {dictator}")
                    executor_logger.info(f"Projector instance created: {projector}")

                    try:
                        executor_logger.info("Calling calculate_profit_loss method.")  # Ensure method is called
                        projector.calculate_profit_loss()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during trade execution: {e}")

                    try:
                        executor_logger.info("Calling filter_open_trades method.")  # Ensure method is called
                        dictator.filter_open_trades()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during config trade execution: {e}")

                    try:
                        executor_logger.info("Calling config method.")  # Ensure method is called
                        executor_logger.info(f"Calling config method with ma_200={ma_200} (type: {type(ma_200)}), "
                                             f"ma_21={ma_21} (type: {type(ma_21)}), "
                                             f"ma_7={ma_7} (type: {type(ma_7)}), "
                                             f"ma_5={ma_5} (type: {type(ma_5)})")  # Log input values
                        Config.fetch_trade_data()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during config trade execution: {e}")

                    while not active_open_queue.empty():
                        # Completely clear the queue
                        with active_open_queue.mutex:
                            active_open_queue.queue.clear()
                    active_open_queue.put("0")  # Mark trade as inactive

                    executor_logger.info(f"Current active_open_queue: {list(active_open_queue.queue)}")
                    executor_logger.info("Trade marked as inactive.")
                    # Send a signal to resume monitoring
                    signal_queue.put("RESUME")
                    executor_logger.info("Monitoring resumed after trade execution.")
                elif current_price >= loss_threshold:  # FIXED: Loss happens when price goes UP in a sell trade
                    executor_logger.info(f"Closing sell trade: Loss limit reached at {loss_threshold}")
                    hotkey.close_market_sell_trade()

                    executor_logger.info("Executed close_market_sell_trade().")
                    executor_logger.info("Clearing active trade queue before resetting status.")
                    trade_id = generate_trade_id(active_open_queue)  # Generate a unique ID

                    log_trade_to_excel(trade_id, symbol, trade_type, current_price, market_type, "Closed",
                                       market_condition,
                                       ma_200, ma_21, ma_7, ma_5)  # Log trade
                    clear_last_trade_id()  # Clear the last trade ID after retrieving it

                    projector = Projector()  # This creates the instance
                    dictator = Dictator()


                    executor_logger.info(f"dictator instance created: {dictator}")
                    executor_logger.info(f"Projector instance created: {projector}")

                    try:
                        executor_logger.info("Calling calculate_profit_loss method.")  # Ensure method is called
                        projector.calculate_profit_loss()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during trade execution: {e}")

                    try:
                        executor_logger.info("Calling filter_open_trades method.")  # Ensure method is called
                        dictator.filter_open_trades()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during trade execution: {e}")

                    try:
                        executor_logger.info("Calling config method.")  # Ensure method is called
                        executor_logger.info(f"Calling config method with ma_200={ma_200} (type: {type(ma_200)}), "
                                             f"ma_21={ma_21} (type: {type(ma_21)}), "
                                             f"ma_7={ma_7} (type: {type(ma_7)}), "
                                             f"ma_5={ma_5} (type: {type(ma_5)})")  # Log input values
                        Config.fetch_trade_data()  # This is the method being called
                    except Exception as e:
                        executor_logger.error(f"Error during config trade execution: {e}")

                    while not active_open_queue.empty():
                        # Completely clear the queue
                        with active_open_queue.mutex:
                            active_open_queue.queue.clear()
                    active_open_queue.put("0")  # Mark trade as inactive

                    executor_logger.info(f"Current active_open_queue: {list(active_open_queue.queue)}")
                    executor_logger.info("Trade marked as inactive.")
                    # Send a signal to resume monitoring
                    signal_queue.put("RESUME")
                    executor_logger.info("Monitoring resumed after trade execution.")
                else:
                    executor_logger.info("Trade closure conditions not met for sell trade. No action taken.")

                    return  # No need to close trade


