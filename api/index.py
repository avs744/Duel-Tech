import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# REQUIRED for Vercel
def handler(event, context):
    return app

