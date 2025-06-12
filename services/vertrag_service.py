from datetime import date

def berschnet_mitdauer(beginnt_datum:date , beendet_datum:date)->int:
    if beginnt_datum >= beendet_datum :
        raise ValueError("Beginndatum muss vor Enddatum liegen")
    return(beendet_datum - beginnt_datum).days