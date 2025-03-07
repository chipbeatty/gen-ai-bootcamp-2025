#!/bin/bash

# Create the SQLite database
sqlite3 ../words.db < migrations/001_initial_schema.sql
sqlite3 ../words.db < migrations/002_french_schema.sql
sqlite3 ../words.db < seeds/french_vocabulary_fixed.sql
