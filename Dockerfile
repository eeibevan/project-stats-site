FROM archlinux:latest

RUN pacman -Syu --noconfirm && \
    pacman -S --noconfirm python python-pip && \
    pacman -Scc --noconfirm

WORKDIR /app
COPY requirements-prod.txt .

RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    /app/venv/bin/pip install --no-cache-dir -r requirements-prod.txt

COPY . .

VOLUME ["/app/data"]

RUN useradd -m -s /bin/bash flaskuser && \
    chown -R flaskuser:flaskuser /app
USER flaskuser

EXPOSE 8000

# Run Flask application
CMD ["/app/venv/bin/gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]