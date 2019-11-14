CREATE TABLE IF NOT EXISTS Movies (
    movie_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    popularity REAL NOT NULL,
    director TEXT NOT NULL,
    imdb_score REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE
);