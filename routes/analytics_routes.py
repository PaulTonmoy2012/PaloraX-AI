from flask import jsonify, request, session

from routes.auth_routes import login_required

from services.analytics_service import (
    get_summary_analytics,
    get_top_keywords,
    get_daily_conversations,
    get_dashboard_analytics
)


def register_analytics_routes(app):

    @app.route("/api/analytics/summary", methods=["GET"])
    @login_required
    def analytics_summary():
        user_id = session["user_id"]

        data = get_summary_analytics(user_id)

        return jsonify(data), 200


    @app.route("/api/analytics/top-keywords", methods=["GET"])
    @login_required
    def analytics_top_keywords():
        user_id = session["user_id"]

        limit = request.args.get("limit", 10)
        limit = int(limit)

        data = get_top_keywords(user_id, limit)

        return jsonify(data), 200


    @app.route("/api/analytics/daily-conversations", methods=["GET"])
    @login_required
    def analytics_daily_conversations():
        user_id = session["user_id"]

        data = get_daily_conversations(user_id)

        return jsonify(data), 200


    @app.route("/api/analytics/dashboard", methods=["GET"])
    @login_required
    def analytics_dashboard():
        user_id = session["user_id"]

        data = get_dashboard_analytics(user_id)

        return jsonify(data), 200