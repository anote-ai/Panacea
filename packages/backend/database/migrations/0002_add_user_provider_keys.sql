-- Adds user_provider_keys, which lets users bring their own Anthropic/
-- OpenAI/Gemini API keys (encrypted at rest) instead of relying on the
-- server's env-configured keys. Safe to run against a database created
-- before this feature existed; fresh installs already have this shape
-- (see the schema_migrations seed at the bottom of schema.sql).

CREATE TABLE IF NOT EXISTS user_provider_keys (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    provider       VARCHAR(20) NOT NULL,
    key_encrypted  TEXT NOT NULL,
    created_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_user_provider (user_id, provider),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
