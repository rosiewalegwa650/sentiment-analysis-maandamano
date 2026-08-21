import secrets
from flask import Blueprint, jsonify, request
from ..database import db
from ..models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username_or_email = (data.get("username") or data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not username_or_email or not password:
        return jsonify({"error": "Please provide username/email and password."}), 400

    user = User.query.filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username/email or password."}), 401

    if not user.token:
        user.token = secrets.token_hex(20)
        db.session.commit()

    return jsonify({
        "message": "Login successful",
        "token": user.token,
        "user": user.to_dict()
    })


@auth_bp.post("/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    role = (data.get("role") or "analyst").strip()

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username is already taken."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email is already registered."}), 400

    new_user = User(
        username=username,
        email=email,
        role=role,
        token=secrets.token_hex(20)
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "token": new_user.token,
        "user": new_user.to_dict()
    }), 201


@auth_bp.get("/auth/me")
def get_me():
    auth_header = request.headers.get("Authorization", "")
    token = request.headers.get("X-Auth-Token")

    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if not token:
        return jsonify({"error": "Authentication token missing."}), 401

    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired session token."}), 401

    return jsonify({"user": user.to_dict()})


@auth_bp.post("/auth/logout")
def logout():
    auth_header = request.headers.get("Authorization", "")
    token = request.headers.get("X-Auth-Token")

    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if token:
        user = User.query.filter_by(token=token).first()
        if user:
            user.token = None
            db.session.commit()

    return jsonify({"message": "Successfully logged out."})
