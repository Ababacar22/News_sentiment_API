import requests
from bs4 import BeautifulSoup
import logging

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
if __name__ == "__main__":

    # Article en anglais, pour notre futur modèle
    test_url = "https://www.bbc.com/news/articles/cd6758pn6ylo" 

    print("--- TEST DU SCRAPER ---")
    text = scrape_article_text(test_url)

    if text:
        print(f"Succès ! Texte extrait (longueur : {len(text)} caractères).")
        print("\nAPERÇU (500 premiers caractères) :")
        print(text[:500] + "...")
    else:
        print("Échec de l'extraction du texte.")