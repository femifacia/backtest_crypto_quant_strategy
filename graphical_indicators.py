import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import plotly.graph_objects as go


def detect_levels(df : pd.DataFrame, order=5):
    local_max = argrelextrema(df['high'].values, np.greater_equal, order=order)[0]
    local_min = argrelextrema(df['low'].values, np.less_equal, order=order)[0]

    resistance_levels = df.iloc[local_max]['high']
    support_levels = df.iloc[local_min]['low']

    return support_levels, resistance_levels

def filter_levels(levels, threshold=0.01):
    """
    Élimine les niveaux trop proches. Le threshold est exprimé en pourcentage.
    """
    filtered = []
    for level in sorted(levels):
        if all(abs(level - prev) / prev > threshold for prev in filtered):
            filtered.append(level)
    return filtered

def plot_horizontal_supports_resistances(df : pd.DataFrame, threshold=0.01):
    support_raw, resistance_raw = detect_levels(df, order=5)

    # 2. Filtrage (1% d'écart minimum)
    support_levels = filter_levels(support_raw, threshold=threshold)
    resistance_levels = filter_levels(resistance_raw, threshold=threshold)

    # ==== Étape 4 : Candlestick chart avec Plotly ====
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Candles"
    )])

    # Ajout des supports en vert (dashed)
    for level in support_levels:
        fig.add_shape(
            type='line',
            x0=df.index[0],
            x1=df.index[-1],
            y0=level,
            y1=level,
            line=dict(color='green', dash='dash'),
            name="Support"
        )

    # Ajout des résistances en rouge (dashed)
    for level in resistance_levels:
        fig.add_shape(
            type='line',
            x0=df.index[0],
            x1=df.index[-1],
            y0=level,
            y1=level,
            line=dict(color='red', dash='dash'),
            name="Resistance"
        )

    # Mise en forme
    fig.update_layout(
        title='Candlestick with Support and Resistance',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark'
    )

    fig.show()