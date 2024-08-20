import os
import tensorflow as tf
import logging
import warnings
from tensorflow import keras
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences

#Warnings handling
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
tf.get_logger().setLevel(logging.ERROR)
warnings.filterwarnings('ignore')

model=keras.models.load_model('C:/Users/Dell/Desktop/programmin/StressDetectionIPD/Emotions_using_NLP/EmotionNLP_LSTM.h5')
tokenizer_path='C:/Users/Dell/Desktop/programmin/StressDetectionIPD/Emotions_using_NLP/tokenizer.json'

with open(tokenizer_path, 'r') as file:
    tokenizer_json = file.read()

tokenizer = tokenizer_from_json(tokenizer_json)

def LSTM_predict(text):
    sequences = tokenizer.texts_to_sequences([text])
    padded_sequences = pad_sequences(sequences, maxlen=50, padding='post')
    pred= model.predict(padded_sequences)

    pred_class = tf.argmax(pred, axis=1).numpy()[0]

    emotion_labels = ['anger', 'fear', 'joy', 'love', 'sadness', 'surprise']
    return emotion_labels[pred_class]

print(LSTM_predict('Today is a bright sunny morning. I feel like going for a walk. ' ))