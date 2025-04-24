from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def render_publisher_stream():
    return dbc.Container([
        html.H5("Live OHLC Stream", className="mb-3"),
        dcc.Dropdown(id="publisher-symbol-dropdown", placeholder="Select Ticker", style={"color": "#000"}),
        
        dash_table.DataTable(
            id="publisher-stream-table",
            columns=[], 
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            page_size=20
        ),
        
        dcc.Interval(id="update-publisher-stream", interval=2000, n_intervals=0)
    ])