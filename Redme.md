# ⚙️ Autovermietungssystem mit FastAPI

Ein Web-API-Projekt zur Verwaltung einer Autovermietung, entwickelt mit **FastAPI** und **PostgreSQL**.  
Das System ist vollständig mit **Docker** integriert, um eine einfache Ausführung und Bereitstellung zu ermöglichen.

Das Projekt umfasst die Verwaltung von Kunden, Autos, Verträgen, Zahlungen und Benutzern.

---

## 🛠️ Verwendete Technologien

- **Programmiersprache**: Python 3.11  
- **Web-Framework**: FastAPI  
- **Datenbank**: PostgreSQL  
- **ORM**: SQLAlchemy  
- **Tests**: Pytest  
- **Authentifizierung**: JWT, bcrypt  
- **Scheduler**: APScheduler  
- **Logging**: Integriertes Python-Logging  
- **Containerisierung**: Docker, Docker Compose

---

## ⚙️ Hauptfunktionen

- 🧾 Vollständige Verwaltung von:  
  - Kunden (`kunden`)  
  - Autos (`autos`)  
  - Verträgen (`verträge`)  
  - Zahlungen (`zahlungen`)  
  - Benutzer (`user`)  
- 🛡️ **JWT-Authentifizierungssystem** für sicheren Login  
- 🔒 **Passwortverschlüsselung** mit `bcrypt`  
- 🕒 **Geplanter Task** mit `APScheduler` zur täglichen Vertragsstatus-Aktualisierung  
- 📋 **Logging-System** zur Fehler- und Ereignisprotokollierung  
- 🧪 **Automatisierte Tests** mit `pytest`  
- 🐳 **Docker & Docker Compose** für einfache Ausführung  
- 🌐 **Saubere Projektstruktur** mit modularen Routern

---

## ⚙️ Umgebungsvariablen (.env)

Erstelle eine `.env`-Datei im Projektverzeichnis mit folgendem Inhalt:
POSTGRES_USER=postgres
POSTGRES_PASSWORD=supersecretpassword
POSTGRES_DB=DB1
DATABASE_URL=postgresql+psycopg2://postgres:supersecretpassword@db:5432/DB1
SECRET_KEY=supersecretkey123456789
ALGORITHM=HS256


## 🚀 Projekt starten
git clone https://github.com/TihanIbrahim/Auto_mieten_neu1-master.git
cd Auto_mieten_neu1-master
docker-compose up --build
