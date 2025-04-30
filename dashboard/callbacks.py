from dash.dependencies import Input, Output
from reader import read_ohlc_data, get_config_status, get_indicator_fig, get_subscriber_status
from dash import dash_table, html
from helpers import dict_to_table 

import plotly.graph_objects as go
import json

def run_callbacks(app):
    publisher_stream_cb(app)
    config_cb(app)
    indicator_cb(app)

def publisher_stream_cb(app):
    
    @app.callback(
        Output("publisher-store", "data"),
        Input("update-publisher-stream", "n_intervals"),
        prevent_initial_call=False
    )
    def fetch_data(_):
        return read_ohlc_data(count=50)

    
    @app.callback(
        Output("publisher-stream-table", "data"),
        Output("publisher-stream-table", "columns"),
        Input("publisher-store", "data"),
        Input("publisher-symbol-dropdown", "value")  # Added this
    )
    def update_table_from_store(data, symbols):
        if not data:
            return [], []

        if symbols:
            data = [d for d in data if d.get("symbol") in symbols]

        columns = [{"name": k, "id": k} for k in data[0].keys()]
        return data, columns


    @app.callback(
        Output("publisher-symbol-dropdown", "options"),
        Input("publisher-store", "data")
    )
    def update_dropdown_options(data):
        if not data:
            return []
    
        symbols = sorted(set(d.get("symbol") for d in data if "symbol" in d))
        return [{"label": s, "value": s} for s in symbols]


def config_cb(app):
    @app.callback(
        Output("publisher-config-table", "data"),
        Output("publisher-config-table", "columns"),
        Input("publisher-status-interval", "n_intervals")
    )
    def update_publisher_config(_):
        data = dict_to_table(get_config_status('publisher'))  
        if not data:
            return [], []
        return data

    @app.callback(
        Output("consumer-config-table", "data"),
        Output("consumer-config-table", "columns"),
        Input("consumer-status-interval", "n_intervals")
    )
    def update_publisher_config(_):
        data = dict_to_table(get_config_status('consumer'))  
        if not data:
            return [], []
        return data



def indicator_cb(app):
    @app.callback(
        Output("indicator-graph", "figure"),
        Input("config-update", "n_intervals")
    )
    def update_graph(n):
        fig_json = get_indicator_fig()
        if fig_json is None:
            return go.Figure()  # Return empty if no plot yet
    
        fig = go.Figure(**json.loads(fig_json))
        return fig
        
    @app.callback(
        Output("subscriber-status-table", "data"),
        Output("subscriber-status-table", "columns"),
        Input("subscriber-status-interval", "n_intervals")
    )
    def update_subscriber_status(_):
        data = get_subscriber_status()
        if not data:
            return [], []
        
        columns = columns = [{"name": k.capitalize(), "id": k} for k in (["ticker", "status"] + [k for k in data[0] if k not in ('ticker', 'status')])]
        return data, columns
