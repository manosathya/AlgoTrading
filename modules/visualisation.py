import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime
from IPython.display import display
from collections import deque

class DynamicPlotter:
    def __init__(self, tickers, fig_config=dict(), plot_type='dash'):
        
        self.tickers = tickers
        self.y_data = {ticker: [] for ticker in tickers}
        self.timestamps = {ticker: [] for ticker in tickers}
        self.positions = {ticker: deque((None, None), maxlen=2) for ticker in tickers}
        
        self.fig = go.FigureWidget()
        for ticker in tickers:
            self.fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name=ticker))
                    
        self.fig.update_layout(
            title= fig_config.get('title',""),
            xaxis_title=fig_config.get('xlabel',"Time"),
            yaxis_title=fig_config.get('ylabel',""),
            yaxis=dict(range=[0, 100]),
            width=1200,
            height=450
        )

        if plot_type == 'jupyter':
            display(self.fig)  

    def update(self, ticker, timestamp, y_value, position):
        """ 
        Update RSI values dynamically and mark entry/exit levels. 
        """
    
        if ticker not in self.y_data:
            return
        
        self.y_data[ticker].append(y_value)
        self.timestamps[ticker].append(timestamp)
        trace_index = self.tickers.index(ticker)
    
        # Check if the RSI crosses thresholds, mark entry/exit/close
        self.positions[ticker].append(position)
        marker_symbol = None
        marker_size = 7
        if self.positions[ticker][1] == 'short':
            marker_color = "red"  # Overbought (short entry)
            if not self.positions[ticker][0]:
                marker_symbol = "triangle-down"          
        elif self.positions[ticker][1] == 'long':
            marker_color = "green"  # Oversold (long entry)
            if not self.positions[ticker][0]:
                marker_symbol = "triangle-up"   
        elif self.positions[ticker][0] and not self.positions[ticker][1]:
            marker_symbol = "star"
            if self.positions[ticker][0] == 'long':
                marker_color = "green"
            if self.positions[ticker][0] == 'short':
                marker_color = "red"
            
            
        with self.fig.batch_update():
            # Update the main RSI line
            self.fig.data[trace_index].x = self.timestamps[ticker]
            self.fig.data[trace_index].y = self.y_data[ticker]
    
            # Add a marker when crossing thresholds
            if marker_symbol:
                self.fig.add_trace(go.Scatter(
                    x=[timestamp], 
                    y=[y_value], 
                    mode="markers+lines", 
                    marker=dict(color=marker_color, symbol=marker_symbol, size=marker_size),
                    showlegend=False
                ))