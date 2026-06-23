import random
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "database.db"

USER_COUNT = 100_000
ENTRY_COUNT = 1_000_000
COMPETITION_COUNT = 500

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("DELETE FROM supports")
    conn.execute("DELETE FROM competition_comments")
    conn.execute("DELETE FROM entries")
    conn.execute("DELETE FROM competitions")
    conn.execute("DELETE FROM users")

    # Oletetaan, että terrains ja run_types on jo täytetty
    terrains = conn.execute("SELECT id FROM terrains").fetchall()
    run_types = conn.execute("SELECT id FROM run_types").fetchall()

    if not terrains or not run_types:
        raise RuntimeError("Täytä ensin terrains ja run_types -taulut ennen seed.py ajoa")

    terrain_ids = [row["id"] for row in terrains]
    run_type_ids = [row["id"] for row in run_types]

    print("Luodaan käyttäjiä...")
    for i in range(1, USER_COUNT + 1):
        username = f"user{i}"
        password_hash = generate_password_hash("password")
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))

    print("Luodaan kilpailuja...")
    for i in range(1, COMPETITION_COUNT + 1):
        name = f"Competition {i}"
        description = f"Kuvaus kilpailulle {i}"
        conn.execute("INSERT INTO competitions (name, description) VALUES (?, ?)", (name, description))

    conn.commit()

    competition_rows = conn.execute("SELECT id, name FROM competitions").fetchall()
    competition_ids = [row["id"] for row in competition_rows]

    print("Luodaan juoksumerkintöjä...")
    for i in range(1, ENTRY_COUNT + 1):
        user_id = random.randint(1, USER_COUNT)
        km = random.randint(0, 42)  # max 42 km
        m = random.randint(0, 999)   # max 999 m
        runtime = f"{random.randint(0, 5):02d}:{random.randint(0, 59):02d}:{random.randint(0, 59):02d}"
        terrain_id = random.choice(terrain_ids)
        run_type_id = random.choice(run_type_ids)

        if random.random() < 0.3 and competition_ids:
            comp_id = random.choice(competition_ids)
            comp_name = None  # data comes from competitions table
        else:
            comp_id = None
            comp_name = f"Local race {random.randint(1, 100)}" if random.random() < 0.1 else None

        other = f"Test entry {i}"

        conn.execute(
            """
            INSERT INTO entries (
                user_id, distance_km, distance_m,
                runtime, terrain_id, run_type_id,
                competition_id, competition_name, other, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (user_id, km, m, runtime, terrain_id, run_type_id, comp_id, comp_name, other)
        )

        if i % 10_000 == 0:
            print(f"{i}/{ENTRY_COUNT} entries luotu...")
            conn.commit()

    conn.commit()
    conn.close()
    print("Valmis.")

if __name__ == "__main__":
    main()
