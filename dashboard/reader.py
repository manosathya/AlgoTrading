import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def read_ohlc_data(symbol=None, count=50):
    data = []
    keys = [f"alpaca:{symbol}"] if symbol else list(r.scan_iter("alpaca:*"))

    for key in keys:
        entries = r.xrevrange(key, count=count)
        for _, item in entries:
            item["symbol"] = item.get("symbol") or key.split(":")[-1]
            data.append(item)

    return sorted(data, key=lambda x: x.get("timestamp"), reverse=True)

def get_config_status(key):
    return r.hget(f"configs:{key}", 'status')

def get_indicator_fig():
    return r.get("current_plot")