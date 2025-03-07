# Backend Server Technical Specs

## Business Goal

A language learning school wants to build a prototype of a learning portal that will serve three purposes:

- Inventory of possible vocabulary that can be learned
- Act as a Learning Record Store (LRS), providing correct and incorrect scores on practice vocabulary
- A unified launchpad to launch different learning apps

## Technical Requirements

- The backend will be built using Go
- The database will be SQLite3
- The API will be built using Gin
- Mage will be used as a task runner for Go
- The API will always return JSON
- There will be no authentication or authorization
- Everything will be treated as a single user

## Directory Structure

```text
backend_go/
├── cmd/
│   └── server/
├── internal/
│   ├── models/     # Data structures and database operations
│   ├── handlers/   # HTTP handlers organized by feature (dashboard, words, groups, etc.)
│   └── service/    # Business logic
├── db/
│   ├── migrations/
│   └── seeds/      # For initial data population
├── magefile.go
├── go.mod
└── words.db
```

## Database Schema

Our database will be a single SQLite database called `words.db`, located in the root of the project folder `backend_go`.

### Tables:

### `words`

Stored vocabulary words

| Column              | Type    |
| ------------------- | ------- |
| id                  | integer |
| latin_word          | string  |
| english_translation | string  |
| parts               | json    |

### `words_groups`

Join table for words and groups (many-to-many)

| Column   | Type    |
| -------- | ------- |
| id       | integer |
| word_id  | integer |
| group_id | integer |

### `groups`

Thematic groups of words

| Column | Type    |
| ------ | ------- |
| id     | integer |
| name   | string  |

### `study_sessions`

Records of study sessions grouping `word_review_items`

| Column            | Type     |
| ----------------- | -------- |
| id                | integer  |
| group_id          | integer  |
| created_at        | datetime |
| study_activity_id | integer  |

### `study_activities`

A specific study activity, linking a study session to a group

| Column           | Type     |
| ---------------- | -------- |
| id               | integer  |
| study_session_id | integer  |
| group_id         | integer  |
| created_at       | datetime |

### `word_review_items`

A record of word practice, determining if the word was correct or not

| Column           | Type     |
| ---------------- | -------- |
| word_id          | integer  |
| study_session_id | integer  |
| correct          | boolean  |
| created_at       | datetime |

---

## API Endpoints

### **GET /api/dashboard/last_study_session**

Returns information about the most recent study session.

#### JSON Response:

```json
{
  "id": 123,
  "group_id": 456,
  "created_at": "2025-02-08T17:20:23-05:00",
  "study_activity_id": 789,
  "group_name": "Basic Latin Vocabulary"
}
```

### **GET /api/dashboard/study_progress**

Returns study progress statistics.

#### JSON Response:

```json
{
  "total_words_studied": 3,
  "total_available_words": 124
}
```

### **GET /api/dashboard/quick-stats**

Returns quick overview statistics.

#### JSON Response:

```json
{
  "success_rate": 80.0,
  "total_study_sessions": 4,
  "total_active_groups": 3,
  "study_streak_days": 4
}
```

---

## Words Endpoints

### **GET /api/words**

Returns a paginated list of words.

#### JSON Response:

```json
{
  "items": [
    {
      "latin_word": "amare",
      "english_translation": "to love",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 5,
    "total_items": 500,
    "items_per_page": 100
  }
}
```

### **GET /api/words/:id**

Retrieves a specific word.

#### JSON Response:

```json
{
  "latin_word": "amare",
  "english_translation": "to love",
  "stats": {
    "correct_count": 5,
    "wrong_count": 2
  },
  "groups": [
    {
      "id": 1,
      "name": "Basic Latin Vocabulary"
    }
  ]
}
```

---

## Groups Endpoints

### **GET /api/groups**

Returns a list of groups.

#### JSON Response:

```json
{
  "items": [
    {
      "id": 1,
      "name": "Basic Latin Vocabulary",
      "word_count": 20
    }
  ]
}
```

### **GET /api/groups/:id**

Retrieves a specific group.

#### JSON Response:

```json
{
  "id": 1,
  "name": "Basic Latin Vocabulary",
  "stats": {
    "total_word_count": 20
  }
}
```

---

## Task Runner Tasks

### **Initialize Database**

This task will initialize the SQLite database called `words.db`.

### **Migrate Database**

This task will run a series of migration SQL files on the database.

Migration files are stored in the `migrations` folder and are executed in sequential order.

Example:

```sql
0001_init.sql
0002_create_words_table.sql
```

### **Seed Data**

This task will import JSON files and transform them into target data for our database.

Example seed data:

```json
[
  {
    "latin_word": "amare",
    "english_translation": "to love"
  },
  {
    "latin_word": "scribere",
    "english_translation": "to write"
  }
]
```
