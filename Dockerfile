FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and data files
# Note: In production, the large text files might be mounted via volumes, 
# but for now we copy them as they are in the repo.
COPY . .

# Expose the internal port
EXPOSE 5000

# Start the application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app.main:app"]
