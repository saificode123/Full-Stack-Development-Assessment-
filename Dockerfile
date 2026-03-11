FROM python:3.11-slim
ENV PYTHONUNBUFFERED True
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# ADD THIS LINE HERE: This creates your database tables during the build
RUN python manage.py migrate --noinput

# Gunicorn is the production-grade server required for GCP/Render
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 backend.wsgi:application