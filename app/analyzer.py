import pandas as pd

def calculate_moving_average(data, window=20):
    """Calculates the simple moving average for the closing price."""
    if data is None or data.empty:
        return None
    # The column name from alpha-vantage is '4. close'
    close_col = '4. close'
    if close_col not in data.columns:
        # Sometimes column names might have different spacing
        for col in data.columns:
            if 'close' in col:
                close_col = col
                break
    if close_col not in data.columns:
        raise ValueError("Could not find closing price column in data")

    # Data is newest to oldest, reverse it for calculation
    data_reversed = data.iloc[::-1]
    ma = data_reversed[close_col].rolling(window=window).mean()
    # Reverse it back to match original order
    return ma.iloc[::-1]
