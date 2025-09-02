#!/usr/bin/env python3
"""
SciTrace - Research Data Management Platform

Main application entry point.
"""

import os
from scitrace import create_app

app = create_app()

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5001))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
