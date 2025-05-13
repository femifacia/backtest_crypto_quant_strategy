from strategy import strategy
import pandas as pd

class RSI_IBS(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'RSI'

    def load_data(self):
        return super().load_data()
    
    def describe(self):
        super().describe()
        text = """This strategy identifies short-term reversal opportunities using two technical indicators: RSI and IBS.
A long position is opened when the RSI is below 30 (indicating oversold conditions) and the IBS is below 0.2 (close near the day's low),
while a short position is initiated when the RSI exceeds 70 (overbought) and the IBS is above 0.8 (close near the day's high).
Each trade is then automatically closed if the price moves +2% (take profit) or -1% (stop loss) from the entry price.
Outside of these conditions, the strategy remains flat to avoid uncertain market phases.\n"""
        text += '\n'

        print(text)
    
    def compute_signal(self, src_data : pd.DataFrame , start=None, end=None, limit=None,  rsi_period=10):
        if start and end:
            src_data = src_data[start:end]
        elif start:
            src_data = src_data[start:]
        elif end:
            src_data = src_data[:end]
        df = src_data.copy()
        src_data = src_data["close"]
        delta = src_data.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
        avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()

        relative_strength = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + relative_strength))

        ibs = (df['close'] - df['low']) / (df['high'] - df['low'])
        df['IBS'] = ibs
        df['signal'] = 0
        df['RSI'] = rsi
        df.loc[(df['RSI'] < 30) & (df['IBS'] < 0.2), 'signal'] = 1   # Long
        df.loc[(df['RSI'] > 70) & (df['IBS'] > 0.8), 'signal'] = -1
#        signal = (src_data.rolling(window_short).mean() >src_data.rolling(window_long).mean()).astype(int)
#        signal = signal.replace(0, -1)
#        signal = signal.shift(1)
        return df['signal'].shift(1)


    def compute_signal_with_exit(self, src_data: pd.DataFrame, start=None, end=None, limit=None, rsi_period=10,
                                tp_pct=0.02, sl_pct=0.01):
        if start and end:
            src_data = src_data[start:end]
        elif start:
            src_data = src_data[start:]
        elif end:
            src_data = src_data[:end]

        df = src_data.copy()
        close = df["close"]
        delta = close.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=rsi_period, min_periods=rsi_period).mean()
        avg_loss = loss.rolling(window=rsi_period, min_periods=rsi_period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        ibs = (df['close'] - df['low']) / (df['high'] - df['low'])

        df['RSI'] = rsi
        df['IBS'] = ibs
        df['signal'] = 0
        df.loc[(df['RSI'] < 30) & (df['IBS'] < 0.2), 'signal'] = 1  # Long
        df.loc[(df['RSI'] > 70) & (df['IBS'] > 0.8), 'signal'] = -1  # Short

        df['position'] = 0  # Position active (1 = long, -1 = short, 0 = flat)
        df['exit_reason'] = None
        in_trade = False

        for i in range(len(df)):
            if in_trade:
                # Check if TP or SL hit
                entry_price = df.loc[entry_idx, 'close']
                current_price = df.loc[i, 'close']
                direction = df.loc[entry_idx, 'signal']

                change_pct = (current_price - entry_price) / entry_price * direction

                if change_pct >= tp_pct:
                    df.loc[i, 'exit_reason'] = 'TP'
                    in_trade = False
                elif change_pct <= -sl_pct:
                    df.loc[i, 'exit_reason'] = 'SL'
                    in_trade = False
                else:
                    df.loc[i, 'position'] = direction
            elif df.loc[i, 'signal'] != 0:
                # Entry signal
                entry_idx = i
                in_trade = True
                df.loc[i, 'position'] = df.loc[i, 'signal']

        return df
