import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure the SDK with the API key
genai.configure(api_key=API_KEY)

def start_chat():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(history=[])
        return chat
    except Exception as e:
        print(f"Error initializing chat: {e}")  # Log error
        return None


def get_bot_response(chat, user_input):
    try:
        config = genai.types.GenerationConfig(
            max_output_tokens=1000,
            temperature=1
        )
        response = chat.send_message(user_input, generation_config=config)
        return response.text
    except Exception as e:
        print(f"Error getting bot response: {e}")  # Log error
        return f"Error: {e}"