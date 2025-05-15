import pandas as pd
import matplotlib.pyplot as plt
#import mplfinance as mpf
import numpy as np
from sklearn.linear_model import LinearRegression as linregress
import random
from scipy.signal import argrelextrema
from strategy import strategy

class reversal_pattern(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'reversal pattern'

    def load_data(self):
        return super().load_data()
    
    def describe(self):
        super().describe()
        text = """Detects recently completed reversal patterns such as Head & Shoulders, Triple Top, Triple Bottom, Double Top, Double Bottom, Cups & handles"""

        print(text)
    
    #strategie qui envoi un ordre de Buy ou de Sell si il identifie un reversal patterns
    def detect_final_reversal_pattern(self, df, order=5, tolerance=0.03, tail=5):
        df = df.copy()
        closes = df['close'].values
        dates = df.index

        max_idx = argrelextrema(closes, np.greater_equal, order=order)[0]
        min_idx = argrelextrema(closes, np.less_equal, order=order)[0]
        all_idx = sorted(np.concatenate([max_idx, min_idx]))

        def is_approx(a, b):
            return abs(a - b) <= tolerance * max(a, b)

        for i in range(len(all_idx) - 6):
            idx_segment = all_idx[i:i+7]
            if idx_segment[-1] < len(df) - tail:
                continue  # on veut uniquement les patterns récents (dans les `tail` dernières bougies)

            prices = closes[idx_segment]
            segment_dates = dates[idx_segment]

            ### 1. Head & Shoulders
            if len(prices) >= 5:
                l_shoulder = prices[0]
                head = prices[2]
                r_shoulder = prices[4]
                neckline1 = prices[1]
                neckline2 = prices[3]

                if (
                    head > l_shoulder and head > r_shoulder
                    and is_approx(l_shoulder, r_shoulder)
                    and is_approx(neckline1, neckline2)
                ):
                    return "SELL"

                if (
                    head < l_shoulder and head < r_shoulder
                    and is_approx(l_shoulder, r_shoulder)
                    and is_approx(neckline1, neckline2)
                ):
                    return "BUY"

            ### 2. Double Top / Bottom
            if len(prices) >= 3:
                if is_approx(prices[0], prices[2]) and prices[1] < prices[0]:
                    return "SELL"
                if is_approx(prices[0], prices[2]) and prices[1] > prices[0]:
                    return "BUY"
            ### 3. Triple Top / Bottom
            if len(prices) >= 5:
                if is_approx(prices[0], prices[2]) and is_approx(prices[2], prices[4]):
                    if prices[1] < prices[0] and prices[3] < prices[2]:
                        return {
                            "pattern": "Triple Top",
                            "signal": "SHORT",
                            "dates": segment_dates[:5].tolist(),
                            "prices": prices[:5].tolist()
                        }
                    if prices[1] > prices[0] and prices[3] > prices[2]:
                        return "BUY"

            ### 4. Cup & Handle
            if len(prices) >= 6:
                left = prices[0]
                bottom = min(prices[1:5])
                right = prices[5]
                if left > bottom and right > bottom and is_approx(left, right):
                    return "BUY"


        return None



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
                result = self.detect_final_reversal_pattern(data_up_to_idx) 
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
