import os
import pandas as pd
import logging
import json
import common
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("projector")

EXCEL_FILE = "trade_log.xlsx"
LOSS_FILE = "loss_trades.xlsx"  # New file to store loss trades
SETTINGS_FILE = "settings.json"  # JSON file for profit/risk loss margins


def load_settings():
    """Load profit margin and risk loss margin from settings.json."""
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        return settings.get("return_percentage", 0), settings.get("loss_risk_percentage", 0)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading settings: {e}")
        return 0, 0  # Default to 0 if settings file is missing or corrupted


class Projector:

    def calculate_profit_loss(self):
        logger.info("Entered calculate_profit_loss method.")  # Check if this shows up

        # Load profit margin and risk loss margin
        return_percentage, loss_risk_percentage = load_settings()
        settings = common.load_settings()  # Load settings as a dictionary
        interval = settings.get("interval")  # Extract interval safely

        try:
            # Load the trade log
            df = pd.read_excel(EXCEL_FILE, sheet_name="Trade Log")

            # Ensure required columns exist
            required_columns = {"Trade ID", "Trade Type", "Price", "Status", "interval"}
            if not required_columns.issubset(df.columns):
                logger.error("Missing required columns in Excel file.")
                return

            # Group trades by Trade ID
            grouped = df.groupby("Trade ID")
            loss_trades = []  # List to store loss trades for saving

            for trade_id, group in grouped:
                if len(group) != 2:
                    logger.warning(f"Trade ID {trade_id} does not have a matching open and close entry.")
                    continue

                open_trade = group[group["Status"] == "Opened"].iloc[0]
                close_trade = group[group["Status"] == "Closed"].iloc[0]

                open_price = open_trade["Price"]
                close_price = close_trade["Price"]
                trade_type = open_trade["Trade Type"]

                if trade_type == "market_buy":
                    profit_loss = close_price - open_price
                elif trade_type == "market_sell":
                    profit_loss = open_price - close_price
                else:
                    logger.warning(f"Unrecognized trade type {trade_type} for Trade ID {trade_id}.")
                    continue

                status = "Profit" if profit_loss > 0 else "Loss"
                logger.info(f"Trade ID {trade_id}: {status} ({profit_loss:.2f})")

                # Store loss trades
                if profit_loss < 0:
                    loss_trades.append({
                        "Trade ID": trade_id,
                        "Trade Type": trade_type,
                        "Open Price": open_price,
                        "Close Price": close_price,
                        "Profit/Loss": profit_loss,
                        "Status": status,
                        "return percentage": return_percentage,
                        "loss risk percentage": loss_risk_percentage,
                        "interval": interval
                    })

                    # Load existing loss trades and filter duplicates
                if os.path.exists(LOSS_FILE):
                    existing_loss_df = pd.read_excel(LOSS_FILE, sheet_name="Loss Trades")
                    new_loss_df = pd.DataFrame(loss_trades)

                    # Remove duplicates before saving
                    combined_loss_df = pd.concat([existing_loss_df, new_loss_df]).drop_duplicates(subset=["Trade ID"],
                                                                                                  keep="first")
                else:
                    combined_loss_df = pd.DataFrame(loss_trades)

                if not combined_loss_df.empty:
                    with pd.ExcelWriter(LOSS_FILE, engine="openpyxl", mode="w") as writer:
                        combined_loss_df.to_excel(writer, index=False, sheet_name="Loss Trades")
                    logger.info(f"Loss trades updated and saved to {LOSS_FILE}")

        except Exception as e:
            logger.error(f"Error processing trade log: {e}")


if __name__ == "__main__":
    projector = Projector()  # Instantiate the Projector class
    projector.calculate_profit_loss()  # Call the method
