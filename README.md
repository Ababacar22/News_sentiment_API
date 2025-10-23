# Mon API d'Analyse de Sentiment / My News Sentiment API

Ce projet est une API complète qui scrape le texte d'un article d'actualité, analyse son sentiment (positif, négatif, neutre) à l'aide d'un modèle NLP, et renvoie le résultat. Il est entièrement conteneurisé avec Docker.

*This project is a complete API that scrapes the text from a news article, analyzes its sentiment (positive, negative, neutral) using an NLP model, and returns the result. It is fully containerized with Docker.*

---

<details>
<summary><strong>🇫🇷 Version Française (Cliquez pour voir)</strong></summary>

## 🧠 Concepts Clés que j'ai appris

Ce projet m'a permis de maîtriser deux concepts fondamentaux :

1.  **Le Pipeline NLP :** J'ai compris comment enchaîner plusieurs étapes de traitement pour transformer un texte non structuré (un article de blog) en une donnée structurée (un score de sentiment). Mon pipeline est : `URL -> Requête HTTP -> Parsing HTML -> Extraction de Texte -> Tokenisation -> Inférence du Modèle -> JSON (Sentiment)`.
2.  **La Conteneurisation :** J'ai appris pourquoi le "ça marche sur ma machine" n'est pas suffisant. En créant un `Dockerfile`, j'ai "emballé" mon application, ses dépendances Python et même le lourd modèle d'IA dans une image portable, reproductible et prête pour le déploiement.

## 🛠️ Mon Architecture et mes Fonctionnalités

J'ai conçu ce service autour de trois piliers principaux, en y ajoutant des fonctionnalités pour le rendre robuste et performant.

### 1. Le Scraper (Data Science)
J'ai utilisé `requests` pour télécharger le code HTML d'une URL et `BeautifulSoup4` pour le parser. J'ai implémenté une logique simple (cibler les balises `<p>`) pour extraire le corps principal du texte, tout en gérant les erreurs HTTP et de scraping.

### 2. L'Analyseur de Sentiment (IA / NLP)
C'est le cœur de mon application. J'utilise la bibliothèque `transformers` de Hugging Face pour charger un modèle pré-entraîné (`cardiffnlp/twitter-roberta-base-sentiment`). J'ai fait en sorte que ce modèle ne soit chargé **qu'une seule fois** au démarrage de l'API pour garantir des performances optimales.

### 3. L'API (Développement Logiciel)
J'ai choisi `FastAPI` pour sa rapidité et sa simplicité.
* Il crée un point de terminaison `POST /analyze` qui accepte une URL.
* J'utilise `Pydantic` pour valider automatiquement les données d'entrée (`HttpUrl`).
* Il génère automatiquement une documentation interactive (`/docs`) que j'ai utilisée pour tous mes tests.

### ✨ Fonctionnalités Avancées
* **Mise en Cache :** J'ai implémenté un simple cache en mémoire (un dictionnaire Python) pour stocker les résultats. Si la même URL est demandée plusieurs fois, la réponse est instantanée (vérifiable avec le champ `"from_cache": true`) et évite de re-scraper le site.
* **Gestion des Erreurs :** Mon API ne crashe pas. Elle renvoie des codes d'erreur HTTP appropriés (422, 404, 503...) si l'URL est invalide, le scraping échoue ou le modèle n'est pas chargé.

## 💻 Technologies Utilisées

Pour construire ce projet, je me suis appuyé sur :

* **Python 3.10**
* **FastAPI** : Pour le framework d'API web.
* **Uvicorn** : Pour servir mon application FastAPI.
* **Hugging Face `transformers`** : Pour le pipeline NLP et le modèle RoBERTa.
* **PyTorch** : En tant que backend pour le modèle `transformers`.
* **Requests** & **BeautifulSoup4** : Pour le web scraping.
* **Docker** : Pour la conteneurisation.

## 🚀 Comment l'utiliser

Vous pouvez lancer ce projet de deux manières.

### Méthode 1 : Lancement avec Docker (Recommandé)

C'est la méthode la plus simple, car j'ai déjà tout configuré dans le `Dockerfile`.

1.  **Assurez-vous que Docker Desktop est en cours d'exécution.**

2.  **Construisez l'image :**
    *(Cette étape sera longue la première fois à cause de PyTorch)*
    ```bash
    docker build -t sentiment-api .
    ```

3.  **Lancez le conteneur :**
    ```bash
    docker run -p 8000:8000 -it sentiment-api
    ```
    Votre API est maintenant accessible sur `http://127.0.0.1:8000`.

### Méthode 2 : Lancement Local (Développement)

1.  **Clonez ce dépôt :**
    ```bash
    git clone [https://github.com/VOTRE_NOM/VOTRE_REPO.git](https://github.com/VOTRE_NOM/VOTRE_REPO.git)
    cd VOTRE_REPO
    ```

2.  **Créez un environnement virtuel et activez-le :**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Installez mes dépendances :**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancez le serveur API :**
    ```bash
    uvicorn main:app --reload
    ```
    Votre API est maintenant accessible sur `http://127.0.0.1:8000`.

## Tester l'API

Une fois l'API lancée (localement ou via Docker), vous avez deux façons de la tester :

### 1. Avec l'interface web (ma méthode préférée)

J'ai trouvé que le plus simple est d'utiliser la documentation auto-générée :

1.  Ouvrez votre navigateur et allez sur **http://127.0.0.1:8000/docs**
2.  Cliquez sur le point de terminaison `POST /analyze`.
3.  Cliquez sur "Try it out".
4.  Collez une URL d'article dans le corps de la requête, par exemple :
    ```json
    {
      "url": "[https://www.reuters.com/business/finance/global-markets-wrapup-1-2022-09-21/](https://www.reuters.com/business/finance/global-markets-wrapup-1-2022-09-21/)"
    }
    ```
5.  Cliquez sur "Execute" et voyez le résultat !

### 2. Avec `curl` (depuis le terminal)

```bash
curl -X POST "[http://127.0.0.1:8000/analyze](http://127.0.0.1:8000/analyze)" \
-H "Content-Type: application/json" \
-d '{"url": "[https://www.reuters.com/business/finance/global-markets-wrapup-1-2022-09-21/](https://www.reuters.com/business/finance/global-markets-wrapup-1-2022-09-21/)"}'

### Auteur
Khalifa Ababacar DIALLO
