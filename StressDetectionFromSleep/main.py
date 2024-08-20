from prediction_model import PredictStress
from pydantic import BaseModel
from fastapi import FastAPI

class SleepParams(BaseModel):
    snoring_range: float
    respiration_rate: float
    body_temp: float
    limb_movement: float
    blood_o2: float
    eye_movement: float
    sleep_hrs: float
    heart_rate: float

app = FastAPI()

@app.post('/predict')
async def adding_data_to_model(sleep_data: SleepParams):
    sleep_features = [[
            sleep_data.snoring_range,
            sleep_data.respiration_rate,
            sleep_data.body_temp,
            sleep_data.limb_movement,
            sleep_data.blood_o2,
            sleep_data.eye_movement,
            sleep_data.sleep_hrs,
            sleep_data.heart_rate
        ]]
    pred_output = PredictStress(sleep_features)
    # The item fuction is used to convert the pred_output which was initially a numpy scalar to a Python scalar,
    # this made is possible to be used in the json
    return {'Predicted stress': pred_output.item()}
