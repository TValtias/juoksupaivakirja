CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    distance_km INTEGER NOT NULL,
    distance_m INTEGER NOT NULL,
    time TEXT NOT NULL,
    terrain TEXT NOT NULL,
    run_type TEXT NOT NULL,
    race_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);