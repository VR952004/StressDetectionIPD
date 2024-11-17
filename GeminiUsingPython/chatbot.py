import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Configure the SDK with the API key
genai.configure(api_key=API_KEY)

def start_chat():
    """
    Start the interactive chat using the Gemini API and initiate conversation by the bot.
    """
    try:
        # Create the model instance
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Start chat without predefined history
        chat = model.start_chat(history=[])

        return chat

    except Exception as e:
        return None, str(e)


def get_bot_response(chat, user_input):
    """
    Send the user input to the chatbot and get the response.
    """
    try:
        # Set generation configuration
        config = genai.types.GenerationConfig(
            max_output_tokens=1000,  # Limit the number of tokens in the output to keep responses short
            temperature=1  # Balance between randomness and determinism
        )

        # Send the user message to the chat API with custom configuration
        response = chat.send_message(user_input, generation_config=config)

        return response.text

    except Exception as e:
        return f"Error: {e}"