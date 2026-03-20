#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Collect static files
echo "Collecting static files..."
python hrms/manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python hrms/manage.py migrate --noinput

# Run the command passed to the script
exec "$@"
