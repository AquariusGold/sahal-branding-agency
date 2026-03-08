# =============================================================================
# run.py  —  Application Entry Point
# =============================================================================
# WHY THIS FILE EXISTS:
#   This is the single file you execute to start the development server:
#       python run.py
#
#   It calls create_app() to build a configured Flask instance, then starts
#   the built-in Werkzeug development server.
#
# PRODUCTION NOTE:
#   In production, do NOT use `python run.py`. Instead, serve the app with a
#   production WSGI server (Gunicorn, uWSGI) behind a reverse proxy (Nginx):
#       gunicorn -w 4 "run:app"
#   The `app` object created here is the WSGI callable.
# =============================================================================

from app import create_app

# Create the application instance using the factory.
# FLASK_ENV (.env) defaults to "development" if not set.
app = create_app()

if __name__ == "__main__":
    # debug=True enables:
    #   - Interactive Werkzeug debugger in the browser on errors.
    #   - Auto-reloader: server restarts when source files change.
    # host="0.0.0.0" makes the dev server reachable from other devices on
    # the local network (useful for testing mobile browsers on the same WiFi).
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
