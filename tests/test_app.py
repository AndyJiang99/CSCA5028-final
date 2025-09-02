import pytest
from app import create_app
import pandas as pd
import json

@pytest.fixture
def client(mocker):
    # Mock the redis client before creating the app
    mock_redis_client = mocker.Mock()
    mock_redis_client.get.return_value = None # Simulate cache miss
    mocker.patch('app.__init__.redis.from_url', return_value=mock_redis_client)
    
    app = create_app()
    app.config['TESTING'] = True
    app.redis_client = mock_redis_client # Ensure app uses the mock

    with app.test_client() as client:
        yield client

def test_get_stock_data_success(client, mocker):
    """Test the stock data page with a successful API call."""
    # Mock the service function that calls the external API
    mock_data = pd.DataFrame({'4. close': [150.0]})
    # We now patch the call inside services.py where the API call is made
    mocker.patch('app.services.TimeSeries.get_daily', return_value=(mock_data, {}))

    # Simulate a POST request to the index page
    response = client.post('/', data={'symbol': 'AAPL'}, follow_redirects=True)

    assert response.status_code == 200
    assert b'Stock Data for AAPL' in response.data
    assert b'150' in response.data
    # Check if redis setex was called
    client.application.redis_client.setex.assert_called_once()

def test_get_stock_data_not_found(client, mocker):
    """Test the stock data page when the stock is not found."""
    # Mock the service function to raise an exception, as it would in case of a bad symbol
    mocker.patch('app.services.TimeSeries.get_daily', side_effect=Exception("Not found"))

    response = client.post('/', data={'symbol': 'FAKESYMBOL'}, follow_redirects=True)

    assert response.status_code == 200
    assert b'Stock symbol \'FAKESYMBOL\' not found' in response.data

def test_caching_works(client, mocker):
    """Test that data is served from cache on the second request."""
    # Mock the API call
    mock_data = pd.DataFrame({'4. close': [200.0]})
    mock_api_call = mocker.patch('app.services.TimeSeries.get_daily', return_value=(mock_data, {}))

    # First request, should call API and cache
    client.post('/', data={'symbol': 'TSLA'}, follow_redirects=True)
    mock_api_call.assert_called_once()

    # Now, simulate that the data is in the cache for the next request
    cached_json = json.dumps(mock_data.to_json(orient='split'))
    client.application.redis_client.get.return_value = cached_json

    # Second request, should NOT call API
    client.post('/', data={'symbol': 'TSLA'}, follow_redirects=True)
    mock_api_call.assert_called_once() # Should still be called only once in total

def test_api_get_stock_success(client, mocker):
    """Test the API endpoint with a successful call."""
    mock_data = pd.DataFrame({'4. close': [150.0]})
    mocker.patch('app.services.TimeSeries.get_daily', return_value=(mock_data, {}))

    response = client.get('/api/stock/AAPL')
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data['data'][0][0] == 150.0

def test_api_get_stock_not_found(client, mocker):
    """Test the API endpoint when the stock is not found."""
    mocker.patch('app.services.TimeSeries.get_daily', side_effect=Exception("Not found"))

    response = client.get('/api/stock/FAKESYMBOL')

    assert response.status_code == 404
    assert 'error' in response.get_json()

def test_metrics_endpoint(client):
    """Test that the /metrics endpoint is available."""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert response.content_type == 'text/plain; version=0.0.4; charset=utf-8'
