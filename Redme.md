# ⚙️ Autovermietungssystem mit FastAPI

Ein Web-API-Projekt zur Verwaltung einer Autovermietung, entwickelt mit FastAPI und PostgreSQL.  
Das System ist vollständig mit Docker integriert, um eine einfache Ausführung und Bereitstellung zu ermöglichen.  
Das Projekt umfasst die Verwaltung von Kunden, Autos, Verträgen, Zahlungen und Benutzern.  
Die API bietet separate Endpunkte für die Web-Anwendung und das Dashboard zur Verwaltung und Überwachung des Systems.

---

⚠️ **Projektstatus:** In Entwicklung  
🌐 **Systemtyp:** Nur Web-API (keine Benutzeroberfläche)  

Das System aktualisiert täglich automatisch den Vertragsstatus um Mitternacht.

---

## 🛠️ Verwendete Technologien

Dieses Projekt nutzt wichtige Technologien, um eine sichere und zuverlässige Autovermietungs-API bereitzustellen.

- **Programmiersprache:** Python 3.11  
- **Web-Framework:** FastAPI – für die schnelle und einfache Entwicklung der API  
- **Datenbank:** PostgreSQL – zur zuverlässigen Speicherung der Daten  
- **ORM:** SQLAlchemy – um einfach mit der Datenbank zu arbeiten  
- **Tests:** Pytest – für automatische Tests, die sicherstellen, dass alles richtig funktioniert  
- **Authentifizierung:** JWT und bcrypt – für eine sichere Anmeldung und Passwortverschlüsselung  
- **Scheduler:** APScheduler – für geplante Aufgaben wie tägliche Updates der Vertragsdaten  
- **Logging:** Python-Logging – um Fehler zu erkennen und das System zu überwachen  
- **Containerisierung:** Docker und Docker Compose – damit das Programm leicht gestartet und verwaltet werden kann  

---

## ⚙️ Hauptfunktionen

Das System bietet folgende wichtige Funktionen zur Verwaltung einer Autovermietung:

- 🧾 Vollständige Verwaltung von:  
  - Kunden (`kunden`)  
  - Autos (`autos`)  
  - Verträgen (`verträge`)  
  - Zahlungen (`zahlungen`)  
  - Benutzern (`user`)  

- 🛡️ Sicheres Login durch ein JWT-Authentifizierungssystem  
- 🔒 Passwortverschlüsselung mit `bcrypt` für erhöhte Sicherheit  
- 🕒 Geplante tägliche Aktualisierung des Vertragsstatus mittels `APScheduler`  
- 📋 Umfassendes Logging zur Fehler- und Ereignisprotokollierung  
- 🧪 Automatisierte Tests mit `pytest` zur Sicherstellung der Funktionalität  
- 🐳 Einfache Ausführung und Bereitstellung durch Docker und Docker Compose  
- 🌐 Saubere und modulare Projektstruktur mit klar getrennten Routern  

---

## 🚀 Projekt lokal starten (ohne Docker)

Folge diesen Schritten, um das Projekt lokal auf deinem Rechner auszuführen:

---

### 1. Voraussetzungen installieren

Stelle sicher, dass folgende Programme installiert sind:

- **Python 3.11**  
- **PostgreSQL** (lokale Datenbank)  
- **pip** (Python-Paketmanager)  

---

### 2. Projekt klonen

```bash
git clone https://github.com/TihanIbrahim/AutoGo.git
cd AutoGo
```

---

### 3. Virtuelle Umgebung erstellen und aktivieren (optional, aber empfohlen)

Erstelle eine virtuelle Umgebung mit folgendem Befehl:

```bash
python -m venv venv
```

Aktiviere die virtuelle Umgebung:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

---

### 4. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

---

### 5. Umgebungsvariablen konfigurieren

Erstelle im Projektverzeichnis eine Datei namens **.env** mit folgendem Beispielinhalt *(ersetze die Werte durch deine eigenen)*:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Geheim123
POSTGRES_DB=autovermietung
DATABASE_URL=postgresql+psycopg2://postgres:Geheim123@localhost:5432/autovermietung
SECRET_KEY=SehrSichererSchluessel987654
ALGORITHM=HS256
```

---

### 6. Server starten

Starte den FastAPI-Server lokal:

```bash
uvicorn main:app --reload
```

✅ Ergebnis:  
Der Server läuft nun auf:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

--------------------------------------------------------------------

## 🚀 🐳 Projekt mit Docker starten

Wenn du Docker verwenden möchtest, folge diesen Schritten:

---

### 1. Docker Desktop installieren
Stelle sicher, dass Docker Desktop auf deinem Rechner installiert und gestartet ist.
Du kannst Docker Desktop hier herunterladen: https://www.docker.com/products/docker-desktop


---

### 2. Projekt klonen (falls noch nicht geschehen)

git clone https://github.com/TihanIbrahim/AutoGo.git
cd AutoGo

---

### 3. Docker-Container bauen und starten

Führe folgenden Befehl im Projektordner aus:
docker-compose up --build

---

### 4. Ergebnis
Der Server läuft nun im Docker-Container und ist erreichbar unter: http://127.0.0.1:8000


---

### 5. Docker-Container stoppen
Zum Stoppen drücke CTRL + C im Terminal oder führe aus:
docker-compose down

---