package models

import (
	"database/sql"
	"encoding/json"
)

type Word struct {
	ID                int             `json:"id"`
	LatinWord         string          `json:"latin_word"`
	EnglishTranslation string         `json:"english_translation"`
	Parts            json.RawMessage  `json:"parts"`
	CorrectCount     int             `json:"correct_count"`
	WrongCount       int             `json:"wrong_count"`
}

type WordPagination struct {
	Items         []Word `json:"items"`
	CurrentPage   int    `json:"current_page"`
	TotalPages    int    `json:"total_pages"`
	TotalItems    int    `json:"total_items"`
	ItemsPerPage  int    `json:"items_per_page"`
}

// GetWords retrieves a paginated list of words with their study statistics
func GetWords(page, itemsPerPage int) (*WordPagination, error) {
	offset := (page - 1) * itemsPerPage

	query := `
		SELECT w.id, w.latin_word, w.english_translation, w.parts,
			   COUNT(CASE WHEN wri.correct = 1 THEN 1 END) as correct_count,
			   COUNT(CASE WHEN wri.correct = 0 THEN 1 END) as wrong_count
		FROM words w
		LEFT JOIN word_review_items wri ON w.id = wri.word_id
		GROUP BY w.id
		LIMIT ? OFFSET ?`

	rows, err := db.Query(query, itemsPerPage, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var words []Word
	for rows.Next() {
		var w Word
		if err := rows.Scan(&w.ID, &w.LatinWord, &w.EnglishTranslation, &w.Parts,
			&w.CorrectCount, &w.WrongCount); err != nil {
			return nil, err
		}
		words = append(words, w)
	}

	// Get total count
	var totalItems int
	err = db.QueryRow("SELECT COUNT(*) FROM words").Scan(&totalItems)
	if err != nil {
		return nil, err
	}

	totalPages := (totalItems + itemsPerPage - 1) / itemsPerPage

	return &WordPagination{
		Items:        words,
		CurrentPage:  page,
		TotalPages:   totalPages,
		TotalItems:   totalItems,
		ItemsPerPage: itemsPerPage,
	}, nil
}

// GetWordByID retrieves a single word by its ID
func GetWordByID(id int) (*Word, error) {
	query := `
		SELECT w.id, w.latin_word, w.english_translation, w.parts,
			   COUNT(CASE WHEN wri.correct = 1 THEN 1 END) as correct_count,
			   COUNT(CASE WHEN wri.correct = 0 THEN 1 END) as wrong_count
		FROM words w
		LEFT JOIN word_review_items wri ON w.id = wri.word_id
		WHERE w.id = ?
		GROUP BY w.id`

	var word Word
	err := db.QueryRow(query, id).Scan(
		&word.ID, &word.LatinWord, &word.EnglishTranslation, &word.Parts,
		&word.CorrectCount, &word.WrongCount,
	)
	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	return &word, nil
}
