import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dictator")

# File paths
TRADE_LOG_FILE = "trade_log.xlsx"
PROJECTOR_FILE = "loss_trades.xlsx"
DICTATOR_OUTPUT_FILE = "dictator_output.xlsx"


class Dictator:
    logger.info("dictator script")

    @staticmethod
    def calculate_percentage(ma_value, price):
        """Calculate the percentage difference between a moving average and the price."""
        return round(((ma_value - price) / price) * 100, 2) if price else None

    @staticmethod
    def filter_open_trades():
        """Filter trades that are open and match trade IDs from projector output, then save them."""
        if not os.path.exists(TRADE_LOG_FILE) or not os.path.exists(PROJECTOR_FILE):
            logger.error("One or both required Excel files are missing.")
            return

        try:
            # Load trade log and projector output
            trade_log_df = pd.read_excel(TRADE_LOG_FILE, sheet_name="Trade Log")
            projector_df = pd.read_excel(PROJECTOR_FILE)

            # Get trade IDs from projector output
            valid_trade_ids = set(projector_df["Trade ID"].tolist())

            # Filter trade log for matching trade IDs with 'Open' status
            filtered_df = trade_log_df[
                (trade_log_df["Trade ID"].isin(valid_trade_ids)) & (trade_log_df["Status"] == "Open")
            ]

            if filtered_df.empty:
                logger.info("No matching open trades found.")
                return

            # Convert moving averages to percentage
            for ma in ["ma_200", "ma_21", "ma_7", "ma_5"]:
                if ma in filtered_df.columns:
                    filtered_df[f"{ma}_percentage"] = filtered_df.apply(
                        lambda row: Dictator.calculate_percentage(row[ma], row["Price"]), axis=1
                    )

            # Save the filtered data to a new Excel file
            filtered_df.to_excel(DICTATOR_OUTPUT_FILE, index=False)
            logger.info(f"Filtered open trades saved to {DICTATOR_OUTPUT_FILE}")

        except Exception as e:
            logger.error(f"Error processing trade logs: {e}")


if __name__ == "__main__":
    Dictator.filter_open_trades()
