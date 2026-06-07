from collections import Counter
from datetime import datetime

from db import conversations_collection


def get_user_conversations(user_id):
    """
    Get all conversations for one logged-in user.
    This keeps analytics user-specific.
    """

    conversations = list(conversations_collection.find({
        "user_id": user_id
    }))

    return conversations


def get_summary_analytics(user_id):
    """
    Count simple summary analytics for one user.
    """

    conversations = get_user_conversations(user_id)

    total_conversations = len(conversations)
    total_messages = 0
    user_messages = 0
    assistant_messages = 0

    for conversation in conversations:
        messages = conversation.get("messages", [])

        total_messages += len(messages)

        for message in messages:
            if message.get("role") == "user":
                user_messages += 1

            elif message.get("role") == "assistant":
                assistant_messages += 1

    if total_conversations > 0:
        average_messages = total_messages / total_conversations
    else:
        average_messages = 0

    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "average_messages_per_conversation": round(average_messages, 2)
    }


def get_top_keywords(user_id, limit=10):
    """
    Simple keyword counting from user messages.
    This is not advanced AI topic detection yet.
    It just counts repeated important words.
    """

    conversations = get_user_conversations(user_id)

    ignore_words = [
        "the", "and", "for", "you", "your", "are", "was", "were",
        "this", "that", "what", "when", "where", "which", "how",
        "why", "can", "could", "would", "should", "hello", "please",
        "thanks", "about", "with", "have", "has", "had", "tell",
        "me", "my", "name", "is", "to", "of", "in", "on", "a", "an",
        "it", "i", "am", "do", "does", "did", "be", "as", "at"
    ]

    words = []

    for conversation in conversations:
        messages = conversation.get("messages", [])

        for message in messages:
            if message.get("role") == "user":
                content = message.get("content", "").lower()

                content = content.replace(".", " ")
                content = content.replace(",", " ")
                content = content.replace("?", " ")
                content = content.replace("!", " ")
                content = content.replace(":", " ")
                content = content.replace(";", " ")

                split_words = content.split()

                for word in split_words:
                    if word not in ignore_words and len(word) > 2:
                        words.append(word)

    counter = Counter(words)

    top_keywords = []

    for word, count in counter.most_common(limit):
        top_keywords.append({
            "keyword": word,
            "count": count
        })

    return top_keywords


def get_daily_conversations(user_id):
    """
    Count how many conversations were created per day.
    """

    conversations = get_user_conversations(user_id)

    date_counter = {}

    for conversation in conversations:
        created_at = conversation.get("created_at")

        if not created_at:
            continue

        if isinstance(created_at, datetime):
            date_string = created_at.strftime("%Y-%m-%d")
        else:
            date_string = str(created_at)[:10]

        if date_string not in date_counter:
            date_counter[date_string] = 0

        date_counter[date_string] += 1

    daily_data = []

    for date, count in date_counter.items():
        daily_data.append({
            "date": date,
            "conversation_count": count
        })

    daily_data.sort(key=lambda item: item["date"])

    return daily_data


def get_dashboard_analytics(user_id):
    """
    Return all analytics together.
    This is useful for the React dashboard later.
    """

    return {
        "summary": get_summary_analytics(user_id),
        "top_keywords": get_top_keywords(user_id),
        "daily_conversations": get_daily_conversations(user_id)
    }