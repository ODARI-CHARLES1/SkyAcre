FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY AI-Models/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY AI-Models /app/AI-Models
COPY AI-Models/Models /app/Models
COPY AI-Models/best_model.keras /app/best_model.keras

# Set environment variables
ENV FLASK_APP=AI-Models/app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
