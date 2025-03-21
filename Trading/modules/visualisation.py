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
        self.overbought_th = 85
        self.oversold_th = 15
        self.close_th = 50
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
        """ Update RSI values dynamically and mark key levels. """
        if ticker not in self.rsi_data:
            return
    
        self.rsi_data[ticker].append(rsi_value)
        self.timestamps[ticker].append(timestamp)
    
        # Find trace index
        trace_index = self.tickers.index(ticker)
    
        # Check if the RSI crosses thresholds
        marker_color = None
        if rsi_value >= self.overbought_th:
            marker_color = "red"  # Overbought (short entry)
        elif rsi_value <= self.oversold_th:
            marker_color = "green"  # Oversold (long entry)
    
        with self.fig.batch_update():
            # Update the main RSI line
            self.fig.data[trace_index].x = self.timestamps[ticker]
            self.fig.data[trace_index].y = self.rsi_data[ticker]
    
            # Add a marker when crossing thresholds
            if marker_color:
                self.fig.add_trace(go.Scatter(
                    x=[timestamp], 
                    y=[rsi_value], 
                    mode="markers", 
                    marker=dict(color=marker_color, size=8),
                    showlegend=False
                ))