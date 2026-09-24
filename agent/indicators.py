import ta
import numpy as np

def add_indicators_and_labels(data):
    # Base Indicators (1H Timeframe)
    data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
    data['MACD'] = ta.trend.MACD(data['Close']).macd()
    data['EMA20'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
    data['EMA50'] = ta.trend.EMAIndicator(data['Close'], window=50).ema_indicator()

    # Volatility & Volume
    data['Bollinger_High'] = ta.volatility.BollingerBands(data['Close']).bollinger_hband()
    data['ATR'] = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close']).average_true_range()
    data['VWAP'] = ta.volume.VolumeWeightedAveragePrice(data['High'], data['Low'], data['Close'], data['Volume']).volume_weighted_average_price()
    data['Stoch'] = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close']).stoch()
    data['OBV'] = ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()

    # Advanced Trend Indicators
    data['ADX'] = ta.trend.ADXIndicator(data['High'], data['Low'], data['Close']).adx()
    data['MFI'] = ta.volume.MFIIndicator(data['High'], data['Low'], data['Close'], data['Volume']).money_flow_index()
    data['CCI'] = ta.trend.cci(data['High'], data['Low'], data['Close'])

    # THE NEW MEGA-INDICATORS
    data['Ichimoku_A'] = ta.trend.IchimokuIndicator(data['High'], data['Low']).ichimoku_a()
    data['Ichimoku_B'] = ta.trend.IchimokuIndicator(data['High'], data['Low']).ichimoku_b()
    data['Keltner_High'] = ta.volatility.KeltnerChannel(data['High'], data['Low'], data['Close']).keltner_channel_hband()
    data['Aroon_Up'] = ta.trend.AroonIndicator(data['High'], data['Low']).aroon_up()
    data['Aroon_Down'] = ta.trend.AroonIndicator(data['High'], data['Low']).aroon_down()

    # CUSTOM FIBONACCI RETRACEMENT MATH
    rolling_high = data['High'].rolling(window=100).max()
    rolling_low = data['Low'].rolling(window=100).min()
    fib_diff = rolling_high - rolling_low
    
    data['Fib_0.382'] = rolling_high - (fib_diff * 0.382)
    data['Fib_0.500'] = rolling_high - (fib_diff * 0.500)
    data['Fib_0.618'] = rolling_high - (fib_diff * 0.618)

    features = [
        'RSI', 'MACD', 'EMA20', 'EMA50',
        'Bollinger_High', 'ATR', 'VWAP', 'Stoch', 'OBV',
        'ADX', 'MFI', 'CCI',
        'Ichimoku_A', 'Ichimoku_B', 'Keltner_High', 'Aroon_Up', 'Aroon_Down',
        'Fib_0.382', 'Fib_0.500', 'Fib_0.618'
    ]
    
    # ==========================================
    # 🌍 MULTI-TIMEFRAME ANALYSIS (MTFA)
    # ==========================================
    # Now that we have 5 years of data, we can include the 1W chart!
    timeframes = {'4H': '4h', '1D': '1d', '1W': '1W'}
    
    for label, rule in timeframes.items():
        resampled = data.resample(rule).agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()
        
        # Calculate MACD and RSI on the MACRO timeframes
        resampled[f'RSI_{label}'] = ta.momentum.RSIIndicator(resampled['Close']).rsi()
        resampled[f'MACD_{label}'] = ta.trend.MACD(resampled['Close']).macd()
        
        # Merge it back into the 1H dataframe
        data = data.join(resampled[[f'RSI_{label}', f'MACD_{label}']], how='left')
        
        # Forward Fill so the 1H candles inside the same day get the same Daily RSI
        data[f'RSI_{label}'] = data[f'RSI_{label}'].ffill()
        data[f'MACD_{label}'] = data[f'MACD_{label}'].ffill()
        
        features.extend([f'RSI_{label}', f'MACD_{label}'])

    # ==========================================
    # 🎯 CUSTOM TRADING STRATEGY LABELING
    # ==========================================
    labels = []
    close_prices = data['Close'].values
    high_prices = data['High'].values
    low_prices = data['Low'].values
    n = len(data)
    
    for i in range(n):
        entry_price = close_prices[i]
        take_profit = entry_price * 1.05  # +5%
        stop_loss = entry_price * 0.97    # -3%
        
        is_profitable = 0
        
        max_lookahead = min(i + 49, n)
        
        for j in range(i + 1, max_lookahead):
            if low_prices[j] <= stop_loss:
                break 
            if high_prices[j] >= take_profit:
                is_profitable = 1
                break
                
        labels.append(is_profitable)

    data['Label'] = labels
    data.loc[data.index[-48:], 'Label'] = np.nan
    
    return data, features
