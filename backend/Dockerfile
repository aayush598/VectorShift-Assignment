# ===============================
# Base image
# ===============================
FROM python:3.12-slim

# ===============================
# Environment
# ===============================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

WORKDIR $APP_HOME

# ===============================
# System dependencies
# ===============================
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ===============================
# Python dependencies
# ===============================
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ===============================
# App source
# ===============================
COPY app ./app

# ===============================
# Expose & run
# ===============================
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
