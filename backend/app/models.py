from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()

class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    keycloak_id = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=dt.datetime.now(dt.timezone.utc))

    roles = db.relationship("Role", secondary="user_roles", backref="users")

class UserRoles(db.Model):
    __tablename__ = "user_roles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), primary_key=True)
