import pandas as pd
import time
import logging
from bot import determine_market_condition, calculate_moving_averages
from common import load_settings

# Define intervals to fetch data for
INTERVALS = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class Config:
    @staticmethod
    def fetch_trade_data():
        """Fetches trade data for all intervals and appends it to an Excel file."""

        logger.info("Entered fetch_trade_data method.")
        settings = load_settings()
        symbol = settings.get('symbol', 'BTCUSDT')
        market_type = settings.get('market_type', 'spot')
        trade_id = settings.get('last_trade_id', 'N/A')

        all_data = []

        for interval in INTERVALS:
            # Get historical price data and moving averages for the interval
            ma_values = calculate_moving_averages(symbol, interval)
            if not isinstance(ma_values, dict):  # Ensure it returns a dictionary
                logger.warning(f"Failed to fetch moving averages for {symbol} at interval {interval}. Skipping.")
                continue
            # Log ma_values to inspect what it contains
            logger.info(f"ma_values: {ma_values} (type: {type(ma_values)})")

            try:
                # Extract moving averages from the dictionary
                ma_200 = ma_values.get(200)
                ma_21 = ma_values.get(21)
                ma_7 = ma_values.get(7)
                ma_5 = ma_values.get(5)
            except KeyError as e:
                logger.error(f"Missing key in moving averages for interval {interval}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error extracting moving averages for {interval}: {e}")
                continue

            # Check if any moving averages are missing
            if None in [ma_200, ma_21, ma_7, ma_5]:
                logger.warning(f"Skipping interval {interval} due to missing MA values.")
                continue

            # Determine market condition based on moving averages
            market_condition = determine_market_condition(symbol, ma_200, ma_21, ma_7, ma_5)

            # Ensure the last price is included in the data
            current_price = ma_values.get("last_price")
            if current_price is None:
                logger.warning(f"Skipping interval {interval} due to missing last price.")
                continue

            data_entry = {
                'Symbol': symbol,
                'Interval': interval,
                'Market Type': market_type,
                'Trade ID': trade_id,
                'Price': current_price,
                'Market Condition': market_condition,
                'Current Price': current_price,
                'MA_200': ma_200,
                'MA_21': ma_21,
                'MA_7': ma_7,
                'MA_5': ma_5,
                'Timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            all_data.append(data_entry)

        # Create a DataFrame with all collected data
        df = pd.DataFrame(all_data)

        # Append to Excel file, creating if it doesn't exist
        try:
            existing_df = pd.read_excel('trade_data.xlsx')
            logger.info(f"Existing file found with {existing_df.shape[0]} rows.")
            df = pd.concat([existing_df, df], ignore_index=True)
        except FileNotFoundError:
            logger.info("No existing trade_data.xlsx file. Creating a new one.")

        # Save the updated DataFrame to Excel
        df.to_excel('trade_data.xlsx', index=False)
        logger.info("Trade data successfully logged.")

if __name__ == "__main__":
    Config.fetch_trade_data()  # Static method, no need for an instance
