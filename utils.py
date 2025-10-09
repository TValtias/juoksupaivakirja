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
