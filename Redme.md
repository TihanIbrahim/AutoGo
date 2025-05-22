# 🚗 Autovermietungssystem mit FastAPI

Ein Web-API-Projekt zur Verwaltung einer Autovermietung mit **FastAPI** und **PostgreSQL**.  
Das System ist vollständig mit **Docker** integriert für eine einfache Ausführung und Bereitstellung.

Es umfasst die Verwaltung von **Kunden**, **Autos** und **Verträgen**.

---

## ⚙️ Hauptfunktionen

- 🛡️ **JWT-Authentifizierungssystem** für sicheren Login  
- 🔒 **Passwortverschlüsselung** mit `bcrypt`  
- 🧾 Vollständige Verwaltung von:
  - Kunden (`kunden`)
  - Autos (`autos`)
  - Verträgen (`verträge`)
- 🕒 **Geplanter Task** mit `APScheduler` zur täglichen Vertragsstatus-Aktualisierung  
- 🧪 **Automatisierte Tests** mit `pytest`  
- 🐳 **Docker & Docker Compose** für einfache Ausführung  
- 🌐 **Saubere Projektstruktur** mit modularen Routern für jede Funktion

---

## 🚀 Projekt starten

Projekt mit Docker starten:  
```bash
docker-compose up --build



## Verwendete Technologien
FastAPI
PostgreSQL
SQLAlchemy
Docker
APScheduler
pytest
JWT
bcrypt

