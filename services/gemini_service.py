import os
#from dotenv import load_dotenv
from google import genai
from config import GEMINI_API_KEY

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing from .env file")
client = genai.Client(api_key=GEMINI_API_KEY)


def build_prompt(user_message, conversation_history=None):
    """
    Builds a prompt that includes previous conversation context.
    conversation_history should be a list of MongoDB message objects:
    [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
    """

    system_instruction = """
You are PaloraX AI, a helpful AI assistant.
Answer clearly and politely.
Use the previous conversation context when it is provided.
If the answer is not available from the conversation, say that you do not know yet.
"""

    prompt = system_instruction.strip() + "\n\n"

    if conversation_history:
        prompt += "Previous conversation:\n"

        for msg in conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "assistant":
                prompt += f"Assistant: {content}\n"
            else:
                prompt += f"User: {content}\n"

        prompt += "\n"

    prompt += f"Current user message:\nUser: {user_message}\n\nAssistant:"

    return prompt


def generate_gemini_reply(user_message, conversation_history=None):
    prompt=build_prompt(user_message, conversation_history)
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents= prompt
    )
    return response.text