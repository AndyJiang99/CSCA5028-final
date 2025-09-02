from flask import Flask
from config import Config
import redis
from prometheus_flask_exporter import PrometheusMetrics

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Redis
    app.redis_client = redis.from_url(app.config['REDIS_URL'])

    # Initialize Prometheus Metrics
    metrics = PrometheusMetrics(app)

    # Register blueprints here
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    return app
