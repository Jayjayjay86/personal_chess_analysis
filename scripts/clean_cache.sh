#!/bin/bash

# Chess Analysis App - Analysis Cache Cleaner

CACHE_DIR="./analysis_cache"
DAYS_TO_KEEP=30

echo "Cleaning analysis cache..."
find "$CACHE_DIR" -type f -name "*.json" -mtime +$DAYS_TO_KEEP -exec rm -f {} \;

echo "Cache cleaned. Removed files older than $DAYS_TO_KEEP days."