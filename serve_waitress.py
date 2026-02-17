"""Serve the Flask `app` with Waitress WSGI server.

Usage:
    python serve_waitress.py

This imports the `app` object from `app.py` (module-level variable `app`).
"""

from waitress import serve
import app

if __name__ == '__main__':
    # Bind to all interfaces on port 5000
    serve(app.app, host='0.0.0.0', port=5000)
