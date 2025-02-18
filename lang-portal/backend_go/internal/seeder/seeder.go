package seeder

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type SeedData struct {
	Groups []Group `json:"groups"`
	Words  []Word  `json:"words"`
}

type Group struct {
	Name string `json:"name"`
}

type Word struct {
	LatinWord          string          `json:"latin_word"`
	EnglishTranslation string          `json:"english_translation"`
	Parts             json.RawMessage `json:"parts"`
	Groups            []string        `json:"groups"`
}

// Seeder handles database seeding operations
type Seeder struct {
	db *sql.DB
}

// NewSeeder creates a new seeder instance
func NewSeeder(db *sql.DB) *Seeder {
	return &Seeder{db: db}
}

// LoadFromJSON loads seed data from a JSON file
func (s *Seeder) LoadFromJSON(filePath string) error {
	// Read and parse JSON file
	data, err := os.ReadFile(filePath)
	if err != nil {
		return fmt.Errorf("failed to read seed file: %v", err)
	}

	var seedData SeedData
	if err := json.Unmarshal(data, &seedData); err != nil {
		return fmt.Errorf("failed to parse seed data: %v", err)
	}

	// Begin transaction
	tx, err := s.db.Begin()
	if err != nil {
		return fmt.Errorf("failed to start transaction: %v", err)
	}
	defer tx.Rollback()

	// Create groups and store their IDs
	groupIDs := make(map[string]int64)
	for _, group := range seedData.Groups {
		result, err := tx.Exec("INSERT INTO groups (name) VALUES (?)", group.Name)
		if err != nil {
			return fmt.Errorf("failed to insert group %s: %v", group.Name, err)
		}
		id, err := result.LastInsertId()
		if err != nil {
			return fmt.Errorf("failed to get group ID for %s: %v", group.Name, err)
		}
		groupIDs[group.Name] = id
	}

	// Create words and their group associations
	for _, word := range seedData.Words {
		// Insert word
		result, err := tx.Exec(
			"INSERT INTO words (latin_word, english_translation, parts) VALUES (?, ?, ?)",
			word.LatinWord,
			word.EnglishTranslation,
			word.Parts,
		)
		if err != nil {
			return fmt.Errorf("failed to insert word %s: %v", word.LatinWord, err)
		}

		wordID, err := result.LastInsertId()
		if err != nil {
			return fmt.Errorf("failed to get word ID for %s: %v", word.LatinWord, err)
		}

		// Create word-group associations
		for _, groupName := range word.Groups {
			groupID, ok := groupIDs[groupName]
			if !ok {
				return fmt.Errorf("unknown group name: %s", groupName)
			}

			_, err = tx.Exec(
				"INSERT INTO words_groups (word_id, group_id) VALUES (?, ?)",
				wordID,
				groupID,
			)
			if err != nil {
				return fmt.Errorf("failed to associate word %s with group %s: %v",
					word.LatinWord, groupName, err)
			}
		}
	}

	// Commit transaction
	if err := tx.Commit(); err != nil {
		return fmt.Errorf("failed to commit transaction: %v", err)
	}

	return nil
}

// LoadAllSeedFiles loads all JSON files from the seeds directory
func (s *Seeder) LoadAllSeedFiles(seedDir string) error {
	files, err := filepath.Glob(filepath.Join(seedDir, "*.json"))
	if err != nil {
		return fmt.Errorf("failed to list seed files: %v", err)
	}

	for _, file := range files {
		if err := s.LoadFromJSON(file); err != nil {
			return fmt.Errorf("failed to load seed file %s: %v", file, err)
		}
	}

	return nil
}
