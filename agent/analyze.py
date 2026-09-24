from binance_api import get_binance_data
from indicators import add_indicators_and_labels

print("Analyzing the last ~3 months of Bitcoin data...")
data = get_binance_data(symbol="BTCUSDT")
data, features = add_indicators_and_labels(data)

# Count the occurrences of 1s (Good Trades) and 0s (Bad Trades)
total_successful_trades = (data['Label'] == 1).sum()
total_failed_trades = (data['Label'] == 0).sum()

print(f"\n==========================================")
print(f"MARKET ANALYSIS (Last {len(data)} Hours / ~83 Days)")
print(f"==========================================")
print(f"Total Successful Opportunities (+5% Hit): {total_successful_trades}")
print(f"Total Failed Opportunities (Stop Loss Hit): {total_failed_trades}")
print(f"==========================================")
