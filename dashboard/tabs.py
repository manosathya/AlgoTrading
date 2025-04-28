from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc


def publisher_tab():
    return dbc.Container([
        html.H5("Live OHLC Stream", className="mb-3"),
        dcc.Dropdown(id="publisher-symbol-dropdown",
                     options =[],
                     placeholder="Select Symbol",
                     style={"width":"400px", "marginBottom":"20px"},
                     multi=True
        ),
        
        dash_table.DataTable(
            id="publisher-stream-table",
            columns=[], 
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            page_size=20
        ),
        
        dcc.Interval(id="update-publisher-stream", interval=10000)
    ])

def indicator_tab():
    return dbc.Container([
        html.H5("Indicator", className="mb-3"),
        dcc.Graph(
            id="indicator-graph",
        ),
        
        dcc.Interval(id="update-publisher-stream", interval=10000)
    ])