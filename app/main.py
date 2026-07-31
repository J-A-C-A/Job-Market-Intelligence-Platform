from fastapi import FastAPI
from app.api.job_offers import router as r1
from app.api.stats import router as r2
from app.scheduler import lifespan
app = FastAPI(lifespan=lifespan)
app.include_router(r1)
app.include_router(r2)