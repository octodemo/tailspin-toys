FROM python:3.13-slim AS runtime

LABEL org.opencontainers.image.source=https://github.com/octodemo/tailspin-toys

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code and seed data
COPY . .

# Create data directory for SQLite database
RUN mkdir -p /app/../data

ENV FLASK_APP=app.py
ENV HOST=0.0.0.0
ENV PORT=5100
EXPOSE 5100

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5100", "app:app"]
