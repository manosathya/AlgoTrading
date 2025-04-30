import json

def dict_to_table(config: dict, key_name="config", value_name="value"):
    """
    Converts a dictionary into a list of row dicts for Dash DataTable.
    - Attempts to parse JSON-like strings.
    - Lists/dicts are converted into comma-separated strings for cleaner display.

    Args:
        config (dict): Dictionary to convert.
        key_name (str): Column name for keys.
        value_name (str): Column name for values.

    Returns:
        Tuple of (data, columns) for use in dash_table.DataTable.
    """
    def format_value(v):
        try:
            v = json.loads(v) if isinstance(v, str) else v
        except (json.JSONDecodeError, TypeError):
            pass

        if isinstance(v, list):
            return ", ".join(map(str, v))
        elif isinstance(v, dict):
            return ", ".join(f"{k}: {v[k]}" for k in v)
        return str(v)

    data = [{key_name: k, value_name: format_value(v)} for k, v in config.items()]
    columns = [
        {"name": key_name, "id": key_name},
        {"name": value_name, "id": value_name}
    ]
    return data, columns