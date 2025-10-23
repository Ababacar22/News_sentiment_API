import requests
from bs4 import BeautifulSoup
import logging
from transformers import pipeline
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta

# --- Configuration du Logging ---
# Configure un logging simple pour voir ce qui se passe
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- PARTIE 1 : LE SCRAPER ---
def scrape_article_text(url: str) -> str:
    """
    Scrape le texte principal (tous les paragraphes) d'une URL.
    """
    # On simule un navigateur pour éviter d'être bloqué (erreur 403)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    
    try:
        logger.info(f"Téléchargement de l'URL : {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        # Lève une erreur si la page n'est pas trouvée (ex: 404)
        response.raise_for_status()
        
        # On "parse" le HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # C'est notre stratégie simple : trouver TOUTES les balises <p>
        paragraphs = soup.find_all('p')
        
        # On joint tous les textes des paragraphes avec un espace
        article_text = ' '.join([p.get_text() for p in paragraphs])
        
        if not article_text.strip():
            logger.warning("Aucun texte trouvé dans les balises <p>.")
            return ""
            
        return article_text

    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête HTTP : {e}")
        return "" # Renvoie une chaîne vide en cas d'erreur


# --- PARTIE 2 : LE MODÈLE NLP ---
# On charge le modèle UNE SEULE FOIS au démarrage.
logger.info("Chargement du modèle de sentiment...")
sentiment_pipeline = None
LABEL_MAP = {}
try:
    # On charge le modèle pré-entraîné
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="cardiffnlp/twitter-roberta-base-sentiment"
    )
    
    # Ce modèle renvoie 'LABEL_0', 'LABEL_1', 'LABEL_2'.
    # On crée un dictionnaire pour les rendre lisibles.
    LABEL_MAP = {
        "LABEL_0": "negative",
        "LABEL_1": "neutral",
        "LABEL_2": "positive"
    }
    logger.info("Modèle NLP chargé avec succès.")
    
except Exception as e:
    logger.error(f"Erreur fatale lors du chargement du modèle NLP : {e}")


# --- PARTIE 3 : L'API ---
# 1. On crée l'application FastAPI
app = FastAPI(
    title="News Sentiment API",
    description="Une API pour scraper et analyser le sentiment d'articles.",
    version="1.0"
)

# 2. On définit les "schémas" de données (entrée et sortie)
class AnalyzeRequest(BaseModel):
    url: HttpUrl  # Pydantic valide que c'est une URL valide !

class AnalyzeResponse(BaseModel):
    url: str
    sentiment: str
    score: float
    from_cache: bool = False # Pour voir si ça vient du cache

# --- PARTIE 4 : LOGIQUE DE CACHE ---
CACHE_STORE = {} # Notre cache en mémoire
CACHE_EXPIRATION = timedelta(minutes=60) # On garde les résultats 1 heure


# 3. On crée le point de terminaison (endpoint)
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_sentiment_endpoint(request: AnalyzeRequest):
    """
    Analyse le sentiment d'un article à partir de son URL.
    """
    if sentiment_pipeline is None:
        # Si le modèle n'a pas chargé, on renvoie une erreur 503
        raise HTTPException(status_code=503, detail="Service Indisponible: Modèle NLP non chargé.")

    url_str = str(request.url)

    # --- VÉRIFIER LE CACHE D'ABORD ---
    current_time = datetime.now()
    if url_str in CACHE_STORE:
        cached_data = CACHE_STORE[url_str]
        # Vérifier si le cache n'a pas expiré
        if current_time < cached_data["expiry_time"]:
            logger.info(f"RÉPONSE DU CACHE pour : {url_str}")
            # On met à jour 'from_cache' à True avant de renvoyer
            cached_response = cached_data["response"]
            cached_response.from_cache = True
            return cached_response # On renvoie directement
        else:
            logger.info(f"Cache expiré pour : {url_str}")
            # Le cache a expiré, on le supprime
            del CACHE_STORE[url_str]
    
    # --- SI PAS DANS LE CACHE (ou expiré), on fait le travail ---
    logger.info(f"Nouvelle requête (non-cachée) pour : {url_str}")
    
    # Étape 1 : Scraper
    article_text = scrape_article_text(url_str)
    
    if not article_text:
        # Si le scraping échoue, on renvoie une erreur 422
        raise HTTPException(status_code=422, detail="Impossible d'extraire le contenu de l'article.")
            
    # Étape 2 : Analyser
    try:
        # On tronque le texte pour le modèle (limite de 512 tokens)
        truncated_text = article_text[:1024] # 1024 char ~= 512 tokens
        
        logger.info("Analyse du sentiment en cours...")
        result = sentiment_pipeline(truncated_text)[0]
        
        sentiment_label = LABEL_MAP.get(result['label'], result['label'])
        sentiment_score = result['score']

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse NLP : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de l'analyse.")

    # Étape 3 : Créer la réponse ET la stocker dans le cache
    response = AnalyzeResponse(
        url=url_str,
        sentiment=sentiment_label,
        score=sentiment_score,
        from_cache=False # C'est une nouvelle réponse
    )
    
    # On stocke la réponse et sa date d'expiration
    CACHE_STORE[url_str] = {
        "response": response,
        "expiry_time": current_time + CACHE_EXPIRATION
    }
    
    return response

# Un point de terminaison "racine" pour vérifier que l'API est en ligne
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API d'analyse de sentiment. Utilisez le endpoint POST /analyze"}