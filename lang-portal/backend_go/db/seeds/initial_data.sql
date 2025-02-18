-- Insert sample groups
INSERT INTO groups (name) VALUES
    ('Basic Latin Vocabulary'),
    ('Common Verbs'),
    ('Nouns and Adjectives');

-- Insert sample words
INSERT INTO words (latin_word, english_translation, parts) VALUES
    ('amare', 'to love', '{"type": "verb", "conjugation": 1}'),
    ('videre', 'to see', '{"type": "verb", "conjugation": 2}'),
    ('puer', 'boy', '{"type": "noun", "declension": 2}'),
    ('puella', 'girl', '{"type": "noun", "declension": 1}'),
    ('bonus', 'good', '{"type": "adjective", "declension": "1st/2nd"}');

-- Link words to groups
INSERT INTO words_groups (word_id, group_id) VALUES
    (1, 1), -- amare -> Basic Latin Vocabulary
    (1, 2), -- amare -> Common Verbs
    (2, 1), -- videre -> Basic Latin Vocabulary
    (2, 2), -- videre -> Common Verbs
    (3, 1), -- puer -> Basic Latin Vocabulary
    (3, 3), -- puer -> Nouns and Adjectives
    (4, 1), -- puella -> Basic Latin Vocabulary
    (4, 3), -- puella -> Nouns and Adjectives
    (5, 1), -- bonus -> Basic Latin Vocabulary
    (5, 3); -- bonus -> Nouns and Adjectives

-- Insert a sample study session
INSERT INTO study_sessions (group_id, created_at) VALUES
    (1, datetime('now', '-2 days')),
    (2, datetime('now', '-1 days')),
    (1, datetime('now'));

-- Insert sample word review items
INSERT INTO word_review_items (word_id, study_session_id, correct, created_at) VALUES
    (1, 1, 1, datetime('now', '-2 days')),
    (2, 1, 0, datetime('now', '-2 days')),
    (3, 1, 1, datetime('now', '-2 days')),
    (4, 2, 1, datetime('now', '-1 days')),
    (5, 2, 1, datetime('now', '-1 days')),
    (1, 3, 1, datetime('now')),
    (2, 3, 1, datetime('now'));
