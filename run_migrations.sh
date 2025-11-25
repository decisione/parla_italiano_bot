#!/bin/bash

# Migration runner script for Parla Italiano Bot
# Runs pending database migrations in order

set -e

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Database connection variables with defaults
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-parla_italiano}
DB_USER=${DB_USER:-parla_user}
DB_PASSWORD=${DB_PASSWORD}

# Validate required password
if [ -z "$DB_PASSWORD" ]; then
    echo "Error: DB_PASSWORD environment variable is required"
    exit 1
fi

echo "Running migrations..."
echo "Database: $DB_HOST:$DB_PORT/$DB_NAME (user: $DB_USER)"

# Function to get psql command (local or via docker)
get_psql_cmd() {
    if command -v docker >/dev/null 2>&1 && docker compose ps postgres >/dev/null 2>&1; then
        echo "docker compose exec -T postgres psql -U $DB_USER -d $DB_NAME"
    elif command -v docker-compose >/dev/null 2>&1 && docker-compose ps postgres >/dev/null 2>&1; then
        echo "docker-compose exec -T postgres psql -U $DB_USER -d $DB_NAME"
    else
        echo "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
    fi
}

PSQL_CMD=$(get_psql_cmd)

# Function to execute SQL command
run_sql() {
    PGPASSWORD=$DB_PASSWORD $PSQL_CMD -c "$1" 2>/dev/null
}

# Function to check if migration is applied
is_migration_applied() {
    local version=$1
    local result
    result=$(PGPASSWORD=$DB_PASSWORD $PSQL_CMD -t -c "SELECT 1 FROM schema_migrations WHERE version = '$version';" 2>/dev/null | tr -d ' ')
    [ "$result" = "1" ]
}

# Get list of migration files in order
for migration_file in $(ls migrations/*.sql 2>/dev/null | sort); do
    version=$(basename "$migration_file" .sql)

    if is_migration_applied "$version"; then
        echo "Migration $version already applied - skipping"
        continue
    fi

    echo "Applying migration $version..."

    # Execute the migration file
    if PGPASSWORD=$DB_PASSWORD $PSQL_CMD < "$migration_file"; then
        # Record the migration as applied
        run_sql "INSERT INTO schema_migrations (version) VALUES ('$version');"
        echo "Migration $version applied successfully"
    else
        echo "Error: Failed to apply migration $version"
        exit 1
    fi
done

echo "All migrations completed successfully"