import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from detector.model import PhishDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Phish Detector API",
    description="API для детекции фишинговых URL",
    version="1.0.0"
)

detector = PhishDetector()

class URLItem(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Detector is running"}

@app.post("/predict")
async def predict_url(item: URLItem):
    try:
        result = detector.predict(item.url)
        logger.info(f"Prediction for {item.url}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error predicting {item.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": True}
