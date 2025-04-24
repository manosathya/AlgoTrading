from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from components import render_publisher_stream
from callbacks import register_publisher_callbacks

app = Dash(external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    dcc.Store(id="publisher-store"),
    
    html.Div([
        html.H4("Publisher Config"),
        html.P("...Config Options..."),
        html.H4("Strategy Config"),
        html.P("...Strategy Options...")
    ], className="p-3"),

    dcc.Tabs(id="main-tabs", value="tab-overview", children=[
        dcc.Tab(label="Overview", value="tab-overview"),
        dcc.Tab(label="Publisher Stream", value="tab-publisher"),
        dcc.Tab(label="Trade Log", value="tab-trades"),
        dcc.Tab(label="RSI Graph", value="tab-rsi")
    ]),

    html.Div(id="tab-content", className="p-4")
])

@app.callback(
    Output("tab-content", "children"),
    Input("main-tabs", "value")
)
def render_tab_content(active_tab):
    if active_tab == "tab-overview":
        return html.Div("Overview content goes here.")
    elif active_tab == "tab-publisher":
        return render_publisher_stream()
    return html.Div("No content available.")

register_publisher_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)