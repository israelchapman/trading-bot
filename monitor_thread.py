import time
from threading import Thread, Event
import queue
from bridge import Bridge
from bot import determine_market_condition
from monitoring import monitor_crypto
import logging

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

# Configure logging to display logs in the terminal
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get the logger for monitor
thread_logger = logging.getLogger("thread")


def listen_for_signals():
    """Listens for pause/resume signals from executor.py and adjusts monitoring."""
    global monitoring_paused
    while True:
        signal = signal_queue.get()
        if signal == "PAUSE":
            monitoring_paused = True
            thread_logger.info("lfs Monitoring paused due to trade execution.")
        elif signal == "RESUME":
            monitoring_paused = False
            thread_logger.info("Monitoring resumed after trade execution.")


def listen_for_active_open():
    """Listens for active trade signals from executor.py and adjusts can execute."""
    global active_open_trade
    while True:
        open_activity = active_open_queue.get()
        thread_logger.debug(f"Received active open trade signal: {open_activity}")
        if open_activity == "1":
            active_open_trade = True
            thread_logger.info("Active open trade detected.")


def listen_for_active_sell():
    """Listens for active trade signals from executor.py and adjusts can execute."""
    global active_sell_trade
    while True:
        sell_activity = active_sell_queue.get()  # Fix: Use the correct queue
        if sell_activity == "1":
            active_sell_trade = True
            thread_logger.info("Active sell trade detected.")


def start_monitoring(symbol, interval, market_type):
    global monitoring_active, monitoring_thread, bridge

    if monitoring_active:
        thread_logger.info("Monitoring is already active.")
        return
    stop_event.clear()
    monitoring_active = True

    monitoring_thread = Thread(target=monitor_thread, args=(symbol, interval, market_type))
    monitoring_thread.start()

    thread_logger.info(f"Started monitoring for {symbol} with {interval} interval on {market_type} market.")

    # Start listening for pause/resume signals
    signal_listener_thread = Thread(target=listen_for_signals)
    signal_listener_thread.daemon = True
    signal_listener_thread.start()


def stop_monitoring():
    global monitoring_active, monitoring_thread
    if not monitoring_active:
        thread_logger.info("Monitoring is not active.")
        return
    stop_signal.put("STOP")
    thread_logger.info("stop mon stop signal.")
    stop_event.set()
    if monitoring_thread and monitoring_thread.is_alive():
        monitoring_thread.join()
    monitoring_active = False
    thread_logger.info("Monitoring stopped successfully.")


def monitor_thread(symbol, interval, market_type):
    global stop_signal, bridge, monitoring_active, monitoring_paused, active_open_trade, active_sell_trade
    thread_logger.debug("Monitoring thread started.")

    monitor_crypto(symbol, signal_queue, active_open_queue, active_sell_queue, interval, market_type, stop_event)
    previous_market_condition = None

    while not stop_event.is_set():
        if not stop_signal.empty():
            stop_signal.get()
            break
        if monitoring_paused:
            thread_logger.info("Monitoring is paused. Waiting...")
            time.sleep(2)
            continue  # Skip this loop iteration

        market_conditions = determine_market_condition(symbol, market_type)
        bridge.set_market_condition(market_conditions)
        thread_logger.debug(f"Previous market condition: {previous_market_condition}, Current market condition: {market_conditions}")

        if market_conditions == previous_market_condition:
            thread_logger.info(f"Queuing trade for market condition: {market_conditions}")

    monitoring_active = False
    thread_logger.info("Monitoring thread stopped.")

