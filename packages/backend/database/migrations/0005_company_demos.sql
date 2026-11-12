-- Company demos are disabled until explicitly published.
CREATE TABLE IF NOT EXISTS company_demos (
  slug VARCHAR(63) PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  enabled BOOLEAN NOT NULL DEFAULT FALSE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS company_demo_sources (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  slug VARCHAR(63) NOT NULL,
  url VARCHAR(1500) NOT NULL,
  content MEDIUMTEXT NOT NULL,
  FOREIGN KEY (slug) REFERENCES company_demos(slug) ON DELETE CASCADE,
  INDEX idx_demo_source_slug (slug)
);
