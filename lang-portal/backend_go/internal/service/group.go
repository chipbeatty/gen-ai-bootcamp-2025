package service

import (
	"database/sql"
)

type GroupService struct {
	db *sql.DB
}

type Group struct {
	ID   int    `json:"id"`
	Name string `json:"name"`
	WordCount int `json:"word_count"`
}

type GroupWithWords struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Words []struct {
		ID                int    `json:"id"`
		LatinWord         string `json:"latin_word"`
		EnglishTranslation string `json:"english_translation"`
	} `json:"words"`
}

func NewGroupService(db *sql.DB) *GroupService {
	return &GroupService{db: db}
}

// GetGroups retrieves all groups with their word counts
func (s *GroupService) GetGroups() ([]Group, error) {
	query := `
		SELECT g.id, g.name, COUNT(wg.word_id) as word_count
		FROM groups g
		LEFT JOIN words_groups wg ON g.id = wg.group_id
		GROUP BY g.id, g.name
		ORDER BY g.name`

	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var groups []Group
	for rows.Next() {
		var g Group
		if err := rows.Scan(&g.ID, &g.Name, &g.WordCount); err != nil {
			return nil, err
		}
		groups = append(groups, g)
	}

	return groups, nil
}

// GetGroupByID retrieves a single group with its words
func (s *GroupService) GetGroupByID(id int) (*GroupWithWords, error) {
	// First get the group
	var group GroupWithWords
	err := s.db.QueryRow("SELECT id, name FROM groups WHERE id = ?", id).Scan(&group.ID, &group.Name)
	if err == sql.ErrNoRows {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}

	// Then get its words
	query := `
		SELECT w.id, w.latin_word, w.english_translation
		FROM words w
		JOIN words_groups wg ON w.id = wg.word_id
		WHERE wg.group_id = ?
		ORDER BY w.latin_word`

	rows, err := s.db.Query(query, id)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	for rows.Next() {
		var word struct {
			ID                int    `json:"id"`
			LatinWord         string `json:"latin_word"`
			EnglishTranslation string `json:"english_translation"`
		}
		if err := rows.Scan(&word.ID, &word.LatinWord, &word.EnglishTranslation); err != nil {
			return nil, err
		}
		group.Words = append(group.Words, word)
	}

	return &group, nil
}

// CreateGroup creates a new word group
func (s *GroupService) CreateGroup(name string) (*Group, error) {
	result, err := s.db.Exec("INSERT INTO groups (name) VALUES (?)", name)
	if err != nil {
		return nil, err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}

	return &Group{
		ID:   int(id),
		Name: name,
		WordCount: 0,
	}, nil
}

// AddWordToGroup adds a word to a group
func (s *GroupService) AddWordToGroup(wordID, groupID int) error {
	_, err := s.db.Exec(
		"INSERT INTO words_groups (word_id, group_id) VALUES (?, ?)",
		wordID, groupID,
	)
	return err
}

// RemoveWordFromGroup removes a word from a group
func (s *GroupService) RemoveWordFromGroup(wordID, groupID int) error {
	_, err := s.db.Exec(
		"DELETE FROM words_groups WHERE word_id = ? AND group_id = ?",
		wordID, groupID,
	)
	return err
}
