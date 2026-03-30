"""Database models for progress tracking and user management."""

from datetime import datetime, timezone

from flask_login import UserMixin

from app import db, login_manager


class User(UserMixin, db.Model):
    """Local user for progress tracking."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    progress = db.relationship("Progress", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Progress(db.Model):
    """Track user progress through modules, labs, and challenges."""

    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # module, lab, challenge
    item_id = db.Column(db.String(100), nullable=False)  # e.g. "module-01", "lab-firmware-101"
    status = db.Column(db.String(20), default="not_started")  # not_started, in_progress, completed
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "item_type", "item_id", name="unique_user_progress"),
    )

    def __repr__(self):
        return f"<Progress {self.item_type}:{self.item_id} - {self.status}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
