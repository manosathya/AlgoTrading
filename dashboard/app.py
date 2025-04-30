from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from tabs import publisher_tab, indicator_tab, status_tab, config_tab
from callbacks import run_callbacks

app = Dash(suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    dcc.Store(id="publisher-store"), 
    dcc.Store(id='config-store'),

    dcc.Tabs(id="main-tabs", value="tab-status", 
        children=[
            dcc.Tab(label="Configs", value="tab-config"),
            dcc.Tab(label="Status", value="tab-status"),
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
    if active_tab == "tab-status":
        return status_tab()
    elif active_tab == 'tab-config':
        return config_tab()
    elif active_tab == "tab-publisher":
        return publisher_tab()
    elif active_tab == 'tab-indicator':
        return indicator_tab()
    return html.Div("No content available.")



run_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)