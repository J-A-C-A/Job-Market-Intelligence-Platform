from fastapi import FastAPI
from app.api.job_offers import router

app = FastAPI()
app.include_router(router)