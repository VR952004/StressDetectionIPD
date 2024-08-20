import warnings
import os
from huggingface_hub import login
from transformers import pipeline

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['F_ENABLE_ONEDNN_OPTS'] = '0'
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


emotion=pipeline("text-classification", model="michellejieli/emotion_text_classifier")

def BERT_predict(a):
    return emotion(a)[0]['label']

print(BERT_predict("I don't feel like going to college today."))