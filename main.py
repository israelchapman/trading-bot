from bot import get_price_data, calculate_moving_averages

data = calculate_moving_averages("BTCUSDT", "1d")
print(data)
