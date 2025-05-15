import numpy as np


def compute_sharpe(strat):
    """compute sharpe ratio

    Args:
        strat (_type_): _description_

    Returns:
        _type_: _description_
    """
    sharpe = (strat.mean() * 365 * 24) / (strat.std() * np.sqrt(365 * 24))
    return sharpe

def backtest_from_strat(strat_obj, bench, start=None, end=None, params={}, bench_target='hourly_return_open', plot_enable=True, sharp_treshold=0.99, vol_treshold=0.33,
                        return_treshold = 0.01, drawdown_treshold = -0.3, runup_treshold = 0.05,save_plot_enable=True, trading_fees = 0.001, win_treshold=0.45, loss_treshold=0.55, flat_treshold = 0.1):
    """Backtest a strategy from the strategy class

    Args:
        strat_obj (_type_): _description_
        bench (_type_): _description_
        start (_type_, optional): _description_. Defaults to None.
        end (_type_, optional): _description_. Defaults to None.
        params (dict, optional): _description_. Defaults to {}.
        bench_target (str, optional): _description_. Defaults to 'hourly_return_open'.
        plot_enable (bool, optional): _description_. Defaults to True.
        sharp_treshold (float, optional): _description_. Defaults to 0.99.
        vol_treshold (float, optional): _description_. Defaults to 0.33.
        return_treshold (float, optional): _description_. Defaults to 0.01.
        drawdown_treshold (float, optional): _description_. Defaults to -0.3.
        save_plot_enable (bool, optional): _description_. Defaults to True.
        trading_fees (float, optional): _description_. Defaults to 0.001.
    """
    signal = strat_obj.compute_signal(bench, start=start, end=end, **params)
    signal = signal.fillna(0)
    strat = signal * bench[bench_target]
    strat -= (signal.diff().abs() * trading_fees)
    # Metrics calculus
    sharpe = compute_sharpe(strat)
    annualized_returns = (strat.mean() * 365 * 24)
    annualized_vol = (strat.std() * np.sqrt(365 * 24))
    drawdown = strat - strat.cummax()
    max_drawdown = drawdown.min()
    runup = strat - strat.cummin()
    max_runup = runup.max()


    nbr_position = (signal != 0).sum()
    win_position = (strat  > 0).sum()
    loss_position = (strat < 0).sum()
    flat_position = (strat == 0).sum()
    total_position = win_position + loss_position + flat_position
    print(f'== \033[96m{strat_obj.name} \033[0m==\n')
    strat_obj.describe()
    print('let\'s print some metrics\n')
    print(f"number of non flat positions: {nbr_position}")
    print(f"number of winning positions: {"\033[92m" if win_position / total_position > win_treshold else '\033[91m'} {win_position / total_position:.2%}\033[0m")
    print(f"number of loosing positions (including fees after returning flat): {"\033[92m" if loss_position / total_position < loss_treshold else '\033[91m'} {loss_position / total_position:.2%}\033[0m")
    print(f"number of flat positions: {"\033[92m" if flat_position / total_position < flat_position else '\033[91m'} {flat_position / total_position:.2%}\033[0m")
    print(f"Annualized Return: {"\033[92m" if annualized_returns > return_treshold else '\033[91m'} {annualized_returns:.2%}\033[0m")
    print(f"Annualized Volatility:{"\033[92m" if annualized_vol < vol_treshold else '\033[91m'} {annualized_vol:.2%}\033[0m")
    print(f"Sharpe Ratio: {"\033[92m" if sharpe > sharp_treshold else '\033[91m'} {sharpe:.2f}\033[0m")
    print(f"Max Drawdown: {"\033[92m" if max_drawdown > drawdown_treshold else '\033[91m'} {max_drawdown:.2%}\033[0m")
    print(f"Max Run-Up: {"\033[92m" if max_runup > runup_treshold else '\033[91m'} {max_runup:.2%}\033[0m\n\n")
    bench_to_plot = bench[bench_target]
    if start and end:
        bench_to_plot = bench_to_plot[start:end]
    elif start:
        bench_to_plot = bench_to_plot[start:]
    elif end:
        bench_to_plot = bench_to_plot[end:]
    if plot_enable:
        plot_strategy_and_benchmark(strat.cumsum(), bench_to_plot.cumsum(), title=strat_obj.name)
    start_str = 'lowest' if start is None else str(start)
    end_str = 'highest' if end is None else str(end)
    if save_plot_enable:
        save_strategy_and_benchmark(strat.cumsum(), bench_to_plot.cumsum(), title=f"{strat_obj.name}",save_path=f'./output/{strat_obj.name}_from_{start_str}_to_{end_str}.png')


def backtest_from_func(func, bench, start=None, end=None, params={}, bench_target='hourly_return_open', name="strat", plot_enable=True, trading_fees=0.002):
    """backtest from a function

    Args:
        func (_type_): _description_
        bench (_type_): _description_
        start (_type_, optional): _description_. Defaults to None.
        end (_type_, optional): _description_. Defaults to None.
        params (dict, optional): _description_. Defaults to {}.
        bench_target (str, optional): _description_. Defaults to 'hourly_return_open'.
        name (str, optional): _description_. Defaults to "strat".
        plot_enable (bool, optional): _description_. Defaults to True.
        trading_fees (float, optional): _description_. Defaults to 0.002.
    """
    signal = func(bench, start=start, end=end, **params)
    strat = signal * bench[bench_target]
    strat -= (signal.diff().abs() * trading_fees)
    sharpe = compute_sharpe(strat)
    annualized_returns = (strat.mean() * 365 * 24)
    annualized_vol = (strat.std() * np.sqrt(365 * 24))
    drawdown = strat - strat.cummax()
    max_drawdown = drawdown.min()
    print('let\'s print some metrics\n')
    print(f"Annualized Return: {annualized_returns:.2%}")
    print(f"Annualized Volatility: {annualized_vol:.2%}")
    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2%}")
    bench_to_plot = bench[bench_target]
    if start and end:
        bench_to_plot = bench_to_plot[start:end]
    elif start:
        bench_to_plot = bench_to_plot[start:]
    elif end:
        bench_to_plot = bench_to_plot[end:]
    if plot_enable:
        plot_strategy_and_benchmark(strat.cumsum(), bench_to_plot.cumsum())
    start_str = 'lowest' if start is None else str(start)
    end_str = 'highest' if end is None else str(end)
    save_strategy_and_benchmark(strat.cumsum(), bench_to_plot.cumsum(), title=f"{name}",save_path=f'./output/{name}_from_{start_str}_to_{end_str}.png')



import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.io as pio

def load_plotly_theme():

    green_plot = go.layout.Template()
    #green_plot.layout.update(font=dict(color="white", size=10, family='../NHaasGroteskDSPro-95Blk.otf'))
    green_plot.layout.update(font=dict(color="white", size=14))
    #green_plot.layout.update(font=dict(color="white", size=20, family='NHaasGroteskDSPro-95Blk'))
    green_plot.layout.update(paper_bgcolor='black')
    green_plot.layout.update(plot_bgcolor='black')
    green_plot.layout.update(xaxis=dict(
            showgrid=False, gridcolor="gray",  # Grille en gris
            zeroline=False, tickcolor="white", tickfont=dict(color="white")

        ),
        yaxis=dict(
            showgrid=True, gridcolor="gray",  # Grille en gris
            zeroline=False, tickcolor="white", tickfont=dict(color="white"), # ticks ou ecriture sur l'axe des ordonnées
            tickformat='.0%'

        ))
    green_plot.data.scatter = [
                            go.Scatter(line=dict(color='green')),
                            go.Scatter(line=dict(color='white')),
                            go.Scatter(line=dict(color='cyan'))
                            ]


    pio.templates['green_plot'] = green_plot

def plot_strategy_and_benchmark(strat : pd.Series, benchmark : pd.Series, legend_strat_title="strat", legend_benchmark_title="benchmark", width=1800, height=600, is_strat_secondary_y_axis=False
                                ,title="Sah", x_axis_title='Time', y_axis_title="Performance", y_axis_secondary_title="<b>performance</b> strat", has_to_save=False,save_path="./strat",save_extension='png'):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    

    # Add traces
    fig.add_trace(
        go.Scatter(x=strat.index , y=strat, name=legend_strat_title,mode='lines'
    ),
        secondary_y=is_strat_secondary_y_axis
    )

    fig.add_trace(
        go.Scatter(x=benchmark.index, y=benchmark, name=legend_benchmark_title),
        secondary_y=False,
    )
    #fig.add_trace(
    #    go.Scatter(x=benchmark.index, y=benchmark, name="benchmark returns", line=dict(color='white')),
    #    secondary_y=False,
    #)

    # Add figure title
    fig.update_layout(
        title_text=title,
        template="green_plot"
    )

    # Set x-axis title
    fig.update_xaxes(title_text=x_axis_title)

    # Set y-axes titles
    fig.update_yaxes(title_text=y_axis_title, secondary_y=False)
    if is_strat_secondary_y_axis:
        fig.update_yaxes(title_text=y_axis_secondary_title, secondary_y=True)
    

    #bench white
    # strat yellow
    #background black ou gris fonce
    #writtings white

    if (has_to_save):
        fig.write_image(save_path,format=save_extension, width=width, height=height)
    fig.show()

def save_strategy_and_benchmark(strat : pd.Series, benchmark : pd.Series, legend_strat_title="strat", legend_benchmark_title="benchmark", width=1800, height=600, is_strat_secondary_y_axis=False
                                ,title="Sah", x_axis_title='Time', y_axis_title="Performance", y_axis_secondary_title="<b>performance</b> strat", has_to_save=False,save_path="./strat",save_extension='png'):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    

    # Add traces
    fig.add_trace(
        go.Scatter(x=strat.index , y=strat, name=legend_strat_title,mode='lines'
    ),
        secondary_y=is_strat_secondary_y_axis
    )

    fig.add_trace(
        go.Scatter(x=benchmark.index, y=benchmark, name=legend_benchmark_title),
        secondary_y=False,
    )
    #fig.add_trace(
    #    go.Scatter(x=benchmark.index, y=benchmark, name="benchmark returns", line=dict(color='white')),
    #    secondary_y=False,
    #)

    # Add figure title
    fig.update_layout(
        title_text=title,
        template="green_plot"
    )

    # Set x-axis title
    fig.update_xaxes(title_text=x_axis_title)

    # Set y-axes titles
    fig.update_yaxes(title_text=y_axis_title, secondary_y=False)
    if is_strat_secondary_y_axis:
        fig.update_yaxes(title_text=y_axis_secondary_title, secondary_y=True)
    

    #bench white
    # strat yellow
    #background black ou gris fonce
    #writtings white

    fig.write_image(save_path,format=save_extension, width=width, height=height)