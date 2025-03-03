import os
import pandas as pd
import logging
import json
import common

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("projector")

EXCEL_FILE = "trade_log.xlsx"
LOSS_FILE = "loss_trades.xlsx"
SETTINGS_FILE = "settings.json"


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
        logger.info("Entered calculate_profit_loss method.")

        return_percentage, loss_risk_percentage = load_settings()
        settings = common.load_settings()
        interval = settings.get("interval")

        try:
            # Load trade log
            df = pd.read_excel(EXCEL_FILE, sheet_name="Trade Log")

            # Ensure required columns exist
            required_columns = {"Trade ID", "Trade Type", "Price", "Status"}
            if not required_columns.issubset(df.columns):
                logger.error("Missing required columns in Excel file.")
                return

            # Sort by index (assuming the latest trades are at the bottom)
            df = df.sort_index(ascending=False)

            # Find the last opened and closed trade with matching Trade ID
            last_trade_id = None
            last_open_trade = None
            last_close_trade = None

            for _, row in df.iterrows():
                trade_id = row["Trade ID"]
                if row["Status"] == "Opened" and last_open_trade is None:
                    last_open_trade = row
                elif row["Status"] == "Closed" and last_close_trade is None:
                    last_close_trade = row

                if last_open_trade is not None and last_close_trade is not None:
                    if last_open_trade["Trade ID"] == last_close_trade["Trade ID"]:
                        last_trade_id = last_open_trade["Trade ID"]
                        break

            if last_trade_id is None:
                logger.warning("No matching open and close trades found.")
                return

            # Process the last matched open-close pair
            open_price = last_open_trade["Price"]
            close_price = last_close_trade["Price"]
            trade_type = last_open_trade["Trade Type"]

            if trade_type == "market_buy":
                profit_loss = close_price - open_price
            elif trade_type == "market_sell":
                profit_loss = open_price - close_price
            else:
                logger.warning(f"Unrecognized trade type {trade_type} for Trade ID {last_trade_id}.")
                return

            status = "Profit" if profit_loss > 0 else "Loss"
            logger.info(f"Trade ID {last_trade_id}: {status} ({profit_loss:.2f})")

            # Store loss trades
            if profit_loss < 0:
                loss_trade = {
                    "Trade ID": last_trade_id,
                    "Trade Type": trade_type,
                    "Open Price": open_price,
                    "Close Price": close_price,
                    "Profit/Loss": profit_loss,
                    "Status": status,
                    "return percentage": return_percentage,
                    "loss risk percentage": loss_risk_percentage,
                    "interval": interval
                }

                # Save the last loss trade without overwriting previous ones
                if os.path.exists(LOSS_FILE):
                    existing_loss_df = pd.read_excel(LOSS_FILE, sheet_name="Loss Trades")
                    new_loss_df = pd.DataFrame([loss_trade])

                    # Remove duplicates before saving
                    combined_loss_df = pd.concat([existing_loss_df, new_loss_df]).drop_duplicates(subset=["Trade ID"], keep="first")
                else:
                    combined_loss_df = pd.DataFrame([loss_trade])

                if not combined_loss_df.empty:
                    with pd.ExcelWriter(LOSS_FILE, engine="openpyxl", mode="w") as writer:
                        combined_loss_df.to_excel(writer, index=False, sheet_name="Loss Trades")

        except Exception as e:
            logger.error(f"Error processing trade log: {e}")


if __name__ == "__main__":
    projector = Projector()
    projector.calculate_profit_loss()
