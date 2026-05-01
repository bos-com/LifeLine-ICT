from fastapi import FastAPI
from app.routers import crud

app = FastAPI(title="LifeLine ICT API")

app.include_router(crud.router)
