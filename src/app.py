import os
import json
from io import StringIO
from dotenv import load_dotenv

import pandas as pd
import redis
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt

from flask import Flask, jsonify, render_template, request, redirect, url_for, current_app
from alpha_vantage.timeseries import TimeSeries
from prometheus_flask_exporter import PrometheusMetrics

# --- Configuration ---
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-very-secret-key'
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

# --- Application Creation ---
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Redis
app.redis_client = redis.from_url(app.config['REDIS_URL'])

# Initialize Prometheus Metrics
metrics = PrometheusMetrics(app)

# --- Helper Functions ---

def get_stock_data(symbol):
    redis_client = app.redis_client
    cached_data = redis_client.get(symbol)

    if cached_data:
        return pd.read_json(StringIO(json.loads(cached_data)), orient='split')

    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    ts = TimeSeries(key=api_key, output_format='pandas')
    try:
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')
        redis_client.setex(symbol, 3600, json.dumps(data.to_json(orient='split')))
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_moving_average(data, window=20):
    if data is None or data.empty:
        return None
    close_col = '4. close'
    if close_col not in data.columns:
        for col in data.columns:
            if 'close' in col:
                close_col = col
                break
    if close_col not in data.columns:
        raise ValueError("Could not find closing price column in data")

    data_reversed = data.iloc[::-1]
    ma = data_reversed[close_col].rolling(window=window).mean()
    return ma.iloc[::-1]

def create_plot(data, symbol):
    static_dir = os.path.join('src', 'static', 'images')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    plot_data = data.iloc[::-1].tail(730)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(plot_data.index, plot_data['4. close'], label='Close Price', color='blue')
    ax.plot(plot_data.index, plot_data['200-Day MA'], label='200-Day MA', color='orange')
    ax.plot(plot_data.index, plot_data['500-Day MA'], label='500-Day MA', color='green')

    above_ma = plot_data[(plot_data['4. close'] > plot_data['200-Day MA']) & 
                         (plot_data['4. close'] > plot_data['500-Day MA'])]
    ax.scatter(above_ma.index, above_ma['4. close'], color='red', s=10, zorder=5)

    below_ma = plot_data[(plot_data['4. close'] < plot_data['200-Day MA']) & 
                         (plot_data['4. close'] < plot_data['500-Day MA'])]
    ax.scatter(below_ma.index, below_ma['4. close'], color='green', s=10, zorder=5)

    ax.set_title(f'{symbol.upper()} Closing Price and Moving Averages')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (USD)')
    ax.legend()
    ax.grid(True)
    fig.autofmt_xdate()

    plot_path = os.path.join(static_dir, f'{symbol}.png')
    fig.savefig(plot_path)
    plt.close(fig)

    return os.path.join('images', f'{symbol}.png')

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form['symbol']
        return redirect(url_for('stock_data', symbol=symbol))
    return render_template('index.html')

@app.route('/stock/<symbol>')
def stock_data(symbol):
    data = get_stock_data(symbol.upper())
    if data is None or data.empty:
        return render_template('stock_not_found.html', symbol=symbol)
    
    ma_200 = calculate_moving_average(data, window=200)
    ma_500 = calculate_moving_average(data, window=500)

    data['200-Day MA'] = ma_200
    data['500-Day MA'] = ma_500

    plot_url = create_plot(data, symbol)

    return render_template('stock_data.html', symbol=symbol, data=data.to_html(), plot_url=plot_url)

@app.route('/api/stock/<string:symbol>')
def get_stock(symbol):
    data = get_stock_data(symbol.upper())
    if data is None or data.empty:
        return jsonify({'error': f'Data not found for symbol {symbol}'}), 404
    
    return jsonify(data.to_dict(orient='split'))

if __name__ == '__main__':
    app.run(debug=True)
