import pickle
from sklearn.pipeline import Pipeline

file_path = 'app/EmotionNLP_SVC.pkl'

with open(file_path, 'rb') as file:
    pipeline=pickle.load(file)

def SVC_predict(a):
    text=[a]
    pred=pipeline.predict(text)

    if pred==0:
        return 'anger'
    elif pred==1:
        return 'fear'
    elif pred==2:
        return 'joy'
    elif pred==3:
        return 'love'
    elif pred==4:
        return 'sadness'
    elif pred==5:
        return 'surprise'