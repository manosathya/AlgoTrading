import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
from IPython.display import display

class RSIPlotter:
    def __init__(self, tickers):
        self.tickers = tickers
        self.rsi_data = {ticker: [] for ticker in tickers}
        self.timestamps = {ticker: [] for ticker in tickers}

        # Create a FigureWidget instead of a regular Figure
        self.fig = go.FigureWidget()

        # Add traces for each ticker
        for ticker in tickers:
            self.fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name=ticker))

        # Set layout
        self.fig.update_layout(
            title="RSI Values",
            xaxis_title="Time",
            yaxis_title="RSI",
            yaxis=dict(range=[0, 100]),
        )

        display(self.fig)  # Display the interactive figure in Jupyter Notebook

    def update(self, rsi_value, ticker, timestamp):
        """ Update the existing figure without creating new traces. """
        if ticker not in self.rsi_data:
            return

        self.rsi_data[ticker].append(rsi_value)
        self.timestamps[ticker].append(timestamp)

        # Find the index of the trace corresponding to the ticker
        trace_index = self.tickers.index(ticker)

        # Update the trace dynamically using FigureWidget
        with self.fig.batch_update():
            self.fig.data[trace_index].x = self.timestamps[ticker]
            self.fig.data[trace_index].y = self.rsi_data[ticker]