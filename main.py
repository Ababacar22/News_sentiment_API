import requests
from bs4 import BeautifulSoup
import logging
from transformers import pipeline  # <-- NOUVEL IMPORT


# Configure un logging simple pour voir ce qui se passe
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


# --- BLOC DE TEST POUR L'ÉTAPE 1 ---
# Ce code ne s'exécute que lorsque vous lancez "python main.py"
#if __name__ == "__main__":

    # Article en anglais, pour notre futur modèle
   #test_url = "https://www.bbc.com/news/articles/cd6758pn6ylo" 

    #print("--- TEST DU SCRAPER ---")
    #text = scrape_article_text(test_url)

    #if text:
        #print(f"Succès ! Texte extrait (longueur : {len(text)} caractères).")
        #print("\nAPERÇU (500 premiers caractères) :")
        #print(text[:500] + "...")
    #else:
        #print("Échec de l'extraction du texte.")

# --- PARTIE 2 : LE MODÈLE NLP ---
# (Cette section est nouvelle)
logger.info("Chargement du modèle de sentiment (cela peut prendre un moment)...")
sentiment_pipeline = None
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


# --- BLOC DE TEST POUR L'ÉTAPE 2 ---
# (Nous modifions ce bloc)
if __name__ == "__main__":

    # Utilisez l'URL qui a fonctionné pour vous
    test_url = "https://www.bbc.com/afrique/articles/cp8nem0k53ro#:~:text=Certaines%20personnes%20sont%20n%C3%A9es%20pour,qui%20nous%20arrive%20tout%20seul." 

    print("\n--- TEST COMBINÉ (SCRAPER + NLP) ---")

    # Étape 1 : Scraper le texte
    text = scrape_article_text(test_url)

    # Étape 2 : Analyser le sentiment (si les 2 étapes ont réussi)
    if text and sentiment_pipeline:
        # IMPORTANT : Les modèles ont une limite de taille (souvent 512 "mots").
        # On ne lui donne que les 1024 premiers caractères pour éviter une erreur.
        truncated_text = text[:1024]

        logger.info("Analyse du sentiment en cours...")
        # Le modèle renvoie une liste de résultats, on prend le premier [0]
        result = sentiment_pipeline(truncated_text)[0]

        sentiment_label = LABEL_MAP.get(result['label'], result['label'])
        sentiment_score = result['score']

        print("\n--- RÉSULTAT DE L'ANALYSE ---")
        print(f"Sentiment: {sentiment_label}")
        print(f"Score de confiance: {sentiment_score:.4f}")

    elif not text:
        print("Échec du scraping. Test NLP annulé.")
    else:
        print("Échec du chargement du modèle NLP. Test annulé.")