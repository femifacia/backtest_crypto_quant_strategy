import pandas as pd

class strategy :
    def __init__(self):
          self.signal = None
          self.bench = None
          self.name= "Strat"
          self.bench_name = 'BTCUSDT'

    def describe(self):
        """describe the strat
        """
        text = f"Strategy name: {self.name}\n"
        text += f"Asset Targeted: {self.bench_name}\n"
        print(text)

    def compute_signal(self, src_data : pd.DataFrame, start=None, end=None, limit=None):
        """Compute The signal

        Args:
            src_data (pd.DataFrame): _description_
            start (_type_, optional): _description_. Defaults to None.
            end (_type_, optional): _description_. Defaults to None.
            limit (_type_, optional): _description_. Defaults to None.
        """
        pass

    def load_data(self):
        pass