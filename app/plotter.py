import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend
import matplotlib.pyplot as plt
import os

def create_plot(data, symbol):
    """Generates and saves a plot of stock prices and moving averages."""
    # Ensure the static directory exists
    static_dir = os.path.join('app', 'static', 'images')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)

    # Reverse data to plot chronologically
    plot_data = data.iloc[::-1].tail(730) # Plot last ~2 years

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot closing price and moving averages
    ax.plot(plot_data.index, plot_data['4. close'], label='Close Price', color='blue')
    ax.plot(plot_data.index, plot_data['200-Day MA'], label='200-Day MA', color='orange')
    ax.plot(plot_data.index, plot_data['500-Day MA'], label='500-Day MA', color='green')

    # Add red dots where close is > 200-Day MA and > 500-Day MA
    above_ma = plot_data[(plot_data['4. close'] > plot_data['200-Day MA']) & 
                         (plot_data['4. close'] > plot_data['500-Day MA'])]
    ax.scatter(above_ma.index, above_ma['4. close'], color='red', s=10, zorder=5)

    # Add green dots where close is < 200-Day MA and < 500-Day MA
    below_ma = plot_data[(plot_data['4. close'] < plot_data['200-Day MA']) & 
                         (plot_data['4. close'] < plot_data['500-Day MA'])]
    ax.scatter(below_ma.index, below_ma['4. close'], color='green', s=10, zorder=5)

    # Formatting
    ax.set_title(f'{symbol.upper()} Closing Price and Moving Averages')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (USD)')
    ax.legend()
    ax.grid(True)
    fig.autofmt_xdate()

    # Save plot to a file
    plot_path = os.path.join(static_dir, f'{symbol}.png')
    fig.savefig(plot_path)
    plt.close(fig) # Close the figure to free up memory

    # Return the path relative to the static folder
    return os.path.join('images', f'{symbol}.png')
