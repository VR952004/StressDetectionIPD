import os
import time
import requests
import docker
import google.generativeai as genai

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import your Gemini chatbot functions
from chatbot import start_chat, get_bot_response

# Load environment variables
load_dotenv()

# Configure the Gemini API key
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)

# Docker/ML Model settings
ML_MODEL_DOCKER_IMAGE = os.getenv("ML_MODEL_DOCKER_IMAGE", "veer954/emotion_svc:latest")
ML_MODEL_HOST_PORT = int(os.getenv("ML_MODEL_HOST_PORT", "8000"))
ML_MODEL_API_URL = f"http://localhost:{ML_MODEL_HOST_PORT}/predict_svc"

# Initialize Docker client
docker_client = docker.from_env()

def wait_for_ml_model(url, timeout=30):
    """
    Polls the given URL using a POST request until a successful (HTTP 200) response is received or timeout is reached.
    (Using a POST because /predict_svc only supports POST.)
    """
    start_time = time.time()
    test_payload = {"text": "health check"}
    while time.time() - start_time < timeout:
        try:
            r = requests.post(url, json=test_payload)
            if r.status_code == 200:
                print("ML model API is ready.")
                return True
        except Exception as e:
            print("Waiting for ML model API to be ready...", e)
        time.sleep(1)
    return False

def start_ml_model_container():
    """
    Pulls the ML model Docker image, checks for a running container,
    starts one if necessary, and waits for the ML model API to be ready.
    """
    try:
        print(f"Pulling ML model image: {ML_MODEL_DOCKER_IMAGE}")
        docker_client.images.pull(ML_MODEL_DOCKER_IMAGE)
        print("Image pulled successfully.")

        # Check if a container for this image is already running
        containers = docker_client.containers.list(filters={"ancestor": ML_MODEL_DOCKER_IMAGE})
        if containers:
            print(f"ML model container already running. Container ID: {containers[0].id}")
        else:
            print("No running container found. Starting a new one...")
            container = docker_client.containers.run(
                ML_MODEL_DOCKER_IMAGE,
                detach=True,
                ports={"8000/tcp": ML_MODEL_HOST_PORT}
            )
            print(f"Started ML model container with ID: {container.id}")
            if not wait_for_ml_model(ML_MODEL_API_URL):
                print("Warning: ML model API did not become ready in time.")
    except Exception as e:
        print(f"Error starting ML model container: {e}")
        raise

# Start the ML model container on startup
start_ml_model_container()

# Create FastAPI app
app = FastAPI()

# Add CORS middleware – note this must be added before any route definitions.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can change "*" to a list of specific origins (e.g., your frontend URL)
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Explicitly define an OPTIONS endpoint (in case middleware doesn't catch it)
@app.options("/process_message")
async def process_message_options():
    return {}

# Define the input model
class InputMessage(BaseModel):
    text: str

@app.post("/process_message")
async def process_message(input_data: InputMessage):
    user_text = input_data.text

    # Call the ML model API
    try:
        ml_response = requests.post(ML_MODEL_API_URL, json={"text": user_text})
        ml_response.raise_for_status()
        ml_data = ml_response.json()
        predicted_emotion = ml_data.get("Predicted emotion", "unknown")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling ML model API: {e}")

    # Create prompt for Gemini API
    prompt = (
        f"User said: '{user_text}'. Detected emotion: '{predicted_emotion}'. "
        "Please provide an empathetic, stress-management-focused response."
    )

    # Call Gemini API
    try:
        chat_session = start_chat()
        if chat_session is None:
            raise Exception("Failed to initialize Gemini chat session.")
        bot_response = get_bot_response(chat_session, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")

    return {
        "bot_response": bot_response,
        "predicted_emotion": predicted_emotion
    }