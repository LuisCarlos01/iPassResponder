"""
Automated Email Response System - Web Interface

This module provides a Flask-based web interface for the automated email 
response system, allowing users to view, add, and modify response rules.
"""

import os
import logging
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Create extension
db = SQLAlchemy(model_class=Base)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_testing")

# Fix for correct URL generation behind proxies
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///instance/email_autoresponder.db"
)
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300,
}

# Configure bootstrap template
app.config["BOOTSTRAP_SERVE_LOCAL"] = True

# Initialize extensions
db.init_app(app)

# Register routes
with app.app_context():
    # Import models here to avoid circular imports
    import models  # noqa: F401
    from routes import register_routes

    # Create tables
    db.create_all()

    # Register routes
    register_routes(app)

# Add template filters
@app.template_filter('truncate_text')
def truncate_text(text, length=100):
    """Truncate text to specified length."""
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length] + "..."

@app.template_filter('format_datetime')
def format_datetime(dt):
    """Format datetime for display."""
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else ""