# API Tests

This test file provides:

1. Complete setup instructions
2. Test cases for major endpoints
3. Sample data for each test
4. Expected response structures
5. Cleanup commands

## Setup Test Database

The test database should be created in the `test` directory:

```bash
# Create test database
cd /Users/chip/Projects/gen-ai-bootcamp/lang-portal/backend_go
sqlite3 test/test.db < db/migrations/001_initial_schema.sql
```

Note: The test database is separate from the main application database to ensure test data doesn't interfere with actual application data.

### 1. Dashboard Last Study Session

#### Insert test data:

```sql
INSERT INTO groups (id, name) VALUES (1, 'Test Latin Group');

INSERT INTO study_sessions (id, group_id, created_at)
VALUES (1, 1, datetime('now', '-1 day'));
```

#### Expected response structure:

```json
{
  "id": 1,
  "group_id": 1,
  "created_at": "2025-02-18T17:47:19Z",
  "group_name": "Test Latin Group"
}
```

#### Test command:

```sh
curl http://localhost:8080/api/dashboard/last_study_session
```

#### Cleanup:

```sql
DELETE FROM study_sessions;
DELETE FROM groups;
```

---

### 2. Dashboard Study Progress

#### Insert test data:

```sql
INSERT INTO groups (id, name) VALUES (1, 'Test Latin Group');

INSERT INTO words (id, latin_word, english_translation, parts) VALUES
(1, 'amo', 'love', 'verb'),
(2, 'puer', 'boy', 'noun'),
(3, 'puella', 'girl', 'noun');

INSERT INTO study_sessions (id, group_id, created_at)
VALUES (1, 1, datetime('now', '-1 day'));

INSERT INTO word_review_items (word_id, study_session_id, correct, created_at) VALUES
(1, 1, true, datetime('now', '-1 day'));
```

#### Expected response structure:

```json
{
  "total_words_studied": 3,
  "total_available_words": 3,
  "correct_answers": 2,
  "incorrect_answers": 1
}
```

#### Test command:

```sh
curl http://localhost:8080/api/dashboard/study_progress
```

#### Cleanup:

```sql
DELETE FROM word_review_items;
DELETE FROM study_sessions;
DELETE FROM words;
DELETE FROM groups;
```

---

### 3. Dashboard Quick Stats

#### Insert test data:

```sql
INSERT INTO groups (id, name) VALUES
(1, 'Test Latin Group'),
(2, 'Advanced Latin');

INSERT INTO study_sessions (id, group_id, created_at) VALUES
(1, 1, datetime('now', '-3 day')),
(2, 1, datetime('now', '-2 day')),
(3, 2, datetime('now', '-1 day'));

INSERT INTO word_review_items (word_id, study_session_id, correct) VALUES
(1, 1, true),
(2, 1, true),
(3, 2, false),
(1, 3, true);
```

#### Expected response structure:

```json
{
  "success_rate": 75.0,
  "total_study_sessions": 3,
  "total_active_groups": 2,
  "study_streak_days": 3
}
```

#### Test command:

```sh
curl http://localhost:8080/api/dashboard/quick-stats
```

#### Cleanup:

```sql
DELETE FROM word_review_items;
DELETE FROM study_sessions;
DELETE FROM groups;
```

---

### 4. Get Words (with pagination)

#### Insert test data:

```sql
INSERT INTO words (latin_word, english_translation, parts) VALUES
('amo', 'love', 'verb'),
('puer', 'boy', 'noun'),
('puella', 'girl', 'noun'),
('et', 'and', 'conjunction'),
('in', 'in/on/at', 'preposition');
```

#### Expected response structure:

```json
{
  "items": [
    {
      "id": 1,
      "latin_word": "amo",
      "english_translation": "love",
      "parts": "verb"
    },
    {
      "id": 2,
      "latin_word": "puer",
      "english_translation": "boy",
      "parts": "noun"
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 2
}
```

#### Test pagination:

```sh
curl "http://localhost:8080/api/words?page=1&per_page=2"
curl "http://localhost:8080/api/words?page=2&per_page=2"
```

#### Test invalid pagination:

```sh
curl "http://localhost:8080/api/words?page=0&per_page=2"
curl "http://localhost:8080/api/words?page=1&per_page=0"
```

#### Cleanup:

```sql
DELETE FROM words;
```

---

### 5. Create Study Session

#### Insert test data:

```sql
INSERT INTO groups (id, name) VALUES (1, 'Test Latin Group');
```

#### Expected response structure:

```json
{
  "id": 1,
  "group_id": 1,
  "created_at": "2025-02-19T17:47:19Z",
  "group_name": "Test Latin Group"
}
```

#### Test command:

```sh
curl -X POST http://localhost:8080/api/study/sessions \
  -H "Content-Type: application/json" \
  -d '{"group_id": 1}'
```

#### Cleanup:

```sql
DELETE FROM study_sessions;
DELETE FROM groups;
```

---

_(The document continues with the remaining test cases formatted in the same structured manner.)_
