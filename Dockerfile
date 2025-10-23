# 1. Point de départ : une image Python 3.10 légère
FROM python:3.10-slim

# 2. Définir le dossier de travail à l'intérieur du conteneur
WORKDIR /app

# 3. Copier d'abord le fichier des dépendances
# (Astuce de cache : Docker n'exécute cette étape que si
# requirements.txt a changé)
COPY requirements.txt .

# 4. Installer les dépendances
# --no-cache-dir réduit la taille finale de l'image
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier tout le reste de notre code (main.py)
COPY . .

# 6. Exposer le port sur lequel notre API (uvicorn) tourne
EXPOSE 8000

# 7. La commande pour lancer l'application quand le conteneur démarre
# IMPORTANT : On utilise --host 0.0.0.0 pour que l'API soit 
# accessible depuis l'extérieur du conteneur.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]