#!/bin/bash

# Chess Analysis App - Database Backup Script

BACKUP_DIR="./backups"
DB_FILE="./chess_games.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p "$BACKUP_DIR"

echo "Backing up database..."
sqlite3 "$DB_FILE" ".backup '$BACKUP_DIR/chess_games_$TIMESTAMP.db'"

# Keep only the last 7 backups
ls -t "$BACKUP_DIR"/chess_games_*.db | tail -n +8 | xargs rm -f

echo "Backup created: $BACKUP_DIR/chess_games_$TIMESTAMP.db"