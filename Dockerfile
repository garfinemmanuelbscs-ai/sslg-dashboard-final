# 1. Use an official stable Python image
FROM python:3.11-slim

# 2. Set strict environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/home/user
ENV PATH=/home/user/.local/bin:$PATH

# 3. Install system dependencies required for OpenCV, TensorFlow, and Psycopg2
# ⚙️ UPDATED: Added wget here so the system can download the biometric weights safely
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    libpq-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 4. Provision the non-root user (Hugging Face UID 1000 standard)
RUN useradd -m -u 1000 user

# 5. Set up application directory and define ownership upfront
WORKDIR /app
RUN chown user:user /app

# Switch context to the non-root user
USER user

# 6. Cache installation layers by copying requirements first 
COPY --chown=user:user requirements.txt /app/
RUN pip install --no-cache-dir --user -r requirements.txt

# 7. Copy the rest of the SSLG management system code
COPY --chown=user:user . /app/

# 8. Set up local directories for DeepFace weights and Django assets
RUN mkdir -p /home/user/.deepface/weights /app/staticfiles /app/media

# 🧠 PRE-DOWNLOAD DEEPFACE WEIGHTS TO PREVENT RUNTIME TIMEOUTS
# Pulls down the model file directly during the build layer phase
RUN wget -O /home/user/.deepface/weights/vgg_face_weights.h5 https://huggingface.co/Hodfa71/deepface-weights/resolve/main/vgg_face_weights.h5

# 9. Collect static files safely into the allocated workspace
RUN python manage.py collectstatic --noinput

# 10. Start application server mapping to Hugging Face app port 7860
# This runs database migrations on your remote PostgreSQL, then boots Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:7860 --workers 2 --threads 4 --timeout 120 studentgov.wsgi:application"]