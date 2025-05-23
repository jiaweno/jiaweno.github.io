FROM python:3.10-slim

WORKDIR /app

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

# Install system dependencies that might be needed by Python packages
# e.g., for psycopg2, sometimes build-essential or libpq-dev are needed
# RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

# Ensure the app directory and its contents are owned by the app user
# RUN chown -R app:app /app # Disabling for now, may cause issues with some setups

# Switch to the non-root user
# USER app # Disabling for now

EXPOSE 8000

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# Use reload for development, but not for production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
