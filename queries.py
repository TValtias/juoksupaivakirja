from utils import get_db_connection
import sqlite3
import re


def validate_positive_int(value, name):
    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} tulee olla numero")
    
def validate_nonempty_str(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} ei saa olla tyhjä.")
    
def validate_runtime(value):
    if not isinstance(value, str):
        raise ValueError("Juoksuaika tulee olla hh:mm:ss")
    form = r'^(0?[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$'
    if not re.match(form, value):
        raise ValueError("Juoksuaika tulee olla esim. 00:20:45")
    hours, minutes, seconds = map(int, value.split(":"))

    if hours < 0 or hours > 23:
        raise ValueError("Tuntien tulee olla väliltä 00-23")
    if minutes < 0 or minutes > 59:
        raise ValueError("Minuuttien tulee olla väliltä 00-59")
    if seconds < 0 or seconds >59:
        raise ValueError("Sekuntien tulee olla väliltä 00-59")

def get_username(username):
    validate_nonempty_str(username, "Username")
    with get_db_connection() as connecting:
        return connecting.execute("SELECT id, username, password_hash FROM users WHERE username =?", (username,)).fetchone()
    
def create_user(username, password_hash):
    validate_nonempty_str(username, "Username")
    validate_nonempty_str(password_hash, "Password hash")
    try:
        with get_db_connection() as connecting:
            connecting.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
            connecting.commit()
    except sqlite3.IntegrityError:
        raise ValueError("Joku toinen ehti ensin. Valitse toinen käyttäjänimi")

def add_entry(user_id, km, m, runtime, terrain, run_type, race_name, other):
    validate_positive_int(user_id, "User ID")
    validate_positive_int(km, "Distance_km")
    validate_positive_int(m, "Distance_m")
    validate_runtime(runtime)
    validate_nonempty_str(terrain, "Terrain")
    validate_nonempty_str(run_type, "Run type")
    race_name = race_name.strip() if race_name and race_name.strip() != "" else None
    other = other.strip() if other else None

    with get_db_connection() as connecting:
        connecting.execute(
            "INSERT INTO entries (user_id, distance_km, distance_m, runtime, terrain, run_type, race_name, other) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, km, m, runtime, terrain, run_type, race_name, other)
        )
        connecting.commit()

def get_entries(user_id):
    validate_positive_int(user_id, "User ID")
    with get_db_connection() as connecting:
        return connecting.execute("SELECT id, distance_km, distance_m, runtime, terrain, run_type, race_name, other, created_at FROM entries WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
    
def get_entry(entry_id, user_id):
    validate_positive_int(entry_id, "Entry ID")
    validate_positive_int(user_id, "User ID")
    with get_db_connection() as conn:
        return conn.execute(
            "SELECT id, distance_km, distance_m, runtime, terrain, run_type, race_name, other, created_at FROM entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id)
        ).fetchone()
    
def get_max_distance(user_id):
    with get_db_connection() as connecting:
        row= connecting.execute (
            "SELECT MAX(distance_km * 1000 + distance_m) FROM entries WHERE user_id = ?", (user_id,)
        ).fetchone()
        if row and row[0] is not None:
            return int(row[0])
        return 0
    
def get_competition_count(user_id):
    with get_db_connection() as connecting:
        row = connecting.execute(
            "SELECT COUNT(*) FROM entries WHERE user_id = ? AND race_name IS NOT NULL AND TRIM(race_name) != ''",
            (user_id,)
        ).fetchone()
        return int(row[0]) if row else 0
    
def get_support_count(user_id):
    with get_db_connection() as connecting:
        row = connecting.execute(
            "SELECT COUNT(*) FROM supports WHERE supported_id = ?",
            (user_id,)
        ).fetchone()
        return int(row[0]) if row else 0
        
    
def already_supported(supporter_id, supported_id):
    validate_positive_int(supporter_id, "Supporter ID")
    validate_positive_int(supported_id, "Supported ID")
    with get_db_connection() as connecting:
        row = connecting.execute(
            "SELECT 1 FROM supports WHERE supporter_id = ? AND supported_id = ?",
            (supporter_id, supported_id)
        ).fetchone()
        return row is not None
    
def add_support(supporter_id, supported_id):
    validate_positive_int(supporter_id, "Supporter ID")
    validate_positive_int(supported_id, "Supported ID")
    with get_db_connection() as connecting:
        connecting.execute(
            "INSERT INTO supports (supporter_id, supported_id) VALUES (?, ?)",
            (supporter_id, supported_id)
        )
        connecting.commit()
    
def get_terrains():
    with get_db_connection() as connecting:
        return connecting.execute("SELECT name FROM terrains").fetchall()
    
def get_run_types():
    with get_db_connection() as connecting:
        return connecting.execute("SELECT name FROM run_types").fetchall()
    

def update_entry(entry_id, user_id, km, m, runtime, terrain, run_type, race_name, other):
    validate_positive_int(entry_id, "Entry ID")
    validate_positive_int(user_id, "User ID")
    validate_positive_int(km, "Distance_km")
    validate_positive_int(m, "Distance_m")
    validate_runtime(runtime)
    validate_nonempty_str(terrain, "Terrain")
    validate_nonempty_str(run_type, "Run type")
    
    race_name=race_name.strip() if race_name and race_name.strip() != "" else None
    other = other.strip() if other else None
    with get_db_connection() as connecting:
        connecting.execute(
            """UPDATE entries SET distance_km =?, distance_m =?, runtime =?, terrain =?, run_type =?, race_name =?, other =? 
            WHERE id =? AND user_id = ?""",
            (km, m, runtime, terrain, run_type, race_name, other, entry_id, user_id)
        )
        connecting.commit()

def delete_entry(entry_id, user_id):
    validate_positive_int(entry_id, "Entry ID")
    validate_positive_int(user_id, "User  ID")
    with get_db_connection() as connecting:
        connecting.execute("DELETE FROM entries WHERE id = ? AND user_id =?", (entry_id, user_id))
        connecting.commit()

def search_runs(km=None, terrain=None, run_type=None, username=None):
    search = """
        SELECT entries.*, users.username
        FROM entries
        JOIN users ON entries.user_id = users.id
        WHERE 1=1
        """
    search_conditions = []
    if km:
        validate_positive_int(int(km), "Distance_km")
        search += " AND entries.distance_km = ?"
        search_conditions.append(int(km))

    if terrain:
        if isinstance(terrain, list) and len(terrain) > 0:
            placeholders = ','.join(['?'] * len(terrain))
            search += f" AND entries.terrain IN ({placeholders})"
            search_conditions.extend(terrain)
        elif isinstance(terrain, str):
            validate_nonempty_str(terrain, "Terrain")
            search += " AND entries.terrain = ?"
            search_conditions.append(terrain.strip())
    if run_type:
        validate_nonempty_str(run_type, "Run type")
        search += " AND entries.run_type = ?"
        search_conditions.append(run_type.strip())
    if username:
        validate_nonempty_str(username, "Username")
        search += " AND users.username LIKE ?"
        search_conditions.append(f"%{username.strip()}%")

    search += " ORDER BY entries.created_at DESC"

    with get_db_connection() as connecting:
        return connecting.execute(search, search_conditions).fetchall()

def get_competitions():
    with get_db_connection() as connecting:
        return connecting.execute("SELECT id, name FROM competitions ORDER BY competitions.id").fetchall()
    
def get_competition(competition_id):
    with get_db_connection() as connecting:
        return connecting.execute(
            "SELECT id, name, description, description2, banner_image, map_image FROM competitions WHERE id = ?", (competition_id, )
        ).fetchone()
    
def get_top_results(competition_name):
    with get_db_connection() as connecting:
        return connecting.execute(
            """SELECT users.username, runtime FROM entries JOIN users ON entries.user_id = users.id WHERE race_name = ? ORDER BY runtime ASC
            LIMIT 10
        """, (competition_name,)
        ).fetchall()

def add_comments_competition(competition_id, user_id, comment):
    with get_db_connection() as connecting:
        connecting.execute(
            "INSERT INTO competition_comments (competition_id, user_id, comment) VALUES (?, ?, ?)",
            (competition_id, user_id, comment)
        ) 
        connecting.commit()

def get_comments_competition(competition_id):
    with get_db_connection() as connecting:
        return connecting.execute(
            """SELECT competition_comments.comment, competition_comments.created_at, users.username
            FROM competition_comments JOIN users ON competition_comments.user_id = users.id
            WHERE competition_comments.competition_id =? 
            ORDER BY competition_comments.created_at DESC
            LIMIT 15
            """, (competition_id,)
        ).fetchall()
