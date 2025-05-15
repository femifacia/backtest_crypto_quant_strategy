import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import plotly.io as pio

def plot_asset_candle(df : pd.DataFrame, last_n_points=None,title='Candlestick chart', xaxis_title='Date', yaxis_title='Price'):
    """Plot a bench candle style

    Args:
        df (pd.DataFrame): _description_
        last_n_points (_type_, optional): _description_. Defaults to None.
        title (str, optional): _description_. Defaults to 'Candlestick chart'.
        xaxis_title (str, optional): _description_. Defaults to 'Date'.
        yaxis_title (str, optional): _description_. Defaults to 'Price'.
    """
    if not (last_n_points is None):
        df = df.iloc[-last_n_points:]

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close']
    )])

    fig.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)
    fig.show()

def load_plotly_theme():
    """load plotly code
    """

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

    """plot strategy and benchmark
    """
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

def save_strategy_and_benchmark(strat : pd.Series, benchmark : pd.Series, legend_strat_title="strat", legend_benchmark_title="benchmark", width=1800, height=600, is_strat_secondary_y_axis=False,title="Sah",
                                 x_axis_title='Time', y_axis_title="Performance", y_axis_secondary_title="<b>performance</b> strat", has_to_save=False,save_path="./strat",save_extension='png'):
    """save the strategy and the benchmark

    Args:
        strat (pd.Series): _description_
        benchmark (pd.Series): _description_
        legend_strat_title (str, optional): _description_. Defaults to "strat".
        legend_benchmark_title (str, optional): _description_. Defaults to "benchmark".
        width (int, optional): _description_. Defaults to 1800.
        height (int, optional): _description_. Defaults to 600.
        is_strat_secondary_y_axis (bool, optional): _description_. Defaults to False.
        title (str, optional): _description_. Defaults to "Sah".
        x_axis_title (str, optional): _description_. Defaults to 'Time'.
        y_axis_title (str, optional): _description_. Defaults to "Performance".
        y_axis_secondary_title (str, optional): _description_. Defaults to "<b>performance</b> strat".
        has_to_save (bool, optional): _description_. Defaults to False.
        save_path (str, optional): _description_. Defaults to "./strat".
        save_extension (str, optional): _description_. Defaults to 'png'.
    """
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