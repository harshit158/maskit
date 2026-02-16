FROM python:3.11-slim

# ---------- system deps ----------
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------- install uv ----------
RUN pip install --no-cache-dir uv
# ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# ---------- copy dependency files first (for caching) ----------
COPY pyproject.toml ./
COPY uv.lock ./

# ---------- create venv ----------
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# ---------- install dependencies ----------
RUN uv sync --frozen --no-dev

# ---------- copy project ----------
COPY src/ ./src/

# ---------- streamlit ----------
EXPOSE 8501

ENV PYTHONPATH=/app

CMD ["uv", "run", "streamlit", "run", "src/streamlit_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]