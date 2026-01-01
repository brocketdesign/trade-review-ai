#!/usr/bin/env python3
"""
Run the Trade Review AI Web Application.

This script starts the Flask web server for the trade review dashboard.
"""

import sys
from pathlib import Path

# Add the webapp directory to the path
webapp_dir = Path(__file__).parent / "webapp"
sys.path.insert(0, str(webapp_dir))

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("Trade Review AI - Web Dashboard")
    print("=" * 60)
    print("\nStarting server...")
    print("Open your browser at: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
