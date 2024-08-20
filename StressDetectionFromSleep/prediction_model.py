import pickle
import sklearn
import numpy as np

file_path = 'C:/Users/Dell/Desktop/programmin/StressDetectionIPD/StressDetectionFromSleep/SleepStress_SVC.pkl'

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


print(PredictStress([1,2,3,4,5,6,7,8]))