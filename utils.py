import re
import sqlite3

def get_db_connection():
    connecting = sqlite3.connect("database.db")

    connecting.row_factory = sqlite3.Row
    return connecting

def strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True

def validate_entry_form(km_str, m_str, runtime, terrain_id, run_type_id):
    errors = []

    km = None
    m = None

    try:
        km =int(km_str)
        m = int(m_str)

        if km < 0 or m < 0:
            errors.append("Matkan määrä ei voi olla negatiivinen")
    except ValueError:
        errors.append("Juoksun pituus tulee ilmoittaa numeroina")

    if not runtime:
        errors.append("Täytä juoksun aika")
    else:
        try:
            validate_runtime(runtime)
        except ValueError as e:
            errors.append(str(e))

    if not terrain_id:
        errors.append("Valitse maasto")

    if not run_type_id:
        errors.append("Valitse juoksun tyyppi")

    return errors, km, m

def validate_runtime(value):
    if not isinstance(value, str):
        raise ValueError("Juoksuaika tulee olla hh:mm:ss")

    form = r"^([0-1]\d|2[0-3]):[0-5]\d:[0-5]\d$"
    if not re.match(form, value):
        raise ValueError("Juoksuaika tulee olla esim. 00:20:45")

    hours, minutes, seconds = map(int, value.split(":"))

    if hours < 0 or hours > 23:
        raise ValueError("Tuntien tulee olla väliltä 00-23")
    if minutes < 0 or minutes > 59:
        raise ValueError("Minuuttien tulee olla väliltä 00-59")
    if seconds < 0 or seconds > 59:
        raise ValueError("Sekuntien tulee olla väliltä 00-59")
