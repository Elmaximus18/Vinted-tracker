import os
import requests
import logging
import time
from telegram import Bot

# Variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Vérification du Token
if TELEGRAM_TOKEN is None or TELEGRAM_TOKEN == "":
    print("❌ ERREUR : TELEGRAM_TOKEN est vide ou non défini !")
    exit(1)  # Arrête le script si le token est absent

print(f"✅ DEBUG - Token récupéré : {TELEGRAM_TOKEN}")  # Debug pour vérifier le token
bot = Bot(token=TELEGRAM_TOKEN)

# Fonction d'envoi de message
async def send_telegram_notification(message):
    """Envoie une notification Telegram."""
    try:
        print(f"✅ DEBUG - Envoi du message : {message}")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=data)
        print(f"✅ DEBUG - Réponse Telegram : {response.json()}")  # Voir la réponse exacte
    except Exception as e:
        print(f"❌ ERREUR - Échec de l'envoi : {e}")

# **Fonction de recherche sur Vinted avec une session persistante**
def search_vinted():
    """Scrape Vinted pour voir si un produit PS1 à 10€ max apparaît."""
    url = "https://www.vinted.fr/api/v2/search?q=PS1&price_to=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
    }

    session = requests.Session()
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ DEBUG - Résultats trouvés : {len(data.get('items', []))}")
        logging.info(f"✅ DEBUG - Résultats trouvés : {len(data.get('items', []))}")
        return data.get("items", [])
    else:
        print(f"❌ ERREUR - Impossible de récupérer les annonces (Code {response.status_code})")
        logging.error(f"❌ ERREUR - Impossible de récupérer les annonces (Code {response.status_code})")
        return []

# **Boucle principale qui surveille Vinted**
if __name__ == "__main__":
    print("✅ Le bot tourne correctement !")
    while True:
        results = search_vinted()
        
        for item in results:
            title = item.get("title", "Sans titre")
            price = item.get("price", "Inconnu")

            print(f"🔍 Produit trouvé : {title} - {price}€")
            
            if price and float(price) <= 10:
                send_telegram_notification(f"🔥 Nouveau produit : {title} - {price}€ !")

        print("🔄 Fin du cycle, prochaine vérification dans 60 secondes...")  
        time.sleep(60)  # Vérifie toutes les 60 secondes
