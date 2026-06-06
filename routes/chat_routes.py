from flask import request, jsonify
from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId

from db import conversations_collection
from services.gemini_service import generate_gemini_reply


def register_chat_routes(app):

    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.json

        if not data or "message" not in data:
            return jsonify({"error": "Message is required"}), 400

        user_message = data["message"]
        conversation_id = data.get("conversation_id")

        #ai_reply = generate_gemini_reply(user_message)

        conversation_history = []
        final_conversation_id = None

        # If conversation_id exists, load previous messages from MongoDB
        if conversation_id:
            try:
                object_id = ObjectId(conversation_id)
            except InvalidId:
                return jsonify({"error": "Invalid conversation_id"}), 400

            conversation = conversations_collection.find_one({"_id": object_id})

            if not conversation:
                return jsonify({"error": "Conversation not found"}), 404

            all_previous_messages = conversation.get("messages", [])

            # Send only last 10 messages to Gemini to avoid sending huge history
            conversation_history = all_previous_messages[-10:]

            final_conversation_id = conversation_id

        # Send current message + previous history to Gemini
        ai_reply = generate_gemini_reply(
            user_message=user_message,
            conversation_history=conversation_history
        )

        now = datetime.now(timezone.utc)

        user_msg_obj = {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc)
        }

        assistant_msg_obj = {
            "role": "assistant",
            "content": ai_reply,
            "timestamp": datetime.now(timezone.utc)
        }

        if conversation_id:
            conversations_collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$push": {
                        "messages": {
                            "$each": [user_msg_obj, assistant_msg_obj]
                        }
                    },
                    "$set": {
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )

            final_conversation_id = conversation_id

        else:
            result = conversations_collection.insert_one({
                "title": user_message[:40],
                "messages": [user_msg_obj, assistant_msg_obj],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })

            final_conversation_id = str(result.inserted_id)

        return jsonify({
            "conversation_id": final_conversation_id,
            "reply": ai_reply
        }), 200