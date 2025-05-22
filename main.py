from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from routers import auto, kunden, vertrag, zahlung
from routers.vertrag import zwischenstatus_aktualisieren
from data_base import get_database_session, Base, engine

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include routers with tags
app.include_router(auto.router, tags=["Autos"])
app.include_router(vertrag.router, tags=["Vertrag"])
app.include_router(kunden.router, tags=["Kunden"])
app.include_router(zahlung.router, tags=["Zahlung"])


# Scheduled task to update contract statuses daily at midnight
def scheduled_task():
    db = next(get_database_session())
    zwischenstatus_aktualisieren(db)

scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_task, 'cron', hour=0, minute=0)
scheduler.start()
