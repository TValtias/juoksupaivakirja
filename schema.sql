CREATE INDEX IF NOT EXISTS idx_entries_user ON entries (user_id);
CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries (created_at);
CREATE INDEX IF NOT EXISTS idx_entries_terrain ON entries (terrain_id);
CREATE INDEX IF NOT EXISTS idx_entries_run_type ON entries (run_type_id);
CREATE INDEX IF NOT EXISTS idx_entries_competition ON entries (competition_id);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    distance_km INTEGER NOT NULL,
    distance_m INTEGER NOT NULL,
    runtime TEXT NOT NULL,
    terrain_id INTEGER NOT NULL,
    run_type_id INTEGER NOT NULL,
    competition_id INTEGER,
    competition_name TEXT,
    other TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (terrain_id) REFERENCES terrains(id),
    FOREIGN KEY (run_type_id) REFERENCES run_types(id),
    FOREIGN KEY (competition_id) REFERENCES competitions(id)
);

CREATE TABLE IF NOT EXISTS supports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supporter_id INTEGER NOT NULL,
    supported_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supporter_id) REFERENCES users(id),
    FOREIGN KEY (supported_id) REFERENCES users(id),
    UNIQUE (supporter_id, supported_id)
);

CREATE INDEX IF NOT EXISTS idx_user_id ON entries(user_id);

CREATE TABLE IF NOT EXISTS competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    description2 TEXT,
    banner_image TEXT,
    map_image TEXT
);

CREATE TABLE IF NOT EXISTS competition_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS run_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO run_types (name) VALUES
('kevyt'),
('tavoitteellinen'),
('kilpailuun tähtäävä'),
('kisat');


CREATE TABLE IF NOT EXISTS terrains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO terrains (name) VALUES
('juoksumatto'),
('katu'),
('rata'),
('hiekka'),
('metsä/epätasainen');