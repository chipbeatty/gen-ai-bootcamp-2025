-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS word_review_items;
DROP TABLE IF EXISTS study_sessions;
DROP TABLE IF EXISTS words_groups;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS words;

-- Create words table with French-specific fields
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    french_word TEXT NOT NULL UNIQUE,
    english_translation TEXT NOT NULL,
    context TEXT,
    pronunciation_url TEXT,
    correct_count INTEGER NOT NULL DEFAULT 0,
    wrong_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create groups table
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- Create words_groups join table
CREATE TABLE words_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE(word_id, group_id)
);

-- Create study_sessions table
CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
);

-- Create word_review_items table
CREATE TABLE word_review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    study_session_id INTEGER NOT NULL,
    correct BOOLEAN NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
    FOREIGN KEY (study_session_id) REFERENCES study_sessions(id) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX idx_words_french_word ON words(french_word);
CREATE INDEX idx_groups_name ON groups(name);
CREATE INDEX idx_word_reviews_session ON word_review_items(study_session_id);
CREATE INDEX idx_word_reviews_word ON word_review_items(word_id);
CREATE INDEX idx_study_sessions_created ON study_sessions(created_at);

-- Insert sample French vocabulary
INSERT INTO words (french_word, english_translation, context) VALUES
('bonjour', 'hello', 'Bonjour, comment allez-vous?'),
('merci', 'thank you', 'Merci beaucoup pour votre aide!'),
('au revoir', 'goodbye', 'Au revoir et bonne journée!'),
('s''il vous plaît', 'please', 'S''il vous plaît, pouvez-vous m''aider?'),
('de rien', 'you''re welcome', 'De rien, c''est un plaisir.'),
('enchanté', 'nice to meet you', 'Enchanté de faire votre connaissance.'),
('oui', 'yes', 'Oui, je comprends.'),
('non', 'no', 'Non, je ne sais pas.'),
('excusez-moi', 'excuse me', 'Excusez-moi, je ne parle pas bien français.'),
('bonne nuit', 'good night', 'Bonne nuit et faites de beaux rêves!');
