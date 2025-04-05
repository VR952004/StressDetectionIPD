import joblib
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

app = FastAPI()
model = joblib.load("stress_regressor.pkl")
transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class TextItem(BaseModel):
    text: str

@app.post("/predict_stress")
def predict_stress(item: TextItem):
    # 1) Convert text to embedding
    emb = transformer.encode([item.text], convert_to_tensor=False)[0]
    # 2) Regressor predicts numeric stress
    stress_val = model.predict([emb])[0]
    return {"stress_score": float(stress_val)}
