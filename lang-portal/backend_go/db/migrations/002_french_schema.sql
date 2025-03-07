-- Rename latin_word column to french_word
ALTER TABLE words RENAME COLUMN latin_word TO french_word;

-- Add context and pronunciation_url columns
ALTER TABLE words ADD COLUMN context TEXT;
ALTER TABLE words ADD COLUMN pronunciation_url TEXT;

-- Update indexes
DROP INDEX IF EXISTS idx_words_latin_word;
CREATE INDEX IF NOT EXISTS idx_words_french_word ON words(french_word);

-- Update the JSON validation for parts to include French-specific fields
-- Note: SQLite doesn't support modifying CHECK constraints, so we need to recreate the table
CREATE TABLE IF NOT EXISTS words_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    french_word TEXT NOT NULL UNIQUE,
    english_translation TEXT NOT NULL,
    context TEXT,
    pronunciation_url TEXT,
    parts TEXT NOT NULL CHECK (json_valid(parts))
);

INSERT INTO words_new (id, french_word, english_translation, context, pronunciation_url, parts)
SELECT id, french_word, english_translation, context, pronunciation_url, parts FROM words;

DROP TABLE words;
ALTER TABLE words_new RENAME TO words;
