from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from tabs import publisher_tab, indicator_tab
from callbacks import publisher_callbacks, config_callbacks, indicator_callbacks

app = Dash(suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    dcc.Store(id="publisher-store"), 
    dcc.Store(id='config-store'),
        
    dbc.Col([
        dbc.Row([
            dbc.Col(html.H6("Publisher Config: "), width='auto'),
            dbc.Col(html.Div(id="publisher-status"), width='auto', style={'font-size':'13px'})
        ], align='baseline', className= 'mt-2 m-1'),  
    
        dbc.Row([
            dbc.Col(html.H6("Consumer Config: "), width='auto'),
            dbc.Col(html.Div(id="consumer-status"), width='auto', style={'font-size':'13px'})
        ], align='baseline', className= 'm-1')  
    ]),

    
    dcc.Interval(id="config-update", interval=10000),


    dcc.Tabs(id="main-tabs", value="tab-overview", 
        children=[
            dcc.Tab(label="Overview", value="tab-overview"),
            dcc.Tab(label="Publisher Stream", value="tab-publisher"),
            dcc.Tab(label="Trade Log", value="tab-trades"),
            dcc.Tab(label="Indicator", value="tab-indicator")
        ]
    ),

    html.Div(id="tab-content", className="p-4")
])

@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "value")
)
def tab_content(active_tab):
    if active_tab == "tab-overview":
        return html.Div("Overview content goes here.")
    elif active_tab == "tab-publisher":
        return publisher_tab()
    elif active_tab == 'tab-indicator':
        return indicator_tab()
    return html.Div("No content available.")



publisher_callbacks(app)
config_callbacks(app)
indicator_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)