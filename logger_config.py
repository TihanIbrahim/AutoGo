import logging

def setup_logger(name=None):
    logger = logging.getLogger(name)  # Logger mit einem Namen erstellen oder Standardlogger verwenden
    logger.setLevel(logging.INFO)     # Log-Level auf INFO setzen

    if not logger.hasHandlers():      # Nur Handler hinzufügen, wenn noch keine vorhanden sind
        ch = logging.StreamHandler()  # Konsole als Ausgabekanal erstellen
        ch.setLevel(logging.INFO)      # Log-Level für den Handler auf INFO setzen

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # Format für Log-Nachrichten definieren
        ch.setFormatter(formatter)    # Format auf den Handler anwenden

        logger.addHandler(ch)          # Handler zum Logger hinzufügen

    return logger                     # Konfigurierten Logger zurückgeben
