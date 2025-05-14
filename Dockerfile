# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Collect static files (uncomment if needed for production)
# RUN python manage.py collectstatic --noinput

# Set environment variables for Django settings (use .env for sensitive info)
ENV DJANGO_SETTINGS_MODULE=config.settings

# Expose port 8000 for the application
EXPOSE 8000

# Default command (override in docker-compose if needed)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

