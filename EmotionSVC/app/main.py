from app.SVC_model import SVC_predict
from pydantic import BaseModel
from fastapi import FastAPI

class InputText(BaseModel):
    text:str

app=FastAPI()

@app.post('/predict_svc')
async def prediction_svc(input_text:InputText):
    prediction=SVC_predict(input_text.text)
    return {'Predicted emotion': prediction}