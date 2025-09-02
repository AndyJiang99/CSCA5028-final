# stock_app

A Python-based stock analysis web application built with Flask. This application fetches stock data, performs analysis, and provides a web interface and a REST API.

## Features

- Web interface to view daily stock data.
- Data analysis (Simple Moving Average).
- REST API to expose stock data in JSON format.
- Caching with Redis to improve performance.
- Unit and integration tests with `pytest`.
- Continuous Integration and Deployment (CI/CD) with GitHub Actions and Heroku.
- Production monitoring with Prometheus.

## Prerequisites

- Python 3.9+
- Redis
- A free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd stock_app
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment variables:**
    -   Rename the `.env.example` file to `.env` (or create a new `.env` file).
    -   Open the `.env` file and add your Alpha Vantage API key:
        ```
        SECRET_KEY='a-super-secret-key'
        ALPHA_VANTAGE_API_KEY='YOUR_ALPHA_VANTAGE_API_KEY'
        REDIS_URL='redis://localhost:6379/0'
        ```

## Running the Application

1.  **Start the Flask development server:**
    ```bash
    flask run
    ```
    Or directly run the main file:
    ```bash
    python main.py
    ```

2.  Open your web browser and navigate to `http://127.0.0.1:5000`.

## Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

## API Endpoint

The application provides a REST API to fetch stock data.

-   **URL**: `/api/stock/<symbol>`
-   **Method**: `GET`
-   **Success Response**:
    ```json
    {
      "columns": ["4. close", "Moving Average"],
      "data": [[150.0, null]],
      "index": [1622159400000]
    }
    ```
-   **Error Response**:
    ```json
    {
      "error": "Data not found for symbol FAKESYMBOL"
    }
    ```

## Deployment

This project is configured for continuous deployment to Heroku via GitHub Actions. The workflow is defined in `.github/workflows/ci.yml`. For the deployment to work, you must configure the `HEROKU_API_KEY`, `HEROKU_APP_NAME`, and `HEROKU_EMAIL` secrets in your GitHub repository settings.
