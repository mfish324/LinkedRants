FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
echo "Starting gunicorn on port $PORT..."\n\
exec gunicorn linkedrants.wsgi:application --bind 0.0.0.0:$PORT --log-level info --access-logfile - --error-logfile -' > /app/start.sh && chmod +x /app/start.sh

# Run startup script
CMD ["/bin/bash", "/app/start.sh"]
