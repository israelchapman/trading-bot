import pyautogui
import time
import common
from common import settings_file
import logging

# Configure logging to display logs in the terminal
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get the logger for hotkey actions
hotkey_logger = logging.getLogger("hotkey")

# Global variable to store the default amount for the session
DEFAULT_AMOUNT = None


# Function to perform a limit sell trade with the required steps
def limit_sell_trade():
    hotkey_logger.info("Limit Sell Trade function called.")
    try:
        # Step 1: Click "Open"
        hotkey_logger.info("Clicking 'Open' button...")
        pyautogui.moveTo(1615, 262)  # Adjust the coordinates to the "Open" button
        pyautogui.click()
        time.sleep(0.1)

        # Step 2: Click "Limit"
        hotkey_logger.info("Clicking 'Limit' option...")
        pyautogui.moveTo(1544, 326)  # Adjust the coordinates to the "Limit" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2b: Click "last price"
        hotkey_logger.info("Clicking 'last price' option...")
        pyautogui.moveTo(1848, 465)  # Adjust the coordinates to the "Last price" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2c: Click "limit price"
        hotkey_logger.info("Clicking 'limit price' option...")
        pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the "limit price" option
        pyautogui.doubleClick()
        time.sleep(0.1)

        # Copy the value automatically
        pyautogui.hotkey('ctrl', 'c')  # Simulates pressing Ctrl+C to copy the selected value
        time.sleep(0.1)

        # Step 3: Show combined input box for limit price and amount
        limit_price = int(settings_file.get('limit_price', 0))  # Convert to int if necessary
        amount = float(settings_file.get('amount', 0))

        # Ensure valid inputs were entered
        if amount is not None:
            # Step 4: Double-Click on the limit price input field to select all text (only if limit_price is provided)
            if limit_price is not None:  # Check if limit_price is provided
                hotkey_logger.info(f"Entering limit price: {limit_price}")
                pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the Limit Price input field
                pyautogui.doubleClick()  # Double-click to select all existing text
                pyautogui.write(str(limit_price))  # Enter the limit price
                time.sleep(0.5)
            else:
                hotkey_logger.info("Limit price is left blank. Skipping entry for limit price.")

            # Step 5: Double-Click on the amount input field to select all text
            hotkey_logger.info(f"Entering amount: {amount}")
            pyautogui.moveTo(1634, 569)  # Adjust the coordinates to the Amount input field
            pyautogui.doubleClick()      # Double-click to select all existing text
            pyautogui.write(str(amount))  # Enter the amount
            time.sleep(0.5)

            # Step 6: Click "Open" button again
            hotkey_logger.info("Clicking 'Open' button again...")
            pyautogui.moveTo(1800, 879)  # Adjust the coordinates to the "Open" button
            pyautogui.click()
            time.sleep(1)

            # Step 7: Click "Confirm" button
            hotkey_logger.info("Clicking 'Confirm' button...")
            # Uncomment and set accurate coordinates for the "Confirm" button
            pyautogui.moveTo(1046, 797)
            pyautogui.click()
            time.sleep(1)

            hotkey_logger.info("Limit sell executed.")
        else:
            hotkey_logger.info("Invalid limit price or amount. Trade not executed.")
    except Exception as e:
        hotkey_logger.info(f"An error occurred during limit sell: {e}")


# Function to perform a limit buy trade with the required steps
def limit_buy_trade():
    hotkey_logger.info("Limit Buy Trade function called.")
    try:
        # Step 1: Click "Open"
        hotkey_logger.info("Clicking 'Open' button...")
        pyautogui.moveTo(1615, 262)  # Adjust the coordinates to the "Open" button
        pyautogui.click()
        time.sleep(0.1)

        # Step 2: Click "Limit"
        hotkey_logger.info("Clicking 'Limit' option...")
        pyautogui.moveTo(1544, 326)  # Adjust the coordinates to the "Limit" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2b: Click "last price"
        hotkey_logger.info("Clicking 'last price' option...")
        pyautogui.moveTo(1848, 465)  # Adjust the coordinates to the "Last price" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2c: Click "limit price"
        hotkey_logger.info("Clicking 'limit price' option...")
        pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the "limit price" option
        pyautogui.doubleClick()
        time.sleep(0.1)

        # Copy the value automatically
        pyautogui.hotkey('ctrl', 'c')  # Simulates pressing Ctrl+C to copy the selected value
        time.sleep(0.1)

        # Step 3: Show combined input box for limit price and amount
        limit_price, amount = settings_file

        # Ensure valid inputs were entered
        if amount is not None:
            # Step 4: Double-Click on the limit price input field to select all text (only if limit_price is provided)
            if limit_price is not None:  # Check if limit_price is provided
                hotkey_logger.info(f"Entering limit price: {limit_price}")
                pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the Limit Price input field
                pyautogui.doubleClick()      # Double-click to select all existing text
                pyautogui.write(str(limit_price))  # Enter the limit price
                time.sleep(0.5)
            else:
                hotkey_logger.info("Limit price is left blank. Skipping entry for limit price.")

            # Step 5: Double-Click on the amount input field to select all text
            hotkey_logger.info(f"Entering amount: {amount}")
            pyautogui.moveTo(1634, 569)  # Adjust the coordinates to the Amount input field
            pyautogui.doubleClick()      # Double-click to select all existing text
            pyautogui.write(str(amount))  # Enter the amount
            time.sleep(0.5)

            # Step 6: Click "Open" button again
            hotkey_logger.info("Clicking 'Open' button again...")
            pyautogui.moveTo(1635, 877)  # Adjust the coordinates to the "Open" button
            pyautogui.click()
            time.sleep(1)

            # Step 7: Click "Confirm" button
            hotkey_logger.info("Clicking 'Confirm' button...")
            # Uncomment and set accurate coordinates for the "Confirm" button
            pyautogui.moveTo(1046, 797)
            pyautogui.click()
            time.sleep(1)

            hotkey_logger.info("Limit buy executed.")
        else:
            hotkey_logger.info("Invalid amount. Trade not executed.")
    except Exception as e:
        hotkey_logger.info(f"An error occurred during limit buy: {e}")


# Function to perform a market buy trade
def market_buy_trade():
    hotkey_logger.info("Market Buy Trade function called.")
    # Load settings from settings.json
    settings = common.load_settings()
    try:
        # Step 1: Click "Open"
        hotkey_logger.info("Clicking 'Open' button...")
        pyautogui.moveTo(1615, 262)  # Adjust the coordinates to the "Open" button
        pyautogui.click()
        time.sleep(0.1)

        # Step 2: Click "Market"
        hotkey_logger.info("Clicking 'Market' option...")
        pyautogui.moveTo(1602, 321)  # Adjust the coordinates to the "Market" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 3: Show input box for amount
        amount = settings.get("amount", None)

        # Ensure valid inputs were entered
        if amount is not None:
            # Step 4: Enter the amount without confirmation
            hotkey_logger.info(f"Entering amount: {amount}")
            pyautogui.moveTo(1634, 569)  # Adjust the coordinates to the Amount input field
            pyautogui.doubleClick()      # Double-click to select all existing text
            pyautogui.write(str(amount))  # Enter the amount
            time.sleep(0.5)

            # Step 5: Click "Open" button again
            hotkey_logger.info("Clicking 'Open' button again...")
            pyautogui.moveTo(1635, 877)  # Adjust the coordinates to the "Open" button
            pyautogui.click()
            time.sleep(1)

            # Step 6: Click "Confirm" button
            hotkey_logger.info("Clicking 'Confirm' button...")
            # Uncomment and set accurate coordinates for the "Confirm" button
            pyautogui.moveTo(1046, 797)
            pyautogui.click()
            time.sleep(1)

            hotkey_logger.info("Market buy executed.")
        else:
            hotkey_logger.info("Invalid amount. Trade not executed.")
    except Exception as e:
        hotkey_logger.info(f"An error occurred during market buy: {e}")


# Function to perform a market sell trade
def market_sell_trade():
    hotkey_logger.info("Market Sell Trade function called.")
    # Load settings from settings.json
    settings = common.load_settings()

    try:
        # Step 1: Click "Open"
        hotkey_logger.info("Clicking 'Open' button...")
        pyautogui.moveTo(1615, 262)  # Adjust the coordinates to the "Open" button
        pyautogui.click()
        time.sleep(0.1)

        # Step 2: Click "Market"
        hotkey_logger.info("Clicking 'Market' option...")
        pyautogui.moveTo(1602, 321)  # Adjust the coordinates to the "Market" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 3: Show input box for amount
        amount = settings.get("amount", None)

        # Ensure valid inputs were entered
        if amount is not None:
            # Step 4: Enter the amount without confirmation
            hotkey_logger.info(f"Entering amount: {amount}")
            pyautogui.moveTo(1634, 569)  # Adjust the coordinates to the Amount input field
            pyautogui.doubleClick()      # Double-click to select all existing text
            pyautogui.write(str(amount))  # Enter the amount
            time.sleep(0.5)

            # Step 5: Click "Open" button again
            hotkey_logger.info("Clicking 'Open' button again...")
            pyautogui.moveTo(1800, 879)  # Adjust the coordinates to the "Open" button
            pyautogui.click()
            time.sleep(1)

            # Step 6: Click "Confirm" button
            hotkey_logger.info("Clicking 'Confirm' button...")
            # Uncomment and set accurate coordinates for the "Confirm" button
            pyautogui.moveTo(1046, 797)
            pyautogui.click()
            time.sleep(1)

            hotkey_logger.info("Market sell executed.")
        else:
            hotkey_logger.info("Invalid amount. Trade not executed.")
    except Exception as e:
        hotkey_logger.info(f"An error occurred during market sell: {e}")


# Function to close market order long
def close_market_buy_trade():
    hotkey_logger.info("Close Market Buy Trade function called.")
    try:
        # Step 1: Click "Close"
        hotkey_logger.info("Clicking 'Close' button...")
        pyautogui.moveTo(1785, 262)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(0.1)

        # Step 2: Click "Market"
        hotkey_logger.info("Clicking 'Market' option...")
        pyautogui.moveTo(1602, 321)  # Adjust the coordinates to the "Market" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 6: Click "100%" button again
        hotkey_logger.info("Clicking '100%' button...")
        pyautogui.moveTo(1875, 624)  # Adjust the coordinates to the "100%" button
        pyautogui.click()
        time.sleep(1)

        # Step 6b: Click "Close" button again
        hotkey_logger.info("Clicking 'Close' button again...")
        pyautogui.moveTo(1797, 744)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(1)

        # Step 7: Click "Confirm" button
        hotkey_logger.info("Clicking 'Confirm' button...")
        # Uncomment and set accurate coordinates for the "Confirm" button
        pyautogui.moveTo(1097, 773)
        pyautogui.click()
        time.sleep(1)

        hotkey_logger.info("Close limit sell executed.")

    except Exception as e:
        hotkey_logger.info(f"An error occurred during close limit sell: {e}")


# Function to close market order short
def close_market_sell_trade():
    hotkey_logger.info("Close Market sell Trade function called.")
    try:
        # Step 1: Click "Close"
        hotkey_logger.info("Clicking 'Close' button...")
        pyautogui.moveTo(1785, 262)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(0.1)

        # Step 2: Click "Market"
        hotkey_logger.info("Clicking 'Market' option...")
        pyautogui.moveTo(1602, 321)  # Adjust the coordinates to the "Market" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 6: Click "100%" button again
        hotkey_logger.info("Clicking '100%' button...")
        pyautogui.moveTo(1875, 624)  # Adjust the coordinates to the "100%" button
        pyautogui.click()
        time.sleep(1)

        # Step 6b: Click "Close" button again
        hotkey_logger.info("Clicking 'Close' button again...")
        pyautogui.moveTo(1615, 744)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(1)

        # Step 7: Click "Confirm" button
        hotkey_logger.info("Clicking 'Confirm' button...")
        # Uncomment and set accurate coordinates for the "Confirm" button
        pyautogui.moveTo(1097, 773)
        pyautogui.click()
        time.sleep(1)

        hotkey_logger.info("Close limit sell executed.")

    except Exception as e:
        hotkey_logger.info(f"An error occurred during close limit sell: {e}")


# Function to close limit order long
def close_limit_buy_trade():
    hotkey_logger.info("Close Limit Buy Trade function called.")
    try:
        # Step 1: Click "Close"
        hotkey_logger.info("Clicking 'Close' button...")
        pyautogui.moveTo(1790, 265)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(0.1)  # Wait for UI to respond

        # Step 2: Click "Limit"
        hotkey_logger.info("Clicking 'Limit' option...")
        pyautogui.moveTo(1544, 326)  # Adjust the coordinates to the "Limit" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2b: Click "last price"
        hotkey_logger.info("Clicking 'last price' option...")
        pyautogui.moveTo(1848, 465)  # Adjust the coordinates to the "Last price" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2c: Click "limit price"
        hotkey_logger.info("Clicking 'limit price' option...")
        pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the "limit price" option
        pyautogui.doubleClick()
        time.sleep(0.1)

        # Copy the value automatically
        pyautogui.hotkey('ctrl', 'c')  # Simulates pressing Ctrl+C to copy the selected value
        time.sleep(0.1)

        # Step 3: Show combined input box for limit price and amount
        limit_price, amount = settings_file

        # Step 4: Double-Click on the limit price input field to select all text (only if limit_price is provided)
        if limit_price is not None:  # Check if limit_price is provided
            hotkey_logger.info(f"Entering limit price: {limit_price}")
            pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the Limit Price input field
            pyautogui.doubleClick()  # Double-click to select all existing text
            pyautogui.write(str(limit_price))  # Enter the limit price
            time.sleep(0.5)
        else:
            hotkey_logger.info("Limit price is left blank. Skipping entry for limit price.")

        # Step 5: Double-Click on the amount input field to select all text (only if amount is provided)
        if amount is not None:  # Only proceed if amount is provided
            hotkey_logger.info(f"Entering amount: {amount}")
            pyautogui.moveTo(1634, 569)  # Adjust the coordinates to the Amount input field
            pyautogui.doubleClick()  # Double-click to select all existing text
            pyautogui.write(str(amount))  # Enter the amount
            time.sleep(0.5)
        else:
            hotkey_logger.info("Amount is left blank. Skipping entry for amount.")

        # Step 6: Click "100%" button again
        if amount is None:  # Check if amount is not provided
            hotkey_logger.info("Clicking 'Close' button again...")
            pyautogui.moveTo(1880, 625)  # Adjust the coordinates to the "100%" button
            pyautogui.click()
            time.sleep(1)

        # Step 6b: Click "Close" button again
        hotkey_logger.info("Clicking 'Close' button again...")
        pyautogui.moveTo(1797, 744)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(1)

        # Step 7: Click "Confirm" button
        hotkey_logger.info("Clicking 'Confirm' button...")
        # Uncomment and set accurate coordinates for the "Confirm" button
        pyautogui.moveTo(1046, 797)
        pyautogui.click()
        time.sleep(1)

        hotkey_logger.info("Close limit sell executed.")

    except Exception as e:
        hotkey_logger.info(f"An error occurred during close limit sell: {e}")


# Function to close limit order short
def close_limit_sell_trade():
    hotkey_logger.info("Close Limit Sell Trade function called.")
    try:
        # Step 1: Click "Close"
        hotkey_logger.info("Clicking 'Close' button...")
        pyautogui.moveTo(1790, 265)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(0.1)  # Wait for UI to respond

        # Step 2: Click "Limit"
        hotkey_logger.info("Clicking 'Limit' option...")
        pyautogui.moveTo(1544, 326)  # Adjust the coordinates to the "Limit" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2b: Click "last price"
        hotkey_logger.info("Clicking 'last price' option...")
        pyautogui.moveTo(1848, 465)  # Adjust the coordinates to the "Last price" option
        pyautogui.click()
        time.sleep(0.1)

        # Step 2c: Click "limit price"
        hotkey_logger.info("Clicking 'limit price' option...")
        pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the "limit price" option
        pyautogui.doubleClick()
        time.sleep(0.1)

        # Copy the value automatically
        pyautogui.hotkey('ctrl', 'c')  # Simulates pressing Ctrl+C to copy the selected value
        time.sleep(0.1)

        # Step 3: Show combined input box for limit price and amount
        limit_price, amount = settings_file

        # Step 4: Double-Click on the limit price input field to select all text (only if limit_price is provided)
        if limit_price is not None:  # Check if limit_price is provided
            hotkey_logger.info(f"Entering limit price: {limit_price}")
            pyautogui.moveTo(1650, 462)  # Adjust the coordinates to the Limit Price input field
            pyautogui.doubleClick()  # Double-click to select all existing text
            pyautogui.write(str(limit_price))  # Enter the limit price
            time.sleep(0.5)
        else:
            hotkey_logger.info("Limit price is left blank. Skipping entry for limit price.")

        # Step 5: Double-Click on the amount input field to select all text (only if amount is provided)
        if amount is not None:  # Only proceed if amount is provided
            hotkey_logger.info(f"Entering amount: {amount}")
            pyautogui.moveTo(1634, 569)  # Adjust the coordinates to the Amount input field
            pyautogui.doubleClick()  # Double-click to select all existing text
            pyautogui.write(str(amount))  # Enter the amount
            time.sleep(0.5)
        else:
            hotkey_logger.info("Amount is left blank. Skipping entry for amount.")

        # Step 6: Click "100%" button again
        if amount is None:  # Check if amount is not provided
            hotkey_logger.info("Clicking 'Close' button again...")
            pyautogui.moveTo(1880, 625)  # Adjust the coordinates to the "100%" button
            pyautogui.click()
            time.sleep(1)

        # Step 6b: Click "Close" button again
        hotkey_logger.info("Clicking 'Close' button again...")
        pyautogui.moveTo(1615, 744)  # Adjust the coordinates to the "Close" button
        pyautogui.click()
        time.sleep(1)

        # Step 7: Click "Confirm" button
        hotkey_logger.info("Clicking 'Confirm' button...")
        # Uncomment and set accurate coordinates for the "Confirm" button
        pyautogui.moveTo(1046, 797)
        pyautogui.click()
        time.sleep(1)

        hotkey_logger.info("Close limit sell executed.")

    except Exception as e:
        hotkey_logger.info(f"An error occurred during close limit sell: {e}")


hotkey_logger.info("Active. Please make sure the trading application window is focused.")



