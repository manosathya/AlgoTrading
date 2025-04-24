from dash.dependencies import Input, Output
from reader import read_ohlc_data
from dash import dash_table


def register_publisher_callbacks(app):
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
        Input("publisher-symbol-dropdown", "value")
    )
    def update_table_from_store(data, symbol):
        if not data:
            return [], []

        if symbol:
            data = [d for d in data if d.get("symbol") == symbol]

        columns = [{"name": k, "id": k} for k in data[0].keys()]
        return data, columns