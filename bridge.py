import logging
from threading import Lock
from bot import determine_market_condition
from common import load_settings

# Create a logger specifically for the Bridge script
bridge_logger = logging.getLogger("bridge")
bridge_logger.setLevel(logging.DEBUG)

# Prevent logs from propagating to the root logger
bridge_logger.propagate = False

# Prevent adding duplicate handlers
if not bridge_logger.handlers:
    # Create a handler for the terminal
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Create a formatter for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    bridge_logger.addHandler(handler)


class Bridge:
    def __init__(self, current_price=None, ma_5=None, ma_7=None, ma_21=None, ma_200=None):
        self.lock = Lock()
        self.market_condition = None
        self.previous_market_condition = None

        # Initialize market condition if parameters are provided
        if (current_price is not None and
                ma_5 is not None and
                ma_7 is not None and
                ma_21 is not None and
                ma_200 is not None):
            self.market_condition = determine_market_condition(
                current_price, ma_5, ma_7, ma_21, ma_200
            )

    def log(self, message):
        """Log message to console and return it for GUI use."""
        bridge_logger.debug(message)
        return message

    def set_market_condition(self, condition):
        with self.lock:
            self.log(
                f"Current Condition Before Update: {self.market_condition}, "
                f"Previous Condition: {self.previous_market_condition}"
            )
            self.previous_market_condition = self.market_condition
            self.market_condition = condition
            self.log(
                f"Updated Market Condition: {self.market_condition}, "
                f"Previous Condition: {self.previous_market_condition}"
            )

    def can_execute_trade(self, trade_type, amount, limit_price=None):

        self.log(f"Checking if trade can be executed: Type: {trade_type}, Amount: {amount}, Limit Price: {limit_price}")

        if self.previous_market_condition == self.market_condition:
            if trade_type in ['market_buy', 'limit_buy', 'market_sell', 'limit_sell']:
                self.log(f"Market condition remains {self.market_condition}; executing trade: {trade_type}.")
                return True

        hotkey_options = self.get_hotkey_options()
        if trade_type not in hotkey_options:
            self.log(f"Trade type '{trade_type}' is not allowed in the current market condition.")
            return False

        if amount <= 0:
            self.log("Trade amount must be greater than zero.")
            return False

        if 'limit' in trade_type and limit_price is None:
            self.log("Limit price must be provided for limit trades.")
            return False

        self.log("Trade can be executed.")
        return True

    def get_hotkey_options(self):
        self.log(f"Debug: Entered get_hotkey_options with market_condition = {self.market_condition}")

        if self.market_condition in ['Bullish', 'Shortbull']:
            options = ['market_buy', 'limit_buy']
        elif self.market_condition in ['Bearish', 'Longbear']:
            options = ['market_sell', 'limit_sell']
        else:
            options = []

        self.log(f"Debug: get_hotkey_options is returning: {options}")
        return options

    def get_traded_amount(self):
        self.log("Trying to get traded amount")
        settings = load_settings()
        return float(settings.get('amount', 1))  # Ensure amount is a float

    @staticmethod
    def gather_trade_data():
        settings = load_settings()
        return {
            'trade_type': settings.get('trade_type', 'market'),
            'amount': settings.get('amount', '1'),
            'limit_price': None
        }
