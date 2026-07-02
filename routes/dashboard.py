from flask import Blueprint, render_template, session, redirect, url_for
from functools import wraps
from models.project import get_user_projects
from models.user import get_user_by_id

dashboard_bp = Blueprint("dashboard", __name__)


def login_required(f):
    """
    Same decorator pattern as routes/reels.py.
    Each route file defines its own copy to keep files independent —
    avoids circular imports between route files.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


@dashboard_bp.route("/")
def index():
    """
    The public landing page — shown to everyone, logged in or not.
    If already logged in, send them straight to the dashboard instead.
    """
    if "user_id" in session:
        return redirect(url_for("dashboard.home"))
    
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
@login_required
def home():
    """
    The main dashboard — shows the user's reel history.
 
    Each project shows its current status:
      queued, generating_script, generating_images,
      generating_audio, rendering_video, done, failed
 
    Clicking an in-progress project takes them to its status page.
    Clicking a done project takes them to view/download the reel.
    """
    user_id = session["user_id"]

    user = get_user_by_id(user_id)
    projects = get_user_projects(user_id)

    # Quick stats for the dashboard header
    total_count = len(projects)
    done_count = len([p for p in projects if p["status"] == "done"])
    in_progres_count = len([
        p for p in projects
        if p["status"] not in ("done", "failed")
    ])

    return render_template(
        "dashboard.html",
        user=user,
        projects=projects,
        total_count=total_count,
        done_count=done_count,
        in_progres_count=in_progres_count,
    )