from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import sys

# Add the current directory to the path so we can import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app

# Configure app for proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# For Vercel deployment
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dueltech.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# This is the handler that Vercel will call
def handler(request):
    # Vercel serverless function handler
    return app

# Make the app available for Vercel
app = app
