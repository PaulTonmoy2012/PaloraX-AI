from flask import jsonify, session
from bson import ObjectId
from bson.errors import InvalidId

from db import conversations_collection
from routes.auth_routes import login_required


def serialize_conversation_summary(conversation):
    return {
        "id": str(conversation["_id"]),
        "title": conversation.get("title", "Untitled conversation"),
        "created_at": conversation.get("created_at"),
        "updated_at": conversation.get("updated_at")
    }


def serialize_message(message):
    return {
        "role": message.get("role"),
        "content": message.get("content"),
        "timestamp": message.get("timestamp")
    }


def register_conversation_routes(app):

    @app.route("/api/conversations", methods=["GET"])
    @login_required
    def get_conversations():
        user_id = session["user_id"]

        conversations = conversations_collection.find(
            {"user_id": user_id},
            {"messages": 0}
        ).sort("updated_at", -1)

        return jsonify({
            "conversations": [
                serialize_conversation_summary(conversation)
                for conversation in conversations
            ]
        }), 200


    @app.route("/api/conversations/<conversation_id>", methods=["GET"])
    @login_required
    def get_conversation(conversation_id):
        user_id = session["user_id"]

        try:
            object_id = ObjectId(conversation_id)
        except InvalidId:
            return jsonify({"error": "Invalid conversation_id"}), 400

        conversation = conversations_collection.find_one({
            "_id": object_id,
            "user_id": user_id
        })

        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404

        return jsonify({
            "conversation": {
                "id": str(conversation["_id"]),
                "title": conversation.get("title", "Untitled conversation"),
                "messages": [
                    serialize_message(message)
                    for message in conversation.get("messages", [])
                ]
            }
        }), 200