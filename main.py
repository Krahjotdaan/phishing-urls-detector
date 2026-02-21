import os
import logging
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from detector.model import PhishDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phishing URLs Detector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates_path = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=templates_path)

static_path = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

try:
    detector = PhishDetector()
    logger.info("Model was loaded")
except Exception as e:
    logger.error(f"Error in model loading: {e}")
    detector = None

class URLItem(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_url(item: URLItem):
    if not detector:
        raise HTTPException(status_code=503, detail="Model was not loaded")
    
    try:
        result = detector.predict(item.url)
        logger.info(f"Prediction for {item.url}: {result}")
        return result
    except Exception as e:
        logger.error(f"Error predicting {item.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    status = "healthy" if detector else "unhealthy"
    return {"status": status, "model_loaded": bool(detector)}