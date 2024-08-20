from LSTM_model import LSTM_predict
from Transformer_model import BERT_predict
from pydantic import BaseModel
from fastapi import FastAPI

class InputText(BaseModel):
    text:str

app=FastAPI()

@app.post('/predict_svc')
async def prediction_svc(text:InputText):
    prediction=LSTM_predict(text)
    return {'Predicted emotion': prediction}

@app.post('/predict_bert')
async def prediction_bert(text:InputText):
    prediction=BERT_predict(text)
    return {'Predicted emotion': prediction}
