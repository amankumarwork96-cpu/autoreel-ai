from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.user import create_user, get_user_by_email, verify_password

# ─────────────────────────────────────────────
#  WHAT IS A BLUEPRINT?
#  ─────────────────────────────────────────────
#  Flask Blueprints let you split routes across multiple files.
#  Instead of cramming every @app.route() into one giant app.py,
#  each feature area (auth, reels, dashboard) gets its own file.
#
#  app.py later does: app.register_blueprint(auth_bp)
#  This "plugs in" all the routes defined here.
# ─────────────────────────────────────────────

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """
    GET  → show the signup form
    POST → process the form submission, create the user
    """

    if request.method == "POST":
        # request.form is a dict-like object containing form field values
        # The keys here ("email", "username", "password") must match
        # the "name" attribute on the HTML <input> tags
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        # ── Basic validation ──────────────────────────────────────
        if not email or not username or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.signup"))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("auth.signup"))
        
        # ── Check if email already exists ─────────────────────────
        existing = get_user_by_email(email)
        if existing:
            flash("An account with that email already exists.", "error")
            return redirect(url_for("auth.signup"))
        
        # ── Create the user ────────────────────────────────────────
        user_id = create_user(email, username, password)

        if user_id is None:
            # Could fail if username is taken (separate UNIQUE constraint)
            flash("Could not create account. Username may be taken.", "error")
            return redirect(url_for("auth.signup"))
 
        # ── Log them in immediately after signup ──────────────────
        # session is Flask's signed cookie storage.
        # We only ever store the user_id — never the password.
        session["user_id"] = user_id
        session["username"] = username

        flash("Account created: Welcome abroad.", "success")
        return redirect(url_for("dashboard.home"))
    
    # GET request — just show the form
    return render_template("signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET  → show the login form
    POST → verify credentials, start a session
    """

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email an password are required.", "error")
            return redirect(url_for("auth.login"))
        
        # ── Fetch the user ─────────────────────────────────────────
        user = get_user_by_email(email)

        if user is None:
            # Don't say "email not found" — that tells attackers
            # which emails are registered. Generic message is safer.
            flash("Inavlid email or password.", "error")
            return redirect(url_for("auth.login"))
        
        # ── Verify the password ────────────────────────────────────
        if not verify_password(password, user["password_hash"]):
            flash("Inavlid email or passwrod." "error")
            return redirect(url_for("auth.login"))
 
        # ── Success — start the session ────────────────────────────
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        flash(f"Welcome bavk, {user['username']}|", "success")
        return redirect(url_for("dashboard.home"))
    
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """
    Clears the session — logs the user out.
    session.clear() removes everything: user_id, username, etc.
    """
    session.clear()
    flash("You've been logged out.", "success")
    return redirect(url_for("auth.login"))