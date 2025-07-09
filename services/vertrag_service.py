from datetime import date
from sqlalchemy.orm import Session
from core.logger_config import setup_logger
from data_base import get_database_session  


logger = setup_logger(__name__)

def berechne_mitdauer(beginnt_datum: date, beendet_datum: date) -> int:
    """
    Berechnet die Dauer in Tagen zwischen beginnt_datum und beendet_datum.
    Raises ValueError, wenn beginnt_datum >= beendet_datum.
    """
    if beginnt_datum >= beendet_datum:
        raise ValueError("Beginndatum muss vor Enddatum liegen")
    return (beendet_datum - beginnt_datum).days


def zwischenstatus_aktualisieren():
    db: Session = next(get_database_session())
    try:
   
        print("Status aktualisieren läuft...")
   
    finally:
        db.close()

