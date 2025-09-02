from flask import Blueprint, render_template, request, redirect, url_for
from app.services import get_stock_data
from app.analyzer import calculate_moving_average
from app.plotter import create_plot

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form['symbol']
        return redirect(url_for('main.stock_data', symbol=symbol))
    return render_template('index.html')

@main.route('/stock/<symbol>')
def stock_data(symbol):
    data = get_stock_data(symbol.upper())
    if data is None or data.empty:
        return render_template('stock_not_found.html', symbol=symbol)
    
    # Calculate moving averages
    ma_200 = calculate_moving_average(data, window=200)
    ma_500 = calculate_moving_average(data, window=500)

    # Add moving averages to the main dataframe for easier display
    data['200-Day MA'] = ma_200
    data['500-Day MA'] = ma_500

    # Generate plot
    plot_url = create_plot(data, symbol)

    return render_template('stock_data.html', symbol=symbol, data=data.to_html(), plot_url=plot_url)
