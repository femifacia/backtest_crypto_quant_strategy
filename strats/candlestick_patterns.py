import pandas as pd
import matplotlib.pyplot as plt
#import mplfinance as mpf
import numpy as np
from sklearn.linear_model import LinearRegression as lineregres
import random
from scipy.signal import argrelextrema
from strategy import strategy

class candlestick_patterns(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'candlestick patterns'

    def load_data(self):
        return super().load_data()

    def describe(self):
        super().describe()
        text = """ """
        text += '\n'

        print(text)
    
    #strategie qui envoi un ordre de Buy ou de Sell si il identifie un candlestick patterns
    def detect_candlestick_patterns(self, df, tail=5):
        df = df.copy()
        df = df[-(tail + 1):]  # On regarde les dernières bougies + celle d’avant pour les engulfings

        pattern = None
        signal = None
        index = None

        for i in range(1, len(df)):
            prev = df.iloc[i - 1]
            curr = df.iloc[i]

            # Engulfing Bullish
            if prev['close'] < prev['open'] and curr['close'] > curr['open']:
                if curr['open'] < prev['close'] and curr['close'] > prev['open']:
                    pattern = "Bullish Engulfing"
                    signal = "BUY"
                    index = df.index[i]

            # Engulfing Bearish
            elif prev['close'] > prev['open'] and curr['close'] < curr['open']:
                if curr['open'] > prev['close'] and curr['close'] < prev['open']:
                    pattern = "Bearish Engulfing"
                    signal = "SELL"
                    index = df.index[i]

            # Hammer (ombre basse longue, petit corps en haut)
            elif curr['close'] > curr['open']:
                body = curr['close'] - curr['open']
                lower_shadow = curr['open'] - curr['low']
                upper_shadow = curr['high'] - curr['close']
                if lower_shadow > 2 * body and upper_shadow < body:
                    pattern = "Hammer"
                    signal = "BUY"
                    index = df.index[i]

            # Shooting Star (ombre haute longue, petit corps en bas)
            elif curr['close'] < curr['open']:
                body = curr['open'] - curr['close']
                upper_shadow = curr['high'] - curr['open']
                lower_shadow = curr['close'] - curr['low']
                if upper_shadow > 2 * body and lower_shadow < body:
                    pattern = "Shooting Star"
                    signal = "SELL"
                    index = df.index[i]

            if pattern:
                break

        return signal



    def compute_signal(self, src_data : pd.DataFrame , start=None, end=None, limit=None):
        LongStopGain = 1.076
        LongStopLoss = 0.983
        LongStop = 43
        ShortStopGain = 0.965
        ShortStopLoss = 1.02
        ShortStop = 45
        if start and end:
            src_data = src_data[start:end]
        elif start:
            src_data = src_data[start:]
        elif end:
            src_data = src_data[:end]
        df = src_data.copy()
        df['signal'] = 0
        result = None
        for i, idx in enumerate(df.index):
            if i < 10:
                continue
            data_up_to_idx = df.loc[:idx]
            if result == None :
                result = self.detect_candlestick_patterns(data_up_to_idx) 
                if result == "BUY":
                    df.at[idx, 'signal'] = 1
                    d = LongStop
                    price = df.at[idx, 'close']
                    
                elif result == "SELL":
                    df.at[idx, 'signal'] = -1
                    d = ShortStop
                    price = df.at[idx, 'close']
            elif result == "BUY":
                d = d-1
                level = df.at[idx, 'close']
                if  d == 0 or level > price*LongStopGain or level < price*LongStopLoss :
                    result = None
                else :
                    df.at[idx, 'signal'] = 1
            elif result == "SELL":
                d = d-1
                level = df.at[idx, 'close']
                if  d == 0 or level > price*ShortStopLoss or level < price*ShortStopGain :
                    result = None
                else :
                    df.at[idx, 'signal'] = -1
        return  df['signal'].shift(1)
