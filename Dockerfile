FROM python:3.10-slim

# Variables d'environnement pour éviter les warnings
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système nécessaires pour OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer le dossier de travail
WORKDIR /app

# Installation des packages Python en une seule couche pour optimiser
RUN pip install --no-cache-dir \
    Flask \
    Flask-SQLAlchemy \
    Flask-Session \
    influxdb_flask \
    numpy \
    scikit-learn \
    pandas \
    tensorflow \
    matplotlib \
    opencv-python \
    gdown \
    gunicorn

# Copier le code de l'application
COPY . /app

# Créer les dossiers nécessaires
RUN mkdir -p static/temp models flask_session

# Exposer le port
EXPOSE 5007

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5007/', timeout=2)" || exit 1

# Commande de démarrage mise à jour pour éviter le spam SIGWINCH
CMD ["gunicorn", "--bind", "0.0.0.0:5007", "--workers", "2", "--timeout", "120", "--no-sendfile", "--log-level", "warning", "app:app"]