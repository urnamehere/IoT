"""Main routes for the IoT Security Learning Tool."""

from datetime import datetime, timezone

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models import User, Progress
from app.content_loader import list_content

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Landing page with curriculum overview."""
    modules = list_content("modules")
    stats = None
    if current_user.is_authenticated:
        stats = get_user_stats(current_user.id)
    return render_template("index.html", modules=modules, stats=stats)


@main.route("/register", methods=["GET", "POST"])
def register():
    """User registration for progress tracking."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return render_template("register.html")

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created! Your progress will now be tracked.", "success")
        return redirect(url_for("main.index"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    """User login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Welcome back!", "success")
            return redirect(url_for("main.index"))

        flash("Invalid username or password.", "error")
        return render_template("login.html")

    return render_template("login.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))


@main.route("/progress")
@login_required
def progress_dashboard():
    """Show user's learning progress."""
    modules = list_content("modules")
    labs = list_content("labs")
    challenges = list_content("challenges")

    progress_records = Progress.query.filter_by(user_id=current_user.id).all()
    progress_map = {f"{p.item_type}:{p.item_id}": p for p in progress_records}

    return render_template(
        "progress.html",
        modules=modules,
        labs=labs,
        challenges=challenges,
        progress_map=progress_map,
    )


@main.route("/api/progress", methods=["POST"])
@login_required
def update_progress():
    """API endpoint to update progress on an item."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    item_type = data.get("item_type")
    item_id = data.get("item_id")
    status = data.get("status")

    if not all([item_type, item_id, status]):
        return jsonify({"error": "Missing required fields"}), 400

    if item_type not in ("module", "lab", "challenge"):
        return jsonify({"error": "Invalid item_type"}), 400

    if status not in ("not_started", "in_progress", "completed"):
        return jsonify({"error": "Invalid status"}), 400

    progress = Progress.query.filter_by(
        user_id=current_user.id, item_type=item_type, item_id=item_id
    ).first()

    if progress:
        progress.status = status
        if status == "completed":
            progress.completed_at = datetime.now(timezone.utc)
    else:
        progress = Progress(
            user_id=current_user.id,
            item_type=item_type,
            item_id=item_id,
            status=status,
            completed_at=datetime.now(timezone.utc) if status == "completed" else None,
        )
        db.session.add(progress)

    db.session.commit()
    return jsonify({"status": "ok", "item_type": item_type, "item_id": item_id, "new_status": status})


def get_user_stats(user_id):
    """Get summary statistics for a user's progress."""
    total_modules = len(list_content("modules"))
    total_labs = len(list_content("labs"))
    total_challenges = len(list_content("challenges"))

    completed = Progress.query.filter_by(user_id=user_id, status="completed").all()
    completed_modules = sum(1 for p in completed if p.item_type == "module")
    completed_labs = sum(1 for p in completed if p.item_type == "lab")
    completed_challenges = sum(1 for p in completed if p.item_type == "challenge")

    return {
        "modules": {"completed": completed_modules, "total": total_modules},
        "labs": {"completed": completed_labs, "total": total_labs},
        "challenges": {"completed": completed_challenges, "total": total_challenges},
    }
