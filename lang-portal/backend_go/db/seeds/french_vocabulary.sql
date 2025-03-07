-- Insert sample vocabulary groups
INSERT INTO groups (name) VALUES 
  ('Basic Greetings'),
  ('Daily Activities'),
  ('Food and Dining');

-- Insert sample French vocabulary words
INSERT INTO words (french_word, english_translation, context, parts) VALUES 
  ('bonjour', 'hello', 'Bonjour! Comment allez-vous?', '{"type": "greeting", "formality": "neutral"}'),
  ('au revoir', 'goodbye', 'Au revoir et bonne journée!', '{"type": "greeting", "formality": "neutral"}'),
  ('s''il vous plaît', 'please', 'Un café, s''il vous plaît.', '{"type": "courtesy", "formality": "formal"}'),
  ('merci beaucoup', 'thank you very much', 'Merci beaucoup pour votre aide.', '{"type": "courtesy", "formality": "neutral"}'),
  ('boulangerie', 'bakery', 'Je vais à la boulangerie acheter du pain.', '{"type": "noun", "gender": "feminine"}'),
  ('café', 'coffee', 'Je prends un café tous les matins.', '{"type": "noun", "gender": "masculine"}');

-- Associate words with groups
INSERT INTO words_groups (word_id, group_id) VALUES 
  (1, 1), -- bonjour -> Basic Greetings
  (2, 1), -- au revoir -> Basic Greetings
  (3, 1), -- s'il vous plaît -> Basic Greetings
  (4, 1), -- merci beaucoup -> Basic Greetings
  (5, 3), -- boulangerie -> Food and Dining
  (6, 3); -- café -> Food and Dining

-- Insert some sample study sessions
INSERT INTO study_sessions (group_id, created_at) VALUES 
  (1, datetime('now', '-2 days')),
  (3, datetime('now', '-1 days')),
  (1, datetime('now'));

-- Insert some sample word reviews
INSERT INTO word_review_items (word_id, study_session_id, correct, created_at) VALUES 
  (1, 1, 1, datetime('now', '-2 days')),
  (2, 1, 1, datetime('now', '-2 days')),
  (3, 1, 0, datetime('now', '-2 days')),
  (5, 2, 1, datetime('now', '-1 days')),
  (6, 2, 1, datetime('now', '-1 days')),
  (1, 3, 1, datetime('now')),
  (2, 3, 1, datetime('now'));
