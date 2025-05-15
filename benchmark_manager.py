import os
import sys

from binance.client import Client
import pandas as pd
from datetime import datetime

# Si tu n'utilises pas d'API key privée, tu peux laisser vide :
client = Client(api_key='', api_secret='')

def get_binance_ticker_sdk(symbol="BTCUSDT", interval="1h", start_str="2024-03-01"):
    # Récupère toutes les k-lines depuis la date spécifiée
    klines = client.get_historical_klines(
        symbol=symbol,
        interval=interval,
        start_str=start_str
    )

    # Colonnes de retour
    columns = [
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"
    ]

    # Mise en DataFrame
    df = pd.DataFrame(klines, columns=columns)

    # Conversions utiles
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms")
    num_cols = ["open", "high", "low", "close", "volume"]
    df[num_cols] = df[num_cols].astype(float)
    df.index = df['timestamp']
    df = df.drop(columns='timestamp')

    return df




def update_tickers_from_file(src_dir='./data/', ticker="BTCUSDT"):
    if not os.path.isdir(src_dir):
        raise Exception('src path does not exist')
    path = os.path.join(src_dir, ticker + '.csv')
    print(path)
    start = "2017-01-01"
    previous_data = None
    if  os.path.exists(path) and os.path.isfile(path):
        previous_data = pd.read_csv(path,index_col=0)
        start = previous_data.index[-1]
        previous_data = previous_data.iloc[:-1]
    print(start)
    print(previous_data)
    new_df = get_binance_ticker_sdk(symbol=ticker, start_str=start)
    result_df = pd.concat([previous_data,new_df],axis=0,verify_integrity=True).drop(columns='ignore')
    result_df.to_csv(path)
    return result_df

def get_benchmark(src_dir='./data/', start=None, end=None, ticker="BTCUSDT"):
    if not os.path.isdir(src_dir):
        raise Exception('src path does not exist')
    df = None
    try:
        df = pd.read_csv(f'{src_dir+ticker}.csv',index_col=0)
        if start and df.index[0] > start:
            raise Exception('Start not in bench')
        if end and df.index[-1] < end:
            raise Exception('Start not in bench')
    except:
        df = update_tickers_from_file(src_dir=src_dir, ticker=ticker)
    if start:
        df = df.loc[start:]
    if end:
        df = df.loc[:end]
    return df