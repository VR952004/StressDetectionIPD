import pickle
import sklearn
import numpy as np

file_path = 'app/SleepStress_SVC.pkl'

with open(file_path, 'rb') as file:
    stress_pred=pickle.load(file)

stress_level_mapping = {
    0: 'low/normal',
    1: 'medium low',
    2: 'medium',
    3: 'medium high',
    4: 'high'
}

def PredictStress(a):
    a=np.array(a).reshape(1, -1)
    pred=stress_pred.predict(a)[0]
    pred=int(pred)
    stress_label = stress_level_mapping[pred]
    return stress_label