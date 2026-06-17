"""Database query functions"""

from utils import get_db_connection, validate_runtime


def validate_positive_int(value, name):
    """Checks if the input value is a positive number
    and raises a valueerror if not"""
    try:
        value = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} tulee olla numero") from exc
    if value < 0:
        raise ValueError(f"{name} tulee olla positiivinen")
    return value

def validate_nonempty_str(value, name):
    """Checks if the field is empty and raises valueerror if it is"""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} ei saa olla tyhjä.")

def get_username(username):
    """Looks for user's information from the database with username."""
    validate_nonempty_str(username, "Username")
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT
                id, username, password_hash
            FROM
                users WHERE username = ?
            """,
            (username,),
        ).fetchone()

def create_user(username, password_hash):
    """Creates a new user to database with given username and password hash"""
    validate_nonempty_str(username, "Username")
    validate_nonempty_str(password_hash, "Password hash")
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()

def add_entry(user_id, km, m, runtime, terrain_id, run_type_id, competition_name, other):
    """Validates and saves a new run to entries-table"""
    user_id = validate_positive_int(user_id, "User ID")
    km = validate_positive_int(km, "Distance_km")
    m = validate_positive_int(m, "Distance_m")
    validate_runtime(runtime)
    terrain_id = validate_positive_int(terrain_id, "Terrain ID")
    run_type_id = validate_positive_int(run_type_id, "Run type ID")

    competition_name = competition_name.strip() if competition_name else None
    competition_id = None
    if competition_name:
        competition = get_competition_name(competition_name)
        if competition:
            competition_id = competition["id"]
    other = other.strip() if other else None

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO entries (
                user_id, distance_km,
                distance_m, runtime, terrain_id,
                run_type_id, competition_id, 
                competition_name, other
            )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, km, m, runtime, terrain_id, run_type_id, competition_id, competition_name, other)
        )
        conn.commit()

def get_entries(user_id):
    """Searches user's entries and displays their info"""
    user_id = validate_positive_int(user_id, "User ID")
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT
                e.id,
                e.distance_km,
                e.distance_m,
                e.runtime,
                t.name AS terrain,
                r.name AS run_type,
                c.name AS race_name,
                e.other,
                e.created_at
            FROM entries e
            LEFT JOIN terrains t ON e.terrain_id = t.id
            LEFT JOIN run_types r ON e.run_type_id = r.id
            LEFT JOIN competitions c ON e.competition_id =c.id
            WHERE e.user_id = ?
            ORDER BY e.created_at DESC
            """,
            (user_id,),
        ).fetchall()

def get_entry(entry_id, user_id):
    """Searches a specific entry of a user"""
    entry_id = validate_positive_int(entry_id, "Entry ID")
    user_id = validate_positive_int(user_id, "User ID")
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT
                e.id,
                e.distance_km,
                e.distance_m,
                e.runtime,
                e.terrain_id,
                e.run_type_id,
                c.name AS race_name,
                e.competition_id,
                e.competition_name,
                e.other,
                e.created_at
            FROM entries e
            LEFT JOIN competitions c ON e.competition_id = c.id
            WHERE e.id = ? AND e.user_id = ?
            """,
            (entry_id, user_id)
        ).fetchone()

def get_max_distance(user_id):
    """Calculates the longest run. Returns 0 if no runs"""
    user_id = validate_positive_int(user_id, "User ID")
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT MAX(distance_km * 1000 + distance_m)
            FROM entries
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()
        if row and row[0] is not None:
            return int(row[0])
        return 0

def get_competition_count(user_id):
    """Calculates the amount of runs that have been stated as competitions"""
    user_id = validate_positive_int(user_id, "User ID")
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*)
            FROM entries
            WHERE user_id = ?
            AND competition_id IS NOT NULL
            AND TRIM(competition_id) != ''
            """,
            (user_id,)
        ).fetchone()
        return int(row[0]) if row else 0

def get_support_count(user_id):
    """Calculates the amount of supporters / cheers the user has"""
    user_id = validate_positive_int(user_id, "User ID")
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT COUNT(*)
            FROM supports
            WHERE supported_id = ?
            """,
            (user_id,)
        ).fetchone()
        return int(row[0]) if row else 0

def already_supported(supporter_id, supported_id):
    """Checks if the user supports the username"""
    supporter_id = validate_positive_int(supporter_id, "Supporter ID")
    supported_id = validate_positive_int(supported_id, "Supported ID")
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT 1
            FROM supports
            WHERE supporter_id = ? AND supported_id = ?
            """,
            (supporter_id, supported_id)
        ).fetchone()
        return row is not None

def add_support(supporter_id, supported_id):
    """Adds a support to database to username from user"""
    supporter_id = validate_positive_int(supporter_id, "Supporter ID")
    supported_id = validate_positive_int(supported_id, "Supported ID")
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO supports (supporter_id, supported_id)
            VALUES (?, ?)
            """,
            (supporter_id, supported_id)
        )
        conn.commit()

def get_terrains():
    """Gets a list of all the terrains available"""
    with get_db_connection() as conn:
        return conn.execute("SELECT id, name FROM terrains").fetchall()

def get_run_types():
    """Gets a list of all the run types available"""
    with get_db_connection() as conn:
        return conn.execute("SELECT id, name FROM run_types").fetchall()

def update_entry(entry_id, user_id, km, m, runtime, terrain_id, run_type_id, competition_name, other):
    """Updates an existing entry with user's new input after validation"""
    entry_id = validate_positive_int(entry_id, "Entry ID")
    user_id = validate_positive_int(user_id, "User ID")
    km = validate_positive_int(km, "Distance_km")
    m = validate_positive_int(m, "Distance_m")
    validate_runtime(runtime)
    terrain_id = validate_positive_int(terrain_id, "Terrain ID")
    run_type_id = validate_positive_int(run_type_id, "Run type ID")
    competition_name = competition_name.strip() if competition_name else None
    competition_id = None

    if competition_name:
        competition = get_competition_name(competition_name)
        if competition:
            competition_id = competition["id"]

    other = other.strip() if other else None

    with get_db_connection() as conn:
        conn.execute(
            """
            UPDATE entries
            SET
                distance_km = ?,
                distance_m = ?,
                runtime = ?,
                terrain_id = ?,
                run_type_id = ?,
                competition_id = ?,
                competition_name = ?,
                other = ?
            WHERE id = ? AND user_id = ?
            """,
            (km, m, runtime, terrain_id, run_type_id, competition_id,competition_name, other, entry_id, user_id)
        )
        conn.commit()

def delete_entry(entry_id, user_id):
    """Deletes an entry form database using ID"""
    entry_id = validate_positive_int(entry_id, "Entry ID")
    user_id = validate_positive_int(user_id, "User ID")
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM entries WHERE id = ? AND user_id = ?",
            (entry_id, user_id),
        )
        conn.commit()

def search_runs(km=None, terrain=None, run_type=None, username=None):
    """Searches runs using filters"""
    search = """
        SELECT entries.*, users.username,
            t.name AS terrain,
            r.name AS run_type,
            entries.competition_name
        FROM entries
        JOIN users ON entries.user_id = users.id
        LEFT JOIN terrains t ON entries.terrain_id = t.id
        LEFT JOIN run_types r ON entries.run_type_id = r.id
        LEFT JOIN competitions c ON entries.competition_id = c.id
        WHERE 1=1
    """
    search_conditions = []

    if km is not None and km != "":
        km_int = validate_positive_int(km, "Distance_km")
        search += " AND entries.distance_km = ?"
        search_conditions.append(km_int)

    if terrain:
        terrain_ids = [validate_positive_int(t, "Terrain ID") for t in terrain]
        search += f" AND entries.terrain_id IN ({','.join(['?']*len(terrain_ids))})"
        search_conditions.extend(terrain_ids)

    if run_type:
        run_type = validate_positive_int(run_type, "Run type ID")
        search += " AND entries.run_type_id = ?"
        search_conditions.append(run_type)

    if username:
        validate_nonempty_str(username, "Username")
        search += " AND users.username LIKE ?"
        search_conditions.append(f"%{username.strip()}%")

    search += " ORDER BY entries.created_at DESC"

    with get_db_connection() as conn:
        return conn.execute(search, search_conditions).fetchall()

def get_competitions():
    """Searches competitions in id-order"""
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT id, name
            FROM competitions
            ORDER BY competitions.id
            """,
        ).fetchall()

def get_competition(competition_id):
    """Searches a competition's details, like descriptions and banners"""
    competition_id = validate_positive_int(competition_id, "Competition ID")
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT id, name, description, description2, banner_image, map_image
            FROM competitions
            WHERE id = ?
            """,
            (competition_id, )
        ).fetchone()
    
def get_competition_name(name):
    """Searches competition by name"""
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT id, name
            FROM competitions
            WHERE LOWER(name) = LOWER(?)
            """,
            (name,)
        ).fetchone()

def get_top_results(competition_id):
    """Searches the top 10 running performances for the race"""
    competition_id = validate_positive_int(
        competition_id,
        "Competition ID"
    )
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT users.username, runtime
            FROM entries
            JOIN users ON entries.user_id = users.id
            WHERE competition_id = ?
            ORDER BY runtime ASC
            LIMIT 10
            """,
            (competition_id,),
        ).fetchall()

def add_comments_competition(competition_id, user_id, comment):
    """Saves user's comment to a competition's page"""
    competition_id = validate_positive_int(competition_id, "Competition ID")
    user_id = validate_positive_int(user_id, "User ID")
    validate_nonempty_str(comment, "Comment")

    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO competition_comments (competition_id, user_id, comment)
            VALUES (?, ?, ?)
            """,
            (competition_id, user_id, comment)
        )
        conn.commit()

def get_comments_competition(competition_id):
    """Searches the 15 latest user comments for the competition"""
    competition_id = validate_positive_int(competition_id, "Competition ID")
    with get_db_connection() as conn:
        return conn.execute(
            """
            SELECT
                competition_comments.comment,
                competition_comments.created_at,
                users.username
            FROM competition_comments
            JOIN users ON competition_comments.user_id = users.id
            WHERE competition_comments.competition_id = ?
            ORDER BY competition_comments.created_at DESC
            LIMIT 15
            """,
            (competition_id,)
        ).fetchall()
