-- Tracks processed Stripe webhook event IDs so a redelivered event (Stripe
-- retries and can send the same event more than once) is a no-op instead
-- of double-crediting a purchase or reprocessing a subscription change.
-- Safe to run against a database created before this feature existed,
-- since fresh installs already have this shape (see the schema_migrations
-- seed at the bottom of schema.sql).

CREATE TABLE IF NOT EXISTS stripe_events (
    event_id      VARCHAR(255) PRIMARY KEY,
    event_type    VARCHAR(100) NOT NULL,
    processed_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
