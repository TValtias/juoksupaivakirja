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
    runtime TEXT NOT NULL,
    terrain TEXT NOT NULL,
    run_type TEXT NOT NULL,
    race_name TEXT,
    other TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_user_id ON entries(user_id);

CREATE TABLE competitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    description2 TEXT,
    banner_image TEXT,
    map_image TEXT
);

CREATE TABLE competition_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    competition_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (competition_id) REFERENCES competitions(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE run_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO run_types (name) VALUES
('kevyt'),
('tavoitteellinen'),
('kilpailuun tähtäävä'),
('kisat');


CREATE TABLE terrains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

INSERT INTO terrains (name) VALUES
('juoksumatto'),
('katu'),
('rata'),
('hiekka'),
('metsä/epätasainen');