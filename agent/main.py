import pandas as pd
from sklearn.model_selection import train_test_split
from binance_api import get_binance_data
from indicators import add_indicators_and_labels
from candlestick import add_candlestick_patterns
from models import train_and_evaluate_xgboost, make_live_prediction

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
TARGET_COIN = "BTCUSDT" 
# ==========================================

# 1. Fetch Data
print(f"Fetching hourly data for {TARGET_COIN} from Binance API...")
data = get_binance_data(symbol=TARGET_COIN)
print(f"Successfully downloaded {len(data)} rows of data!\n")

# 2. Add Indicators
data, indicator_features = add_indicators_and_labels(data)

# 3. Add Candlestick Patterns
data, pattern_features = add_candlestick_patterns(data)

# Combine all features for the AI
features = indicator_features + pattern_features

# 4. Extract Today's Data for Live Prediction!
latest_features = data.iloc[-1:][features]
current_price = data.iloc[-1]['Close']

# 5. Clean and Split Data for Training
data = data.dropna()
X = data[features]
y = data['Label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. Train AI Model
model, accuracy = train_and_evaluate_xgboost(X_train, X_test, y_train, y_test)

# 7. Make Live Prediction!
make_live_prediction(model, latest_features, current_price, TARGET_COIN)
