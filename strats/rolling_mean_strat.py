from strategy import strategy
import pandas as pd

class Momentum_Rolling_Mean(strategy):

    def __init__(self):
        super().__init__()
        self.name = 'momentum_rolling_mean'

    def load_data(self):
        return super().load_data()
    
    def describe(self):
        super().describe()
        text = 'The principle of this strategy is simple\n'
        text += 'We have to windows on long and the other one short\n'
        text += 'We go long when the mean of the long window applied on the close is lower than the one from the short window\n'
        text += 'We are short on the opposite\n'
        text += 'There is no flat on this strategy\n'
        text += '\n'

        print(text)
    
    def compute_signal(self, src_data : pd.DataFrame , start=None, end=None, limit=None,  window_short=10, window_long=20):
        if start and end:
            src_data = src_data[start:end]
        elif start:
            src_data = src_data[start:]
        elif end:
            src_data = src_data[:end]
        src_data = src_data["close"]
        signal = (src_data.rolling(window_short).mean() >src_data.rolling(window_long).mean()).astype(int)
        signal = signal.replace(0, -1)
        signal = signal.shift(1)
        return signal
