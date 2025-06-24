from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

# Routers for App
from routers_app import auto as app_auto
from routers_app import kunden as app_kunden
from routers_app import vertrag as app_vertrag
from routers_app import zahlung as app_zahlung
from routers_app import auth

# Routers for Dashboard
from routers_dashboard import auto as dashboard_auto
from routers_dashboard import kunden as dashboard_kunden
from routers_dashboard import vertrag as dashboard_vertrag
from routers_dashboard import zahlung as dashboard_zahlung

# Services & Database
from services.vertrag_service import zwischenstatus_aktualisieren
from data_base import engine, Base

# Create FastAPI instance
app = FastAPI(
    title="Auto Mieten API",
    version="1.0.0",
    description="API für Auto-Vermietung mit Dashboard und App"
)

# Create tables if not exist
Base.metadata.create_all(bind=engine)

# Include App routers
app.include_router(app_auto.router,tags=["App Autos"])
app.include_router(app_kunden.router,tags=["App Kunden"])
app.include_router(app_vertrag.router,tags=["App Vertraege"])
app.include_router(app_zahlung.router,tags=["App Zahlungen"])

# Include Dashboard routers
app.include_router(dashboard_auto.router,tags=["Dashboard Autos"])
app.include_router(dashboard_kunden.router,tags=["Dashboard Kunden"])
app.include_router(dashboard_vertrag.router,tags=["Dashboard Vertraege"])
app.include_router(dashboard_zahlung.router,tags=["Dashboard Zahlungen"])


app.include_router(auth.router,tags=["auth"])








# Background Scheduler setup


scheduler = BackgroundScheduler()
scheduler.add_job(zwischenstatus_aktualisieren, "interval", hours=1)
scheduler.start()
