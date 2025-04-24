from dash.dependencies import Input, Output
from reader import read_ohlc_data
from dash import dash_table


def publisher_callbacks(app):
    
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