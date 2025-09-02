import os
from alpha_vantage.timeseries import TimeSeries
from flask import current_app
import pandas as pd
import json
from io import StringIO

def get_stock_data(symbol):
    redis_client = current_app.redis_client
    cached_data = redis_client.get(symbol)

    if cached_data:
        # Data is in cache, load it
        # Use StringIO to avoid FutureWarning
        return pd.read_json(StringIO(json.loads(cached_data)), orient='split')

    # Data not in cache, fetch from API
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    ts = TimeSeries(key=api_key, output_format='pandas')
    try:
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')
        # Cache the data in Redis for 1 hour (3600 seconds)
        # We need to serialize the pandas DataFrame to store it
        redis_client.setex(symbol, 3600, json.dumps(data.to_json(orient='split')))
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
