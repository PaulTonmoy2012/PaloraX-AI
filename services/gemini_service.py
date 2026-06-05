import os
#from dotenv import load_dotenv
from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

def generate_gemini_reply(message):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=message
    )
    return response.text