# 1. Use an official Python image
FROM python:3.11-slim

# 2. Install system dependencies for OpenCV and TensorFlow
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Set the working directory
WORKDIR /app

# 4. Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the project
COPY . .

# 6. Collect static files
RUN python manage.py collectstatic --noinput

# 7. Start the server using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "sslg_dashboard.wsgi:application"]