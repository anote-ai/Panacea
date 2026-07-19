-- Adds api_usage, a per-request log of chat completions (tokens + credits
-- charged) ported from the standalone root-level backend/ package's usage
-- metering (database/usage.py there). Flat 1 credit per request, same as
-- that implementation — token counts are stored for display only and don't
-- affect the credit charge. Safe to run against a database created before
-- this feature existed, since fresh installs already have this shape (see
-- the schema_migrations seed at the bottom of schema.sql).

CREATE TABLE IF NOT EXISTS api_usage (
    id                 INT AUTO_INCREMENT PRIMARY KEY,
    user_id            INT NOT NULL,
    endpoint           VARCHAR(100) NOT NULL,
    model              VARCHAR(100),
    prompt_tokens      INT NOT NULL DEFAULT 0,
    completion_tokens  INT NOT NULL DEFAULT 0,
    total_tokens       INT NOT NULL DEFAULT 0,
    credits_used       INT NOT NULL DEFAULT 1,
    created_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
