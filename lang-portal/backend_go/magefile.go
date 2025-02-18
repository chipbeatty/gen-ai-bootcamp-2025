//go:build mage
package main

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"

	"github.com/magefile/mage/mg"
	"github.com/magefile/mage/sh"
	_ "github.com/mattn/go-sqlite3"
	"lang-portal/internal/seeder"
)

// Default target to run when none is specified
var Default = Run

const dbFile = "words.db"

// Aliases for mage targets
var Aliases = map[string]interface{}{
	"r": Run,
	"s": Seed,
	"c": Clean,
	"i": InitDB,
}

// Clean removes the database file
func Clean() error {
	mg.Deps(ensureDir)
	fmt.Println("Cleaning up database file...")
	err := os.Remove(dbFile)
	if err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("failed to remove database: %v", err)
	}
	fmt.Println("Cleanup complete")
	return nil
}

// InitDB creates a new SQLite database and runs all migrations
func InitDB() error {
	mg.Deps(ensureDir)
	fmt.Println("Initializing database...")

	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		return fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()

	// Read and execute migration files
	migrations, err := filepath.Glob("db/migrations/*.sql")
	if err != nil {
		return fmt.Errorf("failed to find migration files: %v", err)
	}

	for _, migration := range migrations {
		fmt.Printf("Executing migration: %s\n", migration)
		content, err := os.ReadFile(migration)
		if err != nil {
			return fmt.Errorf("failed to read migration file %s: %v", migration, err)
		}

		_, err = db.Exec(string(content))
		if err != nil {
			return fmt.Errorf("failed to execute migration %s: %v", migration, err)
		}
	}

	fmt.Println("Database initialization complete")
	return nil
}

// Seed populates the database with initial data from JSON files
func Seed() error {
	mg.Deps(InitDB)
	fmt.Println("Seeding database...")

	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		return fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()

	// Create seeder instance
	s := seeder.NewSeeder(db)

	// Load all JSON seed files
	if err := s.LoadAllSeedFiles("db/seeds"); err != nil {
		return fmt.Errorf("failed to load seed data: %v", err)
	}

	fmt.Println("Database seeding complete")
	return nil
}

// Reset cleans and reinitializes the database with seed data
func Reset() error {
	mg.SerialDeps(Clean, InitDB, Seed)
	return nil
}

// Run starts the server
func Run() error {
	mg.Deps(InitDB)
	fmt.Println("Starting server on :8081...")
	return sh.Run("go", "run", "cmd/server/main.go")
}

// ensureDir ensures required directories exist
func ensureDir() error {
	dirs := []string{
		"db/migrations",
		"db/seeds",
	}

	for _, dir := range dirs {
		if err := os.MkdirAll(dir, 0755); err != nil {
			return fmt.Errorf("failed to create directory %s: %v", dir, err)
		}
	}
	return nil
}
