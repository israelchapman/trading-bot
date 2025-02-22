import json
import logging
import os
from common import load_settings
from bridge import Bridge

# Configure logging
closer_logger = logging.getLogger("closer")
closer_logger.setLevel(logging.DEBUG)

SETTINGS_FILE = "settings.json"


class TradeCloser:
    def __init__(self, active_open_queue, executor):
        self.active_open_queue = active_open_queue
        self.executor = executor  # Reference to the executor module
        self.bridge = Bridge()

    def load_last_trade_price(self):
        """Load the last trade price from settings.json"""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                try:
                    data = json.load(file)
                    if "trades" in data and data["trades"]:
                        return data["trades"][-1]["price"]
                except json.JSONDecodeError:
                    return None
        return None

    def check_and_close_trade(self, symbol, current_price):
        """Check if trade should be closed based on profit/loss thresholds."""
        if self.active_open_queue.qsize() == 0:
            return  # No active open trade

        settings = load_settings()
        last_trade_price = self.load_last_trade_price()

        if last_trade_price is None:
            closer_logger.warning("No last trade price found.")
            return

        profit_margin = float(settings.get("return_percentage", 0)) / 100
        loss_margin = float(settings.get("loss_risk_percentage", 0)) / 100

        profit_threshold = last_trade_price * (1 + profit_margin)
        loss_threshold = last_trade_price * (1 - loss_margin)

        if current_price >= profit_threshold:
            closer_logger.info(f"Closing trade: Profit target reached at {current_price}")
            self.executor.execute_trade(symbol, "close_market_sell")  # Example trade type

        elif current_price <= loss_threshold:
            closer_logger.info(f"Closing trade: Loss threshold reached at {current_price}")
            self.executor.execute_trade(symbol, "close_market_sell")  # Example trade type
