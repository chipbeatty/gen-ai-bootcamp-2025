package service

import (
	"database/sql"
	"time"
)

type StudyService struct {
	db *sql.DB
}

type StudySession struct {
	ID              int        `json:"id"`
	GroupID         int        `json:"group_id"`
	CreatedAt       time.Time  `json:"created_at"`
	StudyActivityID *int       `json:"study_activity_id,omitempty"`
	GroupName       string     `json:"group_name"`
}

type StudyProgress struct {
	TotalWordsStudied    int `json:"total_words_studied"`
	TotalAvailableWords  int `json:"total_available_words"`
}

type QuickStats struct {
	SuccessRate        float64 `json:"success_rate"`
	TotalStudySessions int     `json:"total_study_sessions"`
	TotalActiveGroups  int     `json:"total_active_groups"`
	StudyStreakDays    int     `json:"study_streak_days"`
}

type WordReviewItem struct {
	ID              int       `json:"id"`
	WordID          int       `json:"word_id"`
	StudySessionID  int       `json:"study_session_id"`
	Correct         bool      `json:"correct"`
	CreatedAt       time.Time `json:"created_at"`
}

func NewStudyService(db *sql.DB) *StudyService {
	return &StudyService{db: db}
}

// GetLastStudySession retrieves the most recent study session
func (s *StudyService) GetLastStudySession() (*StudySession, error) {
	query := `
		SELECT s.id, s.group_id, s.created_at, s.study_activity_id, g.name
		FROM study_sessions s
		JOIN groups g ON s.group_id = g.id
		ORDER BY s.created_at DESC
		LIMIT 1`

	var session StudySession
	var studyActivityID sql.NullInt64
	err := s.db.QueryRow(query).Scan(
		&session.ID,
		&session.GroupID,
		&session.CreatedAt,
		&studyActivityID,
		&session.GroupName,
	)
	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	if studyActivityID.Valid {
		session.StudyActivityID = new(int)
		*session.StudyActivityID = int(studyActivityID.Int64)
	}
	return &session, nil
}

// GetStudyProgress retrieves the overall study progress
func (s *StudyService) GetStudyProgress() (*StudyProgress, error) {
	query := `
		SELECT 
			(SELECT COUNT(DISTINCT word_id) FROM word_review_items) as studied,
			(SELECT COUNT(*) FROM words) as total`

	var progress StudyProgress
	err := s.db.QueryRow(query).Scan(&progress.TotalWordsStudied, &progress.TotalAvailableWords)
	if err != nil {
		return nil, err
	}
	return &progress, nil
}

// GetQuickStats retrieves quick overview statistics
func (s *StudyService) GetQuickStats() (*QuickStats, error) {
	query := `
		WITH stats AS (
			SELECT 
				CAST(SUM(CASE WHEN correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / 
				CAST(COUNT(*) AS FLOAT) * 100 as success_rate,
				COUNT(DISTINCT study_session_id) as total_sessions
			FROM word_review_items
		),
		active_groups AS (
			SELECT COUNT(DISTINCT group_id) as active_groups
			FROM study_sessions
			WHERE created_at >= datetime('now', '-30 days')
		),
		streak AS (
			SELECT COUNT(DISTINCT date(created_at)) as streak_days
			FROM study_sessions
			WHERE created_at >= datetime('now', '-30 days')
		)
		SELECT 
			success_rate,
			total_sessions,
			active_groups,
			streak_days
		FROM stats, active_groups, streak`

	var stats QuickStats
	err := s.db.QueryRow(query).Scan(
		&stats.SuccessRate,
		&stats.TotalStudySessions,
		&stats.TotalActiveGroups,
		&stats.StudyStreakDays,
	)
	if err != nil {
		return nil, err
	}
	return &stats, nil
}

// CreateStudySession creates a new study session
func (s *StudyService) CreateStudySession(groupID int) (*StudySession, error) {
	query := `
		INSERT INTO study_sessions (group_id, created_at)
		VALUES (?, datetime('now'))
		RETURNING id, group_id, created_at`

	var session StudySession
	err := s.db.QueryRow(query, groupID).Scan(
		&session.ID,
		&session.GroupID,
		&session.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	// Get the group name
	err = s.db.QueryRow("SELECT name FROM groups WHERE id = ?", groupID).Scan(&session.GroupName)
	if err != nil {
		return nil, err
	}

	return &session, nil
}

// AddWordReview adds a word review item to a study session
func (s *StudyService) AddWordReview(sessionID, wordID int, correct bool) (*WordReviewItem, error) {
	query := `
		INSERT INTO word_review_items (word_id, study_session_id, correct, created_at)
		VALUES (?, ?, ?, datetime('now'))
		RETURNING id, word_id, study_session_id, correct, created_at`

	var review WordReviewItem
	err := s.db.QueryRow(query, wordID, sessionID, correct).Scan(
		&review.ID,
		&review.WordID,
		&review.StudySessionID,
		&review.Correct,
		&review.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	return &review, nil
}

// GetSessionReviews retrieves all word reviews for a specific study session
func (s *StudyService) GetSessionReviews(sessionID int) ([]WordReviewItem, error) {
	query := `
		SELECT id, word_id, study_session_id, correct, created_at
		FROM word_review_items
		WHERE study_session_id = ?
		ORDER BY created_at ASC`

	rows, err := s.db.Query(query, sessionID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var reviews []WordReviewItem
	for rows.Next() {
		var review WordReviewItem
		if err := rows.Scan(
			&review.ID,
			&review.WordID,
			&review.StudySessionID,
			&review.Correct,
			&review.CreatedAt,
		); err != nil {
			return nil, err
		}
		reviews = append(reviews, review)
	}

	return reviews, nil
}
