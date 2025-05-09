from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from routers import auto, kunden, vertrag
from routers.vertrag import zwischenstatus_aktuliseren
from data_base import get_database_session, Base, engine
from models import auto as auto_model, kunden as kunden_model, vertrag as vertrag_model
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auto.router, tags=["Autos"])
app.include_router(vertrag.router, tags=["Vertrag"])
app.include_router(kunden.router, tags=["Kunden"])

def scheduled_task():
    db = next(get_database_session()) 
    zwischenstatus_aktuliseren(db)

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'cron', hour=0, minute=0)
scheduler.start()
