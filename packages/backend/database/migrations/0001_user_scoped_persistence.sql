-- Migration 0001: user-scoped chat/document persistence
--
-- Brings pre-existing databases (created from an older schema.sql) up to the
-- current schema. Fresh databases initialised from schema.sql do NOT need
-- this. Apply with: mysql anote < 0001_user_scoped_persistence.sql
--
-- chats: address sessions by UUID, allow anonymous sessions, track cwd/model
-- and last activity.

ALTER TABLE chats
    MODIFY user_id INT NULL,
    ADD COLUMN session_uuid VARCHAR(36) NULL AFTER mode,
    ADD COLUMN cwd VARCHAR(1024) DEFAULT '' AFTER session_uuid,
    ADD COLUMN model VARCHAR(100) DEFAULT '' AFTER cwd,
    ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- Backfill UUIDs for existing rows, then enforce uniqueness.
UPDATE chats SET session_uuid = UUID() WHERE session_uuid IS NULL;

ALTER TABLE chats
    MODIFY session_uuid VARCHAR(36) NOT NULL,
    ADD UNIQUE INDEX idx_chats_session_uuid (session_uuid);

-- documents: allow anonymous uploads, store file path/content type and last
-- activity.

ALTER TABLE documents
    MODIFY user_id INT NULL,
    ADD COLUMN path VARCHAR(1024) DEFAULT '' AFTER filename,
    ADD COLUMN content_type VARCHAR(255) DEFAULT '' AFTER path,
    ADD COLUMN updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP AFTER created_at;
