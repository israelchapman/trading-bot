import executor
from bot import determine_market_condition, calculate_moving_averages, get_historical_prices, get_price_data, \
    calculate_market_pressure, get_current_ma
from bridge import Bridge
import time
import logging

# Configure logging to display logs in the terminal
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get the logger for monitor
monitor_logger = logging.getLogger("monitor")


def monitor_crypto(symbol, signal_queue, active_open_queue=None, active_sell_queue=None, interval='1m', market_type='spot', stop_event=None):
    monitor_logger.info("Starting crypto monitoring...")
    bridge = Bridge()  # Initialize Bridge instance once outside the loop

    while not stop_event.is_set():
        monitor_logger.debug("Monitor loop is active.")

        prices = get_historical_prices(symbol, interval, market_type=market_type)
        if prices.empty:
            monitor_logger.warning("No historical prices available, continuing...")
            time.sleep(5)  # Wait before retrying
            continue
        # monitor_logger.debug(f"Prices for {symbol}: {prices.head()}")

        prices = calculate_moving_averages(prices)
        current_price_data = get_price_data(symbol, market_type)
        current_price = current_price_data['current_price']

        # Retrieve moving averages
        ma_values = {
            5: get_current_ma(5),
            7: get_current_ma(7),
            21: get_current_ma(21),
            150: get_current_ma(150),
            200: get_current_ma(200),
        }

        # Calculate market pressure
        pressure = calculate_market_pressure(prices)
        monitor_logger.debug(
            f"Market Pressure - Bullish Avg: {pressure['bullish_avg']}, Bearish Avg: {pressure['bearish_avg']}")

        # Determine the new market condition
        market_condition = determine_market_condition(
            current_price,
            ma_values[5],
            ma_values[7],
            ma_values[21],
            ma_values[200]
        )

        # Log current and previous market conditions using the Bridge instance
        previous_market_condition = bridge.previous_market_condition
        monitor_logger.debug(f"Previous Market Condition: {previous_market_condition}")
        monitor_logger.debug(f"Current Market Condition: {market_condition}")

        # Check for market condition change and potential trades
        if previous_market_condition == 'Shortbull' and market_condition == 'Bearish':
            monitor_logger.debug("Condition change detected: shortbull to bearish")
        if market_condition == 'Bullish' and previous_market_condition == 'Shortbull':
            monitor_logger.debug("Condition change detected: shortbull to bullish")
        if market_condition == 'Bearish' and previous_market_condition == 'Longbear':
            monitor_logger.debug("Condition change detected: longbear to bearish")
        if market_condition == 'Bullish' and previous_market_condition == 'Longbear':
            monitor_logger.debug("Condition change detected: longbear to bullish")
        if market_condition == 'Longbear' and previous_market_condition == 'Bullish':
            monitor_logger.debug("Condition change detected: bullish to longbear")
        if market_condition == 'Shortbull' and previous_market_condition == 'Bearish':
            monitor_logger.debug("Condition change detected: bearish to shortbull")

        # Execute trades based on market conditions (open)
        if market_condition == 'Bullish' and previous_market_condition == 'Bullish':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute buy trade with amount: {amount}")
            if bridge.can_execute_trade('market_buy', amount=amount):
                monitor_logger.debug("Executing market buy trade...")
                executor.execute_trade(
                    trade_type='market_buy',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Bearish' and previous_market_condition == 'Bearish':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute sell trade with amount: {amount}")
            if bridge.can_execute_trade('market_sell', amount=amount):
                monitor_logger.debug("Executing market sell trade...")
                executor.execute_trade(
                    trade_type='market_sell',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Longbear' and previous_market_condition == 'Longbear':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute sell trade with amount: {amount}")
            if bridge.can_execute_trade('market_sell', amount=amount):
                monitor_logger.debug("Executing market sell trade...")
                executor.execute_trade(
                    trade_type='market_sell',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Shortbull' and previous_market_condition == 'Shortbull':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute buy trade with amount: {amount}")
            if bridge.can_execute_trade('market_buy', amount=amount):
                monitor_logger.debug("Executing market buy trade...")
                executor.execute_trade(
                    trade_type='market_buy',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Bullish' and previous_market_condition == 'Shortbull':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute buy trade with amount: {amount}")
            if bridge.can_execute_trade('market_buy', amount=amount):
                monitor_logger.debug("Executing market buy trade...")
                executor.execute_trade(
                    trade_type='market_buy',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Bearish' and previous_market_condition == 'Longbear':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute sell trade with amount: {amount}")
            if bridge.can_execute_trade('market_sell', amount=amount):
                monitor_logger.debug("Executing market sell trade...")
                executor.execute_trade(
                    trade_type='market_sell',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Shortbull' and previous_market_condition == 'Bearish':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute buy trade with amount: {amount}")
            if bridge.can_execute_trade('market_buy', amount=amount):
                monitor_logger.debug("Executing market buy trade...")
                executor.execute_trade(
                    trade_type='market_buy',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Bullish' and previous_market_condition == 'Longbear':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute buy trade with amount: {amount}")
            if bridge.can_execute_trade('market_buy', amount=amount):
                monitor_logger.debug("Executing market buy trade...")
                executor.execute_trade(
                    trade_type='market_buy',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Longbear' and previous_market_condition == 'Bullish':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute sell trade with amount: {amount}")
            if bridge.can_execute_trade('market_sell', amount=amount):
                monitor_logger.debug("Executing market sell trade...")
                executor.execute_trade(
                    trade_type='market_sell',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        if market_condition == 'Bearish' and previous_market_condition == 'Shortbull':
            amount = bridge.get_traded_amount()
            monitor_logger.debug(f"Attempting to execute sell trade with amount: {amount}")
            if bridge.can_execute_trade('market_sell', amount=amount):
                monitor_logger.debug("Executing market sell trade...")
                executor.execute_trade(
                    trade_type='market_sell',
                    symbol=symbol,
                    market_type=market_type,
                    signal_queue=signal_queue,
                    active_open_queue=active_open_queue,
                    active_sell_queue=active_sell_queue,
                    market_condition=market_condition,
                    ma_200=ma_values[200],
                    ma_21=ma_values[21],
                    ma_7=ma_values[7],
                    ma_5=ma_values[5]
                )
        # Update the market condition in Bridge
        bridge.set_market_condition(market_condition)  # Update market condition in Bridge

        monitor_logger.debug(f"Updated Bridge Market Condition: {market_condition}")
        time.sleep(1)  # Wait before the next iteration

    monitor_logger.debug("Monitor loop has stopped.")
