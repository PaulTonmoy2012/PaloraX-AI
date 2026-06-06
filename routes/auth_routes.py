from functools import wraps
from datetime import datetime, timezone

from bson import ObjectId
from flask import request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from db import users_collection

def get_current_user_id():
    return session.get("user_id")


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please login first"}), 401

        return route_function(*args, **kwargs)

    return wrapper

def register_auth_routes(app):
    @app.route("/api/auth/register", methods=["POST"])
    def register():
        data = request.json

        if not data:
            return jsonify({"error": "Request body is required"}), 400
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({"error": "Name, email, and password are required"}), 400
        
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409

        password_hash = generate_password_hash(password,method="pbkdf2:sha256:1000000")

        result = users_collection.insert_one({
            "name": name,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now(timezone.utc)
        })

        return jsonify({
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }), 201


    @app.route("/api/auth/login", methods=["POST"])
    def login():
        data = request.json

        if not data:
            return jsonify({"error": "Request body is required"}), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = users_collection.find_one({"email": email})

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        if not check_password_hash(user["password_hash"], password):
            return jsonify({"error": "Invalid email or password"}), 401

        session["user_id"] = str(user["_id"])

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"]
            }
        }), 200


    @app.route("/api/auth/logout", methods=["POST"])
    def logout():
        session.clear()
        return jsonify({"message": "Logout successful"}), 200


    @app.route("/api/auth/me", methods=["GET"])
    @login_required
    def me():
        user_id = session["user_id"]

        user = users_collection.find_one({"_id": ObjectId(user_id)})

        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"]
            }
        }), 200