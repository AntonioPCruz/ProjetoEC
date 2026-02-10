CREATE TABLE IF NOT EXISTS records (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50),
    title TEXT NOT NULL,
    value NUMERIC,
    created_at TIMESTAMP
);