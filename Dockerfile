FROM python:3.11-slim

# Create isolated user application workspace
WORKDIR /app

# Ensure SQLite components are installed correctly
RUN apt-get update && apt-get install -y sqlite3

# Mount and lock dependency stack
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sync application source payload
COPY . .

# Prevents execution stalling on un-flushed logs
ENV PYTHONUNBUFFERED=1

# Expose target Gradio port for Spaces orchestration routing
EXPOSE 7860

# Default target invokes Gradio UI Server
CMD ["python", "app.py"]
