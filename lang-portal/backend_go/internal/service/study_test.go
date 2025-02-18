package service

import (
	"database/sql"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	_ "github.com/mattn/go-sqlite3"
)

func setupTestDB(t *testing.T) *sql.DB {
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatalf("Failed to open test database: %v", err)
	}

	// Create tables
	_, err = db.Exec(`
		CREATE TABLE words (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			latin_word TEXT NOT NULL UNIQUE,
			english_translation TEXT NOT NULL,
			parts TEXT NOT NULL
		);

		CREATE TABLE groups (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL UNIQUE
		);

		CREATE TABLE study_sessions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			group_id INTEGER NOT NULL,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			study_activity_id INTEGER,
			FOREIGN KEY (group_id) REFERENCES groups(id)
		);

		CREATE TABLE word_review_items (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			word_id INTEGER NOT NULL,
			study_session_id INTEGER NOT NULL,
			correct BOOLEAN NOT NULL,
			created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (word_id) REFERENCES words(id),
			FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
		);
	`)
	if err != nil {
		t.Fatalf("Failed to create test tables: %v", err)
	}

	return db
}

func TestGetLastStudySession(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	service := NewStudyService(db)

	// Insert test data
	_, err := db.Exec("INSERT INTO groups (id, name) VALUES (1, 'Test Group')")
	assert.NoError(t, err)

	testTime := time.Now().Add(-24 * time.Hour)
	_, err = db.Exec(`
		INSERT INTO study_sessions (id, group_id, created_at, study_activity_id)
		VALUES (1, 1, ?, NULL)`,
		testTime,
	)
	assert.NoError(t, err)

	// Test getting last session
	session, err := service.GetLastStudySession()
	assert.NoError(t, err)
	assert.NotNil(t, session)
	assert.Equal(t, 1, session.ID)
	assert.Equal(t, 1, session.GroupID)
	assert.Equal(t, "Test Group", session.GroupName)
	assert.Nil(t, session.StudyActivityID) // Study activity ID should be nil
}

func TestGetStudyProgress(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	service := NewStudyService(db)

	// Insert test data
	_, err := db.Exec(`
		INSERT INTO words (id, latin_word, english_translation, parts)
		VALUES 
			(1, 'amare', 'to love', '{"type":"verb"}'),
			(2, 'videre', 'to see', '{"type":"verb"}'),
			(3, 'puer', 'boy', '{"type":"noun"}')
	`)
	assert.NoError(t, err)

	_, err = db.Exec(`
		INSERT INTO groups (id, name)
		VALUES (1, 'Test Group')
	`)
	assert.NoError(t, err)

	_, err = db.Exec(`
		INSERT INTO study_sessions (id, group_id)
		VALUES (1, 1)
	`)
	assert.NoError(t, err)

	_, err = db.Exec(`
		INSERT INTO word_review_items (word_id, study_session_id, correct)
		VALUES 
			(1, 1, true),
			(2, 1, false),
			(3, 1, true)
	`)
	assert.NoError(t, err)

	// Test getting progress
	progress, err := service.GetStudyProgress()
	assert.NoError(t, err)
	assert.NotNil(t, progress)
	assert.Equal(t, 3, progress.TotalWordsStudied)
	assert.Equal(t, 3, progress.TotalAvailableWords)
}

func TestGetQuickStats(t *testing.T) {
	db := setupTestDB(t)
	defer db.Close()

	service := NewStudyService(db)

	// Insert test data
	_, err := db.Exec(`
		INSERT INTO words (id, latin_word, english_translation, parts)
		VALUES 
			(1, 'amare', 'to love', '{"type":"verb"}'),
			(2, 'videre', 'to see', '{"type":"verb"}'),
			(3, 'puer', 'boy', '{"type":"noun"}'),
			(4, 'puella', 'girl', '{"type":"noun"}')
	`)
	assert.NoError(t, err)

	_, err = db.Exec("INSERT INTO groups (id, name) VALUES (1, 'Test Group')")
	assert.NoError(t, err)

	_, err = db.Exec(`
		INSERT INTO study_sessions (group_id, created_at)
		VALUES 
			(1, datetime('now', '-1 day')),
			(1, datetime('now'))
	`)
	assert.NoError(t, err)

	_, err = db.Exec(`
		INSERT INTO word_review_items (word_id, study_session_id, correct)
		VALUES 
			(1, 1, true),
			(2, 1, true),
			(3, 1, false),
			(4, 2, true)
	`)
	assert.NoError(t, err)

	// Test getting stats
	stats, err := service.GetQuickStats()
	assert.NoError(t, err)
	assert.NotNil(t, stats)
	assert.Equal(t, 2, stats.TotalStudySessions)
	assert.Equal(t, 1, stats.TotalActiveGroups)
	assert.Equal(t, 2, stats.StudyStreakDays)
	assert.InDelta(t, 75.0, stats.SuccessRate, 0.1) // 3 correct out of 4 = 75%
}
