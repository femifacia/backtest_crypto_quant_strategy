import pandas as pd
import matplotlib.pyplot as plt
#import mplfinance as mpf
import numpy as np
from scipy.stats import linregress
import random
from scipy.signal import argrelextrema
from strategy import strategy

class breakout_patterns(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'breakout patterns'

    def load_data(self):
        return super().load_data()

    def describe(self):
        super().describe()
        text = """ Detects a breakout pattern of type Triangle, Flag, Wedge or Rectangle that has just ended."""
        text += '\n'

        print(text)
    
    #strategie qui envoi un ordre de Buy ou de Sell si il identifie un breakout patterns
    def detect_breakout_patterns(self, df, window=30, tail=5):
        df = df.copy()
        pattern = None
        signal = None

        # On se concentre sur la fin du graphique
        recent = df[-window:]
        highs = recent['high'].values
        lows = recent['low'].values
        closes = recent['close'].values

        x = np.arange(len(recent))

        # Droite de résistance
        high_slope, high_intercept, _, _, _ = linregress(x, highs)
        resistance = high_slope * x + high_intercept

        # Droite de support
        low_slope, low_intercept, _, _, _ = linregress(x, lows)
        support = low_slope * x + low_intercept

        # Écarts moyens
        upper_error = np.mean(np.abs(highs - resistance))
        lower_error = np.mean(np.abs(lows - support))

        last_close = closes[-1]

        def breakout_detected():
            return last_close > resistance[-1] + upper_error or last_close < support[-1] - lower_error

        def in_last_n_bars():
            return np.argmax((df.index == recent.index[-1])) >= len(df) - tail

        # Triangle : support et résistance convergent
        if high_slope < 0 and low_slope > 0 and abs(high_slope - low_slope) > 0.01:
            if breakout_detected() and in_last_n_bars():
                pattern = "Triangle"
                signal = "BUY" if last_close > resistance[-1] else "SELL"

        # Rectangle : support et résistance presque plats
        elif abs(high_slope) < 0.01 and abs(low_slope) < 0.01:
            if breakout_detected() and in_last_n_bars():
                pattern = "Rectangle"
                signal = "BUY" if last_close > resistance[-1] else "SELL"

        # Wedge : biseau montant ou descendant
        elif high_slope > 0 and low_slope > 0:
            if breakout_detected() and in_last_n_bars():
                pattern = "Rising Wedge"
                signal = "SELL"
        elif high_slope < 0 and low_slope < 0:
            if breakout_detected() and in_last_n_bars():
                pattern = "Falling Wedge"
                signal = "BUY"

        # Flag : petite consolidation après mouvement directionnel fort
        elif abs(high_slope) < 0.2 and abs(low_slope) < 0.2:
            previous = df[-(window + 20):-window]
            if len(previous) > 0:
                direction = previous['close'].iloc[-1] - previous['close'].iloc[0]
                if abs(direction) > 2 * (highs.max() - lows.min()):  # fort mouvement
                    if breakout_detected() and in_last_n_bars():
                        pattern = "Flag"
                        signal = "BUY" if direction > 0 else "SELL"

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
                result = self.detect_breakout_patterns(data_up_to_idx) 
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