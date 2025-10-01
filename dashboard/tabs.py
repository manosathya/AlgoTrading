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
        
        dcc.Interval(id="config-update", interval=5000)
    ])

def status_tab():
    return html.Div([
        html.H5("Subscriber Status"),
        dash_table.DataTable(
            id="subscriber-status-table",
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'padding': '5px'},
            style_header={'fontWeight': 'bold'},
        ),
        dcc.Interval(id="subscriber-status-interval", interval=2000)
    ])


def config_tab():
    
    def config_section(title, table_id, interval_id, interval=2000):
        return dbc.Col(
            html.Div([
                html.H5(title),
                dash_table.DataTable(
                    id=table_id,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'center', 'padding': '5px'},
                    style_header={'fontWeight': 'bold'},
                ),
                dcc.Interval(id=interval_id, interval=interval)
            ])
        )

    return dbc.Row([
        config_section("Publisher Config", "publisher-config-table", "publisher-status-interval"),
        config_section("Consumer Config", "consumer-config-table", "consumer-status-interval")
    ])