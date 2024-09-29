from app.LSTM_model import LSTM_predict
from pydantic import BaseModel
from fastapi import FastAPI

class InputText(BaseModel):
    text:str

app=FastAPI()

@app.post('/predict_lstm')
async def prediction_svc(text:InputText):
    prediction=LSTM_predict(text.text)
    return {'Predicted emotion': prediction}
