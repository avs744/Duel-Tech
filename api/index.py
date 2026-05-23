
import sys
import os
from flask import Flask

# allow import from root folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel needs THIS variable
app = app

# handler for Vercel
def handler(request):
    return app

