from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from functools import wraps
from models.project import create_project, get_project, get_user_projects
from workers.generate_worker import start_generation

reels_bp = Blueprint("reels", __name__)


# ─────────────────────────────────────────────
#  LOGIN REQUIRED DECORATOR
#  ─────────────────────────────────────────────
#  This wraps a route function so it checks if the user is
#  logged in BEFORE running the actual route code.
#
#  Usage:
#    @reels_bp.route("/create")
#    @login_required
#    def create(): ...
#
#  If not logged in → redirect to login page
#  If logged in     → run the route normally
# ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorarted_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log into continue.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorarted_function


@reels_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """
    GET  → show the topic input form
    POST → create a project, start the worker, redirect to status page
    """

    if request.method == "POST":
        topic = request.form.get("topic", "").strip()

        if not topic:
            flash("Please enter a topic.", "error")
            return redirect(url_for("reels.create"))

        if len(topic) > 200:
            flash("Topic is too long. Keep it under 200 characters.", "error")
            return redirect(url_for("reels.create"))

        # ── Create the project record (status = 'queued') ─────────
        user_id = session["user_id"]
        project_id = create_project(user_id, topic)

        if project_id is None:
            flash("Something went wrong creating your project.", "error")
            return redirect(url_for("reels.create"))
        
        # ── Start the pipeline in a background thread ──────────────
        # This returns IMMEDIATELY — the actual generation happens
        # in the background while we redirect the user to the status page
        start_generation(project_id, topic)

        return redirect(url_for("reels.status", project_id=project_id))
    
    return render_template("create.html")


@reels_bp.route("/status/<project_id>")
@login_required
def status(project_id):
    """
    Shows the live status page.
    The page itself uses JavaScript to poll /status/<id>/json
    every few seconds and update the UI without a full refresh.
    """
    project = get_project(project_id)

    if project is None:
        flash("Project not found.", "error")
        return redirect(url_for("dashboard.home"))
    
    # Security check: make sure this project belongs to the logged-in user
    # Without this, any logged-in user could view ANY project by guessing IDs
    if project["user_id"] != session["user_id"]:
        flash("You don't have access to that project", "error")
        return redirect(url_for("dashboard.home"))
    
    return render_template("status.html", project=project)


@reels_bp.route("/status/<project_id>/json")
@login_required
def status_json(project_id):
    """
    Returns the project's current status as JSON.
    The status page's JavaScript calls this endpoint every 2-3 seconds
    to check progress without reloading the whole page.
 
    This is the core of the "real-time" status tracker —
    no WebSockets needed, just simple polling.
    """
    project = get_project(project_id)

    if project is None:
        return jsonify({"error": "Project not found"}), 404
    
    if project["user_id"] != session["user_id"]:
        return jsonify({"error": "Access denied"}), 403
    
    # jsonify converts a Python dict to a JSON HTTP response
    return jsonify({
        "status": project["status"],
        "error_msg": project["error_msg"],
        "video_path": project["video_path"],
    })


@reels_bp.route("/gallery")
@login_required
def gallery():
    """
    Shows all of the logged-in user's finished reels.
    """
    projects = get_user_projects(session["user_id"])

    # Only show completed projects in the gallery
    completed = [p for p in projects if p["status"] == "done"]
 
    return render_template("gallery.html", projects=completed)