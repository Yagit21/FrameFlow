from datetime import datetime, timezone
from . import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc)
    )

    projects = db.relationship(
        "Project",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Character(db.Model):
    __tablename__ = "characters"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    blend_file = db.Column(
        db.String(255),
        nullable=False
    )

    preview_image = db.Column(
        db.String(255)
    )

    description = db.Column(
        db.Text
    )

    projects = db.relationship(
        "Project",
        backref="character",
        lazy=True
    )


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    character_id = db.Column(
        db.Integer,
        db.ForeignKey("characters.id"),
        nullable=False
    )

    project_name = db.Column(
        db.String(100),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Recording"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc)
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )

    recordings = db.relationship(
        "Recording",
        backref="project",
        cascade="all, delete-orphan"
    )

    pose_files = db.relationship(
        "PoseFile",
        backref="project",
        cascade="all, delete-orphan"
    )

    camera_files = db.relationship(
        "CameraFile",
        backref="project",
        cascade="all, delete-orphan"
    )

    animations = db.relationship(
        "Animation",
        backref="project",
        cascade="all, delete-orphan"
    )

    settings = db.relationship(
        "Settings",
        backref="project",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
class Recording(db.Model):
    __tablename__ = "recordings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    recording_uuid = db.Column(
        db.String(36),
        unique=True,
        nullable=False
    )

    video_path = db.Column(
        db.String(255),
        nullable=False
    )

    fps = db.Column(db.Integer)

    resolution = db.Column(db.String(30))

    duration = db.Column(db.Float)

    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc)
    )


class PoseFile(db.Model):
    __tablename__ = "pose_files"

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    json_path = db.Column(
        db.String(255),
        nullable=False
    )

    frame_count = db.Column(db.Integer)

    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc)
    )


class CameraFile(db.Model):
    __tablename__ = "camera_files"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    json_path = db.Column(
        db.String(255),
        nullable=False
    )

    algorithm = db.Column(
        db.String(100)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc)
    )


class Animation(db.Model):
    __tablename__ = "animations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False
    )

    animation_path = db.Column(
        db.String(255),
        nullable=False
    )

    thumbnail_path = db.Column(
        db.String(255)
    )

    duration = db.Column(db.Float)

    render_time = db.Column(db.Float)

    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc)
    )
    
class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id"),
        nullable=False,
        unique=True
    )

    tracking_mode = db.Column(
        db.String(50),
        default="Full Body"
    )

    pose_smoothing = db.Column(
        db.Boolean,
        default=True
    )

    camera_smoothing = db.Column(
        db.Boolean,
        default=True
    )

    mirror_camera = db.Column(
        db.Boolean,
        default=True
    )

    output_fps = db.Column(
        db.Integer,
        default=30
    )

    render_resolution = db.Column(
        db.String(20),
        default="1280x720"
    )
