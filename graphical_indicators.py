import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import plotly.graph_objects as go


import pandas as pd
import numpy as np
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from itertools import combinations


def print_trend_lines(trendlines, df : pd.DataFrame):
    """print trend lines

    Args:
        trendlines (_type_): _description_
        df (pd.DataFrame): _description_
    """

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Candles"
    )])

    # Ajout des supports en vert (dashed)
        

    for i, j, k, coeffs in trendlines:
        x_vals = np.array([df.index.get_loc(i), df.index.get_loc(k)])
#        print(x_vals)
        y_vals = np.poly1d(coeffs)(x_vals)
        x_vals = np.array([i, k])
        fig.add_shape(
                type='line',
                x0=x_vals[0],
                y0 = y_vals[0],
                x1=x_vals[1],
                y1 = y_vals[1],
                line=dict(color='cyan', dash='dash'),
                name="Support"
            )

    fig.update_layout(
            title='Candlestick with Trendlines',
            xaxis_title='Date',
            yaxis_title='Price',
            template='plotly_dark'
        )

    fig.show()

def find_trendlines(df, order=5, tolerance=30, tresh=0.5, plot_enabled=True):
    """Find trendlines

    Args:
        df (_type_): _description_
        order (int, optional): _description_. Defaults to 5.
        tolerance (int, optional): _description_. Defaults to 30.
        tresh (float, optional): _description_. Defaults to 0.5.
        plot_enabled (bool, optional): _description_. Defaults to True.

    Returns:
        _type_: _description_
    """
    lows_idx = argrelextrema(df['low'].values, np.less_equal, order=order)[0]
    lows = df.iloc[lows_idx][['low']]

    valid_trendlines = []

    for i, j, k in combinations(lows.index, 3):
        x = np.array([df.index.get_loc(i), df.index.get_loc(k)])  # positions numériques
        y = np.array([df['low'].loc[i], df['low'].loc[k]])


        # Droite entre i et k
        coeffs = np.polyfit(x, y, 1)  # y = mx + b
        line = np.poly1d(coeffs)

        # Vérifie que le point j est bien proche de la ligne (tolérance)
        j_pos = df.index.get_loc(j)
        if abs(df['low'][j] - line(j_pos)) > tolerance:

            continue

        # Vérifie que les prix ne passent PAS sous la ligne entre i et k
        print(i,"fel",k)
        segment = df.loc[i:k]
        for idx in segment.index:
            x_idx = df.index.get_loc(idx)
            if (df['low'][idx] - line(x_idx) ) > tresh:

                break
            else:
                valid_trendlines.append((i, j, k, coeffs))

    if plot_enabled:
        print_trend_lines(valid_trendlines, df)

    return valid_trendlines


def detect_levels(df : pd.DataFrame, order=5):
    """Detect levels for horizontales support

    Args:
        df (pd.DataFrame): _description_
        order (int, optional): _description_. Defaults to 5.

    Returns:
        _type_: _description_
    """
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
    """Plot horizontal support resistances

    Args:
        df (pd.DataFrame): _description_
        threshold (float, optional): _description_. Defaults to 0.01.
    """

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