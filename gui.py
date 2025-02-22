import queue
import logging
import tkinter as tk
from threading import Thread, Event
from tkinter import ttk
from common import load_settings, save_settings
from monitoring import monitor_crypto
import time
from bot import determine_market_condition
from bridge import Bridge


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logging.getLogger("urllib3").setLevel(logging.WARNING)

gui_logger = logging.getLogger("gui")
monitoring_active = False
stop_event = Event()
stop_signal = queue.Queue()
monitoring_thread = None
bridge = Bridge()

# Initialize a queue for communication
signal_queue = queue.Queue()
active_open_queue = queue.Queue()
active_sell_queue = queue.Queue()

# active open trade control flag
active_open_trade = False
# active close trade control flag
active_sell_trade = False
# Monitoring control flag
monitoring_paused = False


def monitor_thread(symbol, interval, market_type):
    global stop_signal, bridge, monitoring_active, monitoring_paused, active_open_trade, active_sell_trade
    gui_logger.debug("Monitoring thread started.")

    monitor_crypto(symbol, signal_queue, active_open_queue, active_sell_queue, interval, market_type, stop_event)
    previous_market_condition = None

    while not stop_event.is_set():
        if not stop_signal.empty():
            stop_signal.get()
            break
        if monitoring_paused:
            gui_logger.info("Monitoring is paused. Waiting...")
            time.sleep(2)
            continue  # Skip this loop iteration

        market_conditions = determine_market_condition(symbol, market_type)
        bridge.set_market_condition(market_conditions)
        gui_logger.debug(f"Previous market condition: {previous_market_condition}, Current market condition: {market_conditions}")

        if market_conditions == previous_market_condition:
            gui_logger.info(f"Queuing trade for market condition: {market_conditions}")

    monitoring_active = False
    gui_logger.info("Monitoring thread stopped.")


def listen_for_signals():
    """Listens for pause/resume signals from executor.py and adjusts monitoring."""
    global monitoring_paused
    while True:
        signal = signal_queue.get()
        if signal == "PAUSE":
            monitoring_paused = True
            gui_logger.info("lfs Monitoring paused due to trade execution.")
        elif signal == "RESUME":
            monitoring_paused = False
            gui_logger.info("Monitoring resumed after trade execution.")


def listen_for_active_open():
    """Listens for active trade signals from executor.py and adjusts can execute."""
    global active_open_trade
    while True:
        open_activity = active_open_queue.get()
        gui_logger.debug(f"Received active open trade signal: {open_activity}")
        if open_activity == "1":
            active_open_trade = True
            gui_logger.info("Active open trade detected.")


def listen_for_active_sell():
    """Listens for active trade signals from executor.py and adjusts can execute."""
    global active_sell_trade
    while True:
        sell_activity = active_sell_queue.get()  # Fix: Use the correct queue
        if sell_activity == "1":
            active_sell_trade = True
            gui_logger.info("Active sell trade detected.")


def start_monitoring(symbol, interval, market_type):
    global monitoring_active, monitoring_thread, bridge

    if monitoring_active:
        gui_logger.info("Monitoring is already active.")
        return
    stop_event.clear()
    monitoring_active = True
    monitoring_thread = Thread(target=monitor_thread, args=(symbol, interval, market_type))
    monitoring_thread.start()
    gui_logger.info(f"Started monitoring for {symbol} with {interval} interval on {market_type} market.")
    bridge = Bridge()

    # Start listening for pause/resume signals
    signal_listener_thread = Thread(target=listen_for_signals)
    signal_listener_thread.daemon = True
    signal_listener_thread.start()


def stop_monitoring():
    global monitoring_active, monitoring_thread
    if not monitoring_active:
        gui_logger.info("Monitoring is not active.")
        return
    stop_signal.put("STOP")
    gui_logger.info("stop mon stop signal.")
    stop_event.set()
    if monitoring_thread and monitoring_thread.is_alive():
        monitoring_thread.join()
    monitoring_active = False
    gui_logger.info("Monitoring stopped successfully.")


def create_gui():
    root = tk.Tk()
    root.title("Crypto Monitoring Tool")
    settings = load_settings()  # Load existing settings

    def create_dropdown(label_text, values, default):
        tk.Label(root, text=label_text).pack()
        var = tk.StringVar(value=default)
        dropdown = ttk.Combobox(root, textvariable=var, values=values)
        dropdown.pack()
        return var

    def create_input_field(label_text, default_value):
        tk.Label(root, text=label_text).pack()
        entry = tk.Entry(root)
        entry.insert(0, default_value)
        entry.pack()
        return entry

    symbol_entry = tk.Entry(root)
    symbol_entry.insert(0, settings.get('symbol', 'BTCUSDT'))
    symbol_entry.pack()

    interval_var = create_dropdown("Interval", ['1m', '5m', '15m', '30m', '1h', '4h', '1d'], settings.get('interval', '1m'))
    market_type_var = create_dropdown("Market Type", ['spot', 'futures'], settings.get('market_type', 'spot'))
    trade_type_var = create_dropdown("Trade Type", ['market', 'limit'], settings.get('trade_type', 'market'))

    amount_entry = create_input_field("Trade Amount", settings.get('amount', '1'))
    return_percentage_entry = create_input_field("Return Percentage (%)", settings.get('return_percentage', '5'))
    loss_risk_entry = create_input_field("Loss Risk Percentage (%)", settings.get('loss_risk_percentage', '2'))
    fee_margin = create_input_field("fee margin (%)", settings.get('fee_margin', ''))

    def save_settings_gui():
        """Save updated settings using common.py's save_settings function"""
        settings['symbol'] = symbol_entry.get()
        settings['interval'] = interval_var.get()
        settings['market_type'] = market_type_var.get()
        settings['trade_type'] = trade_type_var.get()
        settings['amount'] = amount_entry.get()
        settings['return_percentage'] = return_percentage_entry.get()
        settings['loss_risk_percentage'] = loss_risk_entry.get()
        settings['fee_margin'] = fee_margin.get()
        save_settings(settings)  # Call save_settings from common.py

    tk.Button(root, text="Start Monitoring",
              command=lambda: start_monitoring(symbol_entry.get(), interval_var.get(), market_type_var.get())).pack()
    tk.Button(root, text="Stop Monitoring", command=stop_monitoring).pack()
    tk.Button(root, text="Save Settings", command=save_settings_gui).pack()  # Save settings button

    gui_logger.debug("GUI created and ready.")
    root.mainloop()


if __name__ == "__main__":
    create_gui()
