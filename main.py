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
        if price:
            percentage = round(((ma_value - price) / price) * 100, 2)
            logger.debug(f"Calculated percentage: {percentage}% for MA: {ma_value}, Price: {price}")
            return percentage
        return None

    def filter_open_trades(self):
        """Filter trades that are open and match trade IDs from projector output, then save them."""
        if not os.path.exists(TRADE_LOG_FILE) or not os.path.exists(PROJECTOR_FILE):
            logger.error("One or both required Excel files are missing.")
            return

        try:
            logger.info("Loading trade log and projector output files...")
            trade_log_df = pd.read_excel(TRADE_LOG_FILE, sheet_name="Trade Log")
            projector_df = pd.read_excel(PROJECTOR_FILE)

            logger.info(f"Loaded {len(trade_log_df)} records from trade log.")
            logger.info(f"Loaded {len(projector_df)} records from projector output.")

            # Log Trade IDs from both dataframes
            logger.info(f"Trade Log Trade IDs: {trade_log_df[['Trade ID', 'Status']].to_dict(orient='records')}")
            logger.info(f"Projector Output Trade IDs: {projector_df['Trade ID'].tolist()}")

            # Get trade IDs from projector output
            valid_trade_ids = set(projector_df["Trade ID"].tolist())
            logger.info(f"Extracted {len(valid_trade_ids)} unique trade IDs from projector output.")

            # Ensure column names match
            logger.info(f"Trade log columns: {trade_log_df.columns.tolist()}")
            logger.info(f"Projector columns: {projector_df.columns.tolist()}")

            # Filter trade log for matching trade IDs with 'Open' status
            trade_log_df["Trade ID"] = trade_log_df["Trade ID"].astype(str)
            valid_trade_ids = set(map(str, valid_trade_ids))  # Convert valid trade IDs to strings
            trade_log_df["Status"] = trade_log_df["Status"].str.strip().str.capitalize()
            matching_trade_ids_df = trade_log_df[trade_log_df["Trade ID"].isin(valid_trade_ids)]
            matching_open_status_df = trade_log_df[trade_log_df["Status"] == "Open"]

            logger.info(f"Rows Matching Trade IDs: {len(matching_trade_ids_df)}")
            logger.info(f"Rows with Status 'Open': {len(matching_open_status_df)}")

            filtered_df = trade_log_df[
                (trade_log_df["Trade ID"].isin(valid_trade_ids)) & (trade_log_df["Status"] == "Open")
            ]

            logger.info(f"Filtered {len(filtered_df)} matching open trades.")

            if filtered_df.empty:
                logger.info("No matching open trades found.")
                return

            # Convert moving averages to percentage
            for ma in ["ma_200", "ma_21", "ma_7", "ma_5"]:
                if ma in filtered_df.columns:
                    logger.info(f"Converting {ma} values to percentages...")
                    filtered_df[f"{ma}_percentage"] = filtered_df.apply(
                        lambda row: self.calculate_percentage(row[ma], row["Price"]), axis=1
                    )

            # Save the filtered data to a new Excel file
            filtered_df.to_excel(DICTATOR_OUTPUT_FILE, index=False)
            logger.info(f"Saved {len(filtered_df)} filtered open trades to {DICTATOR_OUTPUT_FILE}")

        except Exception as e:
            logger.error(f"Error processing trade logs: {e}")


if __name__ == "__main__":
    dictator = Dictator()
    dictator.filter_open_trades()
