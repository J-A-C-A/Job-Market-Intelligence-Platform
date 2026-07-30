from fastapi import FastAPI
from app.api.job_offers import router as r1
from app.api.stats import router as r2
app = FastAPI()
app.include_router(r1)
app.include_router(r2)