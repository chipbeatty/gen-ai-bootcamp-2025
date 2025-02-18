package models

import "time"

type StudySession struct {
	ID              int       `json:"id"`
	GroupID         int       `json:"group_id"`
	CreatedAt       time.Time `json:"created_at"`
	StudyActivityID int       `json:"study_activity_id"`
	GroupName       string    `json:"group_name"`
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

// GetLastStudySession retrieves the most recent study session
func GetLastStudySession() (*StudySession, error) {
	query := `
		SELECT s.id, s.group_id, s.created_at, s.study_activity_id, g.name
		FROM study_sessions s
		JOIN groups g ON s.group_id = g.id
		ORDER BY s.created_at DESC
		LIMIT 1`

	var session StudySession
	err := db.QueryRow(query).Scan(
		&session.ID,
		&session.GroupID,
		&session.CreatedAt,
		&session.StudyActivityID,
		&session.GroupName,
	)
	if err != nil {
		return nil, err
	}
	return &session, nil
}

// GetStudyProgress retrieves the overall study progress
func GetStudyProgress() (*StudyProgress, error) {
	query := `
		SELECT 
			(SELECT COUNT(DISTINCT word_id) FROM word_review_items) as studied,
			(SELECT COUNT(*) FROM words) as total`

	var progress StudyProgress
	err := db.QueryRow(query).Scan(&progress.TotalWordsStudied, &progress.TotalAvailableWords)
	if err != nil {
		return nil, err
	}
	return &progress, nil
}

// GetQuickStats retrieves quick overview statistics
func GetQuickStats() (*QuickStats, error) {
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
	err := db.QueryRow(query).Scan(
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
