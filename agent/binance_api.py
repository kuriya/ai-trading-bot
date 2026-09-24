import pandas as pd
import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_binance_data(symbol="BTCUSDT", interval="1h", years=5):
    """Fetches up to 5 years of hourly data for DAY TRADING by paginating backwards"""
    target_candles = int(years * 365 * 24)
    
    all_data = []
    end_time = None
    
    print(f"Downloading 5 years of data (approx {target_candles} candles)... Please wait 10-15 seconds...")
    
    while len(all_data) < target_candles:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=1000"
        if end_time:
            url += f"&endTime={end_time}"
            
        try:
            response = requests.get(url, verify=False).json()
            if not isinstance(response, list) or len(response) == 0:
                print("\nReached the earliest available data for this coin!")
                break
                
            all_data = response + all_data 
            end_time = response[0][0] - 1  
            
            # Print a little progress tracker so it doesn't look frozen
            print(f"\rDownloaded {len(all_data)} / {target_candles} rows...", end="", flush=True)
            
            time.sleep(0.1) # Be nice to Binance rate limits
        except Exception as e:
            print(f"\nError fetching data: {e}")
            break
            
    print("\n")
            
    if len(all_data) > target_candles:
        all_data = all_data[-target_candles:]
        
    df = pd.DataFrame(all_data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote volume', 'Trades', 'Taker base', 'Taker quote', 'Ignore'])
    df['Datetime'] = pd.to_datetime(df['Open time'], unit='ms')
    df.set_index('Datetime', inplace=True)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
    
    return df
