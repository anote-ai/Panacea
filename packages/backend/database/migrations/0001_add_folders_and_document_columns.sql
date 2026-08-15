-- Adds the folders table plus documents.folder_id / documents.chat_id,
-- which the folders/chat-scoped documents feature depends on.
-- Safe to run against a database created before that feature existed,
-- since databases bootstrapped from database/schema.sql already have
-- this shape and skip this file (see the schema_migrations seed at the
-- bottom of schema.sql).

CREATE TABLE IF NOT EXISTS folders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    name        VARCHAR(255) NOT NULL,
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

ALTER TABLE documents
    ADD COLUMN folder_id INT NULL AFTER user_id,
    ADD COLUMN chat_id INT NULL AFTER folder_id;

ALTER TABLE documents
    ADD CONSTRAINT fk_documents_folder_id FOREIGN KEY (folder_id) REFERENCES folders(id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_documents_chat_id FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE SET NULL;
