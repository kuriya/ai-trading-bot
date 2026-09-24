from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sklearn.model_selection import train_test_split
from binance_api import get_binance_data
from indicators import add_indicators_and_labels
from candlestick import add_candlestick_patterns
from models import train_and_evaluate_xgboost, make_live_prediction

app = FastAPI()

# Allow React to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to cache the model so we don't retrain it on every API request
global_model = None
global_features = None

def initialize_ai(target_coin="BTCUSDT"):
    global global_model
    global global_features
    print(f"\n[DASHBOARD STARTUP] Initializing AI for {target_coin}...")
    print("This will take a few seconds to fetch 5 years of historical data to train the model...")
    
    # 1. Train the model ONCE on startup using 5 years of data
    data = get_binance_data(symbol=target_coin)
    data, indicator_features = add_indicators_and_labels(data)
    data, pattern_features = add_candlestick_patterns(data)
    
    features = indicator_features + pattern_features
    global_features = features
    
    data = data.dropna()
    X = data[features]
    y = data['Label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model, _ = train_and_evaluate_xgboost(X_train, X_test, y_train, y_test)
    global_model = model
    
    print(f"\n[DASHBOARD STARTUP] AI Initialized and Ready for Web API requests!\n")

@app.on_event("startup")
def startup_event():
    # Automatically train the AI on BTC when the server boots up
    initialize_ai("BTCUSDT")

@app.get("/api/predict/{coin}")
def get_prediction(coin: str):
    print(f"\n[API REQUEST] Web dashboard requested live prediction for {coin}...")
    
    # Fetch just the very latest data (last ~400 hours) for a live prediction using the pre-trained model!
    # By using years=0.05, it downloads enough data to calculate 100-hour rolling indicators instantly
    data = get_binance_data(symbol=coin, years=0.05) 
    
    data, _ = add_indicators_and_labels(data)
    data, _ = add_candlestick_patterns(data)
    
    # Extract the very last hour's features for the prediction
    latest_features = data.iloc[-1:][global_features]
    current_price = data.iloc[-1]['Close']
    
    # Make the live prediction using the pre-trained model
    result = make_live_prediction(global_model, latest_features, current_price, coin)
    
    return result

if __name__ == "__main__":
    import uvicorn
    # Starts the web server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
