from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler

# Router für die App
from routers.app import auto as app_auto
from routers.app import kunden as app_kunden
from routers.app import vertrag as app_vertrag
from routers.app import zahlung as app_zahlung
from routers.app import auth 

# Router für das Dashboard
from routers.dashboard import auto as dashboard_auto
from routers.dashboard import kunden as dashboard_kunden
from routers.dashboard import vertrag as dashboard_vertrag
from routers.dashboard import zahlung as dashboard_zahlung

# Services & Datenbank
from services.vertrag_service import zwischenstatus_aktualisieren
from data_base import engine, Base

# Erstelle FastAPI-Instanz
app = FastAPI(
    title="Auto Mieten API",
    version="1.0.0",
    description="API für Auto-Vermietung mit Dashboard und App"
)

# Tabellen erstellen, falls nicht vorhanden
Base.metadata.create_all(bind=engine)

# App-Router einbinden
app.include_router(app_auto.router, tags=["App Autos"])
app.include_router(app_kunden.router, tags=["App Kunden"])
app.include_router(app_vertrag.router, tags=["App Vertraege"])
app.include_router(app_zahlung.router, tags=["App Zahlungen"])

# Dashboard-Router einbinden
app.include_router(dashboard_auto.router, tags=["Dashboard Autos"])
app.include_router(dashboard_kunden.router, tags=["Dashboard Kunden"])
app.include_router(dashboard_vertrag.router, tags=["Dashboard Vertraege"])
app.include_router(dashboard_zahlung.router, tags=["Dashboard Zahlungen"])

# Authentifizierungs-Router einbinden
app.include_router(auth.router, tags=["auth"])

# Hintergrundscheduler einrichten
scheduler = BackgroundScheduler()
scheduler.add_job(zwischenstatus_aktualisieren, "interval", hours=1)
scheduler.start()
