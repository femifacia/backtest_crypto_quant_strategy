import pandas as pd
import matplotlib.pyplot as plt
#import mplfinance as mpf
import numpy as np
from sklearn.linear_model import LinearRegression as linregress
import random
from scipy.signal import argrelextrema
from strategy import strategy

class harmonic_pattern(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'harmonic pattern'

    def load_data(self):
        return super().load_data()
    

    #strategie qui envoi un ordre de Buy ou de Sell si il identifie un harmonic patterns
    def find_harmonic_pattern(self, df, lookback=100, tail=5):
        df = df.copy()
        closes = df['close'].values

        maxima = argrelextrema(closes, np.greater, order=5)[0]
        minima = argrelextrema(closes, np.less, order=5)[0]
        pivots = np.sort(np.concatenate([maxima, minima]))

        pattern = None
        signal = None
        pattern_points = []

        def approx(value, target, tolerance=0.05):
            return abs(value - target) <= tolerance * target

        for i in range(len(pivots) - 4):
            indices = pivots[i:i+5]
            if indices[-1] < len(df) - tail:
                continue  # On veut que le point D soit à la fin

            X, A, B, C, D = closes[indices]

            XA = A - X
            AB = B - A
            BC = C - B
            CD = D - C

            # Normalisation des longueurs
            xa = abs(XA)
            ab = abs(AB)
            bc = abs(BC)
            cd = abs(CD)

            # Détection du pattern
            if approx(ab/xa, 0.618) and approx(bc/ab, 0.618) and approx(cd/xa, 0.786):
                pattern = "Gartley"
            elif approx(ab/xa, 0.5) and approx(cd/xa, 0.886):
                pattern = "Bat"
            elif approx(ab/xa, 0.786) and approx(cd/xa, 1.27):
                pattern = "Butterfly"
            elif approx(ab/xa, 0.618) and approx(cd/xa, 1.618):
                pattern = "Crab"

            if pattern:
                pattern_points = indices
                signal = "BUY" if CD < 0 else "SELL"
                break

        if pattern:
            return signal,
        
        else:
            return None
    
    

    def compute_signal(self, src_data : pd.DataFrame , start=None, end=None, limit=None):
        LongStopGain = 1.076 
        LongStopLoss = 0.983
        LongStop = 43 #duree max d'une pose longue
        ShortStopGain = 0.965
        ShortStopLoss = 1.02
        ShortStop = 45 #duree max d'une pose courte
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
                result = self.find_harmonic_pattern(data_up_to_idx) 
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

