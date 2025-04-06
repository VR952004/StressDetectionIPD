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

# Existing Docker/ML Model settings (unchanged)
ML_MODEL_DOCKER_IMAGE = os.getenv("ML_MODEL_DOCKER_IMAGE", "veer954/sentiment_svc")
ML_MODEL_HOST_PORT = int(os.getenv("ML_MODEL_HOST_PORT", "8000"))
ML_MODEL_API_URL = f"http://localhost:{ML_MODEL_HOST_PORT}/predict_svc"

# New stress prediction settings (added)
STRESS_MODEL_IMAGE = os.getenv("STRESS_MODEL_IMAGE", "veer954/stress_predictor")
STRESS_MODEL_PORT = int(os.getenv("STRESS_MODEL_PORT", "8002"))
STRESS_MODEL_API_URL = f"http://localhost:{STRESS_MODEL_PORT}/predict_stress"

# Initialize Docker client (existing)
docker_client = docker.from_env()

# Existing wait function (unchanged)
def wait_for_ml_model(url, timeout=30):
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

# New wait function for stress model (added)
def wait_for_stress_model(url, timeout=30):
    start_time = time.time()
    test_payload = {"text": "health check"}
    while time.time() - start_time < timeout:
        try:
            r = requests.post(url, json=test_payload)
            if r.status_code == 200:
                print("Stress model API is ready.")
                return True
        except Exception as e:
            print("Waiting for stress model API to be ready...", e)
        time.sleep(1)
    return False

# Existing container starter (unchanged)
def start_ml_model_container():
    try:
        print(f"Pulling ML model image: {ML_MODEL_DOCKER_IMAGE}")
        docker_client.images.pull(ML_MODEL_DOCKER_IMAGE)
        print("Image pulled successfully.")

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

# New stress model container starter (added)
def start_stress_model_container():
    try:
        print(f"\nPulling stress model image: {STRESS_MODEL_IMAGE}")
        docker_client.images.pull(STRESS_MODEL_IMAGE)
        print("Stress model image pulled successfully.")

        containers = docker_client.containers.list(filters={"ancestor": STRESS_MODEL_IMAGE})
        if containers:
            print(f"Stress model container already running. Container ID: {containers[0].id}")
        else:
            print("No running stress container found. Starting a new one...")
            container = docker_client.containers.run(
                STRESS_MODEL_IMAGE,
                detach=True,
                ports={"8002/tcp": STRESS_MODEL_PORT}
            )
            print(f"Started stress model container with ID: {container.id}")
            if not wait_for_stress_model(STRESS_MODEL_API_URL):
                print("Warning: Stress model API did not become ready in time.")
    except Exception as e:
        print(f"Error starting stress model container: {e}")
        raise

# Start both containers (modified)
def start_containers():
    start_ml_model_container()  # Existing
    start_stress_model_container()  # Added

# Update startup call (modified)
start_containers()

# Existing FastAPI setup (unchanged)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.options("/process_message")
async def process_message_options():
    return {}

class InputMessage(BaseModel):
    text: str

# Modified endpoint with stress prediction
@app.post("/process_message")
async def process_message(input_data: InputMessage):
    user_text = input_data.text

    # Existing emotion prediction (unchanged)
    try:
        ml_response = requests.post(ML_MODEL_API_URL, json={"text": user_text})
        ml_response.raise_for_status()
        ml_data = ml_response.json()
        predicted_emotion = ml_data.get("Predicted emotion", "unknown")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling ML model API: {e}")

    # New stress prediction with logging and validation
    stress_level = 0  # Default value
    try:
        stress_response = requests.post(STRESS_MODEL_API_URL, json={"text": user_text})
        stress_response.raise_for_status()
        stress_data = stress_response.json()
        print("Raw stress_data response:", stress_data)  # Keep this for debugging
        stress_score = stress_data.get("stress_score")  # Use the correct key
        if stress_score is None:
            print("Warning: stress_score not found in stress_data, using default 0")
            stress_level = 0
        else:
            stress_level = stress_score  # Assign the score to stress_level
    except Exception as e:
        print(f"Error calling stress model API: {e}, using default stress_level 0")
        stress_level = 0

    # Modified prompt with stress level
    prompt = (
        f"User said: '{user_text}'. "
        f"Detected emotion: '{predicted_emotion}'. "
        f"Stress level: {stress_level}/5. "
        "Please provide an empathetic, stress-management-focused response.In case you observe a mismatch between the emotion predicted, please dont mention that in the response."
    )

    # Existing Gemini call
    try:
        chat_session = start_chat()
        if chat_session is None:
            raise Exception("Failed to initialize Gemini chat session.")
        bot_response = get_bot_response(chat_session, prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling Gemini API: {e}")

    # Modified return with stress level
    return {
        "bot_response": bot_response,
        "predicted_emotion": predicted_emotion,
        "stress_level": stress_level
    }