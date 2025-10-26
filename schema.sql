-- schema.sql
CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    wpm INTEGER NOT NULL,
    accuracy FLOAT NOT NULL,
    duration_seconds INTEGER DEFAULT 60,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add a unique constraint to the username column
ALTER TABLE leaderboard ADD CONSTRAINT unique_username UNIQUE (username);

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_leaderboard_wpm ON leaderboard(wpm DESC);
CREATE INDEX IF NOT EXISTS idx_leaderboard_username ON leaderboard(username);