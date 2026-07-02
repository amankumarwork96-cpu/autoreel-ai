from flask import Flask
from config import Config, validate_config
from database.db import init_db

# ─────────────────────────────────────────────
#  Import blueprints
#  Each blueprint is a group of related routes
# ─────────────────────────────────────────────
from routes.auth import auth_bp
from routes.reels import reels_bp
from routes.dashboard import dashboard_bp


def create_app():
    """
    Application factory function.
    Creates and configures the Flask app.
 
    WHY A FACTORY FUNCTION?
    Instead of creating the app at module level (app = Flask(__name__)),
    wrapping it in a function lets you create multiple instances —
    useful for testing (create a test app with test config) without
    affecting the real app. Industry standard pattern.
    """
    app =Flask(__name__)

    # ── Load config ────────────────────────────────────────────────
    # SECRET_KEY is required for sessions to work
    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["DEBUG"] = Config.DEBUG

    # ── Register blueprints ────────────────────────────────────────
    # This "plugs in" all the routes defined in each file.
    # url_prefix adds a prefix to every route in that blueprint.
    # auth_bp has no prefix → /login, /signup, /logout
    # reels_bp has no prefix → /create, /status/<id>, /gallery
    # dashboard_bp has no prefix → /, /dashboard
    app.register_blueprint(auth_bp)
    app.register_blueprint(reels_bp)
    app.register_blueprint(dashboard_bp)

    return app


# ─────────────────────────────────────────────
#  STARTUP SEQUENCE
# ─────────────────────────────────────────────
if __name__ == "__main__":

    # Step 1: Validate all required env vars are present
    # Crashes early with a clear message if anything is missing
    validate_config()

    # Step 2: Initialize database tables
    # Safe to call every time — IF NOT EXISTS means no data is lost
    init_db()

    # Step 3: Create and run the app
    app = create_app()

    print("\n─────────────────────────────────────")
    print("  AutoReel AI is running!")
    print("  Open: http://localhost:5000")
    print("─────────────────────────────────────\n")
 
    # debug=True: auto-reloads when you save a file — no manual restart needed
    # use_reloader=False: prevents the worker threads from doubling up in debug mode
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=Config.DEBUG,
        use_reloader=False
    )