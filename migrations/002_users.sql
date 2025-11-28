-- Migration 002: Create users table for tracking user first/last access and profile info

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    username VARCHAR(255),
    language_code VARCHAR(10),
    is_bot BOOLEAN NOT NULL DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    first_access_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_access_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
