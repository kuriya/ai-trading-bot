import numpy as np

def add_candlestick_patterns(data):
    """
    Analyzes Open, High, Low, Close prices to detect psychological trading patterns.
    Returns the updated dataframe and the new feature names.
    """
    O = data['Open']
    H = data['High']
    L = data['Low']
    C = data['Close']
    
    # Pre-compute some basic candle anatomy for the math formulas
    body = abs(C - O)
    total_range = H - L
    upper_wick = H - np.maximum(O, C)
    lower_wick = np.minimum(O, C) - L
    
    # 1. Doji (Body is practically non-existent, less than 10% of the total range)
    data['Doji'] = (body < (total_range * 0.1)).astype(int)
    
    # 2. Hammer (Small body at the top, long lower wick at least 2x the body, tiny upper wick)
    data['Hammer'] = ((lower_wick > (2 * body)) & (upper_wick < (0.1 * total_range)) & (body > 0)).astype(int)
    
    # 3. Shooting Star (Small body at the bottom, long upper wick at least 2x the body, tiny lower wick)
    data['Shooting_Star'] = ((upper_wick > (2 * body)) & (lower_wick < (0.1 * total_range)) & (body > 0)).astype(int)
    
    # 4. Bullish Engulfing
    # Previous candle was Red. Current is Green. Current Green body completely covers previous Red body.
    prev_O = O.shift(1)
    prev_C = C.shift(1)
    data['Bullish_Engulfing'] = ((prev_O > prev_C) & (C > O) & (C >= prev_O) & (O <= prev_C)).astype(int)
    
    # 5. Bearish Engulfing
    # Previous candle was Green. Current is Red. Current Red body completely covers previous Green body.
    data['Bearish_Engulfing'] = ((prev_C > prev_O) & (O > C) & (O >= prev_C) & (C <= prev_O)).astype(int)

    pattern_features = ['Doji', 'Hammer', 'Shooting_Star', 'Bullish_Engulfing', 'Bearish_Engulfing']
    
    return data, pattern_features
