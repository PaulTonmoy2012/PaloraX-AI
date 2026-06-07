from flask import jsonify, session

from routes.auth_routes import login_required
from services.memory_service import get_user_memory


def register_memory_routes(app):

    @app.route("/api/memory", methods=["GET"])
    @login_required
    def get_memory():
        user_id = session["user_id"]
        memory = get_user_memory(user_id)

        return jsonify({
            "memory": memory
        }), 200
