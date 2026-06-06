import json
from datetime import datetime, timezone

from google import genai

from config import GEMINI_API_KEY
from db import user_memories_collection

client = genai.Client(api_key=GEMINI_API_KEY)


def get_user_memory(user_id):
    memory = user_memories_collection.find_one({"user_id": user_id})

    if not memory:
        return {}

    return memory.get("facts", {})


def save_user_facts(user_id, facts):
    if not facts:
        return

    update_fields = {}

    for key, value in facts.items():
        update_fields[f"facts.{key}"] = value

    update_fields["updated_at"] = datetime.now(timezone.utc)

    user_memories_collection.update_one(
        {"user_id": user_id},
        {
            "$set": update_fields,
            "$setOnInsert": {
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )


def extract_memory_facts(user_message):
    prompt = f"""
You are a memory extraction system.

Your job is to extract important long-term user facts from the user's message.

Only extract facts that are useful across future conversations.

Good examples:
- user's name
- user's project
- user's role or profession
- user's goals
- user's preferences
- user's tech stack
- user's learning level
- important personal context


Return only valid JSON.
Do not include markdown.
Do not include explanation.

If there are no important memory facts, return:
{{}}

User message:
{user_message}
"""
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    try:
        facts = json.loads(response.text)
    except json.JSONDecodeError:
        return {}

    if not isinstance(facts, dict):
        return {}

    return facts


def update_memory_from_message(user_id, user_message):
    facts = extract_memory_facts(user_message)
    save_user_facts(user_id, facts)