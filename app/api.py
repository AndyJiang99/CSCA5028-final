from flask import Blueprint, jsonify
from app.services import get_stock_data

api = Blueprint('api', __name__)

@api.route('/api/stock/<string:symbol>')
def get_stock(symbol):
    data = get_stock_data(symbol.upper())
    if data is None or data.empty:
        return jsonify({'error': f'Data not found for symbol {symbol}'}), 404
    
    # Convert DataFrame to JSON
    return jsonify(data.to_dict(orient='split'))
