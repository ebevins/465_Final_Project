#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

DB="sports_cards.db"
SQLITE="${SQLITE:-sqlite3}"

echo "Recreating database..."
rm -f "$DB"
"$SQLITE" "$DB" < schema.sql
"$SQLITE" "$DB" < insert_data.sql

echo
echo "Running queries..."
"$SQLITE" -header -column "$DB" < queries.sql

echo
echo "Running transaction..."
if ! "$SQLITE" -bail "$DB" < transaction.sql; then
    echo "Transaction failed. See the SQLite error above." >&2
    exit 1
fi
echo "Transaction completed successfully; the demonstration rolled back its changes."

echo
echo "Done."
