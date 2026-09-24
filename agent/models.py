import xgboost as xgb
from sklearn.metrics import accuracy_score

def train_and_evaluate_xgboost(X_train, X_test, y_train, y_test):
    model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    model.fit(X_train, y_train)
    
    # Overall baseline accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print("\n[XGBoost Model Result]")
    print(f"Overall Accuracy (Default 50% Rule): {accuracy * 100:.2f}%")
    
    # CUSTOM 80% THRESHOLD FOR HISTORICAL TESTING
    y_prob = model.predict_proba(X_test)
    
    # Find all test cases where AI was >= 80% confident
    good_trade_mask = y_prob[:, 1] >= 0.80
    bad_trade_mask = y_prob[:, 0] >= 0.80
    
    ai_said_good_total = sum(good_trade_mask)
    ai_said_bad_total = sum(bad_trade_mask)
    
    # How many times was it actually right when it was 80% confident?
    actual_good_when_predicted_good = sum(y_test.values[good_trade_mask] == 1)
    actual_bad_when_predicted_bad = sum(y_test.values[bad_trade_mask] == 0)
    
    good_trade_win_rate = (actual_good_when_predicted_good / ai_said_good_total * 100) if ai_said_good_total > 0 else 0
    bad_trade_correct_rate = (actual_bad_when_predicted_bad / ai_said_bad_total * 100) if ai_said_bad_total > 0 else 0
    neutral_count = len(y_test) - (ai_said_good_total + ai_said_bad_total)
    
    print("\n[Historical Confidence Breakdown (STRICT 80% RULE)]")
    print(f"When AI was 80%+ sure it was a 'GOOD TRADE', it was right: {good_trade_win_rate:.2f}% of the time!")
    print(f"When AI was 80%+ sure it was a 'BAD TRADE', it was right:  {bad_trade_correct_rate:.2f}% of the time.")
    print(f"(Out of {len(y_test)} historical tests, it took {ai_said_good_total} Good Trades, avoided {ai_said_bad_total} Bad Trades, and stayed NEUTRAL {neutral_count} times)")
    
    return model, accuracy

def make_live_prediction(model, latest_features, current_price, coin_symbol):
    prediction = model.predict(latest_features)[0]
    probabilities = model.predict_proba(latest_features)[0]
    
    prob_down = probabilities[0] * 100
    prob_up = probabilities[1] * 100
    
    target_price = current_price * 1.05
    stop_loss = current_price * 0.97
    
    print("\n==========================================")
    print(f"LIVE PREDICTION ({coin_symbol}) for next 48 hours")
    print(f"Current Price:      ${current_price:,.2f}")
    print(f"Take Profit (+5%):  ${target_price:,.2f}")
    print(f"Stop Loss (-3%):    ${stop_loss:,.2f}")
    print("==========================================")
    
    if prob_up >= 80.0:
        forecast = "GOOD TRADE"
        confidence = prob_up
        print(f"Forecast: GOOD TRADE")
        print(f"AI Confidence: {prob_up:.2f}% (Price will hit ${target_price:,.2f} within the next 48 hours)")
    elif prob_down >= 80.0:
        forecast = "BAD TRADE"
        confidence = prob_down
        print(f"Forecast: BAD TRADE")
        print(f"AI Confidence: {prob_down:.2f}% (Price will drop to ${stop_loss:,.2f} or stagnate within the next 48 hours)")
    else:
        forecast = "NEUTRAL"
        confidence = max(prob_up, prob_down)
        print(f"Forecast: NEUTRAL (NO ENTRY)")
        print(f"AI Confidence: {confidence:.2f}% (Too low to risk your money. Waiting for >80%)")
    print("==========================================\n")
    
    return {
        "coin": coin_symbol,
        "current_price": float(current_price),
        "target_price": float(target_price),
        "stop_loss": float(stop_loss),
        "forecast": forecast,
        "confidence": float(confidence)
    }
