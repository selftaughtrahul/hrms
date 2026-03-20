# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies (for reportlab, pycairo, etc.)
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean

# Install Python dependencies
COPY hrms/requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Create static directories
RUN mkdir -p /app/hrms/staticfiles /app/hrms/media

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Port for Django
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command for web (can be overridden in compose)
CMD ["gunicorn", "--chdir", "hrms", "hrms_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
