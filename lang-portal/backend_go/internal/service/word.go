package service

import (
	"database/sql"
	"fmt"
	"lang-portal/internal/models"
)

type WordService struct {
	db *sql.DB
}

func NewWordService(db *sql.DB) *WordService {
	return &WordService{db: db}
}

func (s *WordService) GetWords(page, itemsPerPage int) (*models.WordPagination, error) {
	offset := (page - 1) * itemsPerPage

	// Get total count
	var totalItems int
	err := s.db.QueryRow("SELECT COUNT(*) FROM words").Scan(&totalItems)
	if err != nil {
		return nil, fmt.Errorf("failed to get total count: %v", err)
	}

	// Get paginated words
	rows, err := s.db.Query(`
		SELECT id, french_word, english_translation, context, pronunciation_url,
			   correct_count, wrong_count
		FROM words
		ORDER BY french_word
		LIMIT ? OFFSET ?
	`, itemsPerPage, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to query words: %v", err)
	}
	defer rows.Close()

	var words []models.Word
	for rows.Next() {
		var word models.Word
		var context, pronunciationURL sql.NullString
		err := rows.Scan(
			&word.ID,
			&word.FrenchWord,
			&word.EnglishTranslation,
			&context,
			&pronunciationURL,
			&word.CorrectCount,
			&word.WrongCount,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan word: %v", err)
		}

		// Ensure empty strings instead of null
		word.Context = context.String
		word.PronunciationURL = pronunciationURL.String
		words = append(words, word)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("error iterating words: %v", err)
	}

	totalPages := (totalItems + itemsPerPage - 1) / itemsPerPage
	return &models.WordPagination{
		Items:        words,
		CurrentPage:  page,
		TotalPages:   totalPages,
		TotalItems:   totalItems,
		ItemsPerPage: itemsPerPage,
	}, nil
}

func (s *WordService) GetWordByID(id int) (*models.Word, error) {
	var word models.Word
	var context, pronunciationURL, parts sql.NullString

	err := s.db.QueryRow(`
		SELECT id, french_word, english_translation, context, pronunciation_url,
			   correct_count, wrong_count
		FROM words
		WHERE id = ?
	`, id).Scan(
		&word.ID,
		&word.FrenchWord,
		&word.EnglishTranslation,
		&context,
		&pronunciationURL,
		&word.CorrectCount,
		&word.WrongCount,
	)
	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, fmt.Errorf("failed to get word: %v", err)
	}

	// Ensure empty strings instead of null
	word.Context = context.String
	word.PronunciationURL = pronunciationURL.String
	word.Parts = parts.String
	return &word, nil
}
