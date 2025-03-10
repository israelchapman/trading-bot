import logging
import tkinter as tk
from tkinter import ttk
from common import load_settings, save_settings
from monitor_thread import start_monitoring, stop_monitoring

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

gui_logger = logging.getLogger("gui")

logging.getLogger("urllib3").setLevel(logging.WARNING)


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