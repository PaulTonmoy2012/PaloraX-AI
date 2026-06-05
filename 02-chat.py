import logging
import os

from dotenv import load_dotenv
from google import genai

logging.getLogger("google.genai").setLevel(logging.ERROR)

def main():
    load_dotenv()

    client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))
    chat = client.chats.create(model="gemini-3.5-flash")

    print("Hi Tonmoy, How can I help you today? ")

    while True:
        message = input("> ").strip()
        if message.lower() == "exit":
            break


        res = chat.send_message_stream(message)
        for stream in res:
            print(stream.text, end="", flush=True)


if __name__ == "__main__":
    main()
