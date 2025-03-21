import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
from IPython.display import display
from collections import deque

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

        self.positions = {ticker: deque((None, None), maxlen=2) for ticker in tickers}
        
        display(self.fig)  # Display the interactive figure in Jupyter Notebook

    def update(self, rsi_value, ticker, timestamp, position):
        """ Update RSI values dynamically and mark key levels. """
        if ticker not in self.rsi_data:
            return
        
        self.rsi_data[ticker].append(rsi_value)
        self.timestamps[ticker].append(timestamp)
        trace_index = self.tickers.index(ticker)
    
        # Check if the RSI crosses thresholds, mark entry/exit/close
        self.positions[ticker].append(position)
        marker_symbol = None
        if self.positions[ticker][1] == 'short':
            marker_color = "red"  # Overbought (short entry)
            if not self.positions[ticker][0]:
                marker_symbol = "star" 
                marker_size = 7
        elif self.positions[ticker][1] == 'long':
            marker_color = "green"  # Oversold (long entry)
            if not self.positions[ticker][0]:
                marker_symbol = "star"
                marker_size = 7     
        elif self.positions[ticker][0] and not self.positions[ticker][1]:
            marker_color = "purple"
            marker_symbol = "star"
            marker_size = 7

            
            
        with self.fig.batch_update():
            # Update the main RSI line
            self.fig.data[trace_index].x = self.timestamps[ticker]
            self.fig.data[trace_index].y = self.rsi_data[ticker]
    
            # Add a marker when crossing thresholds
            if marker_symbol:
                self.fig.add_trace(go.Scatter(
                    x=[timestamp], 
                    y=[rsi_value], 
                    mode="markers+lines", 
                    marker=dict(color=marker_color, symbol=marker_symbol, size=marker_size),
                    showlegend=False
                ))