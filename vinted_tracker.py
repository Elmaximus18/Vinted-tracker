import os
import requests
import time
from telegram import Bot

# Variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Vérification du Token
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERREUR : TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID non défini !")
    exit(1)

print(f"✅ DEBUG - Token récupéré : {TELEGRAM_TOKEN}")
bot = Bot(token=TELEGRAM_TOKEN)

# Fonction d'envoi de message sur Telegram
def send_telegram_notification(message):
    """Envoie une notification Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=data)
        print(f"✅ DEBUG - Réponse Telegram : {response.json()}")
    except Exception as e:
        print(f"❌ ERREUR - Envoi échoué : {e}")

# Fonction de recherche sur Vinted via API
def search_vinted():
    """Interroge l'API de Vinted pour récupérer des annonces."""
    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": "PS1",
        "price_to": 10,
        "per_page": 5,  # Nombre d'annonces à récupérer
        "order": "newest_first"
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])

        if items:
            print(f"✅ DEBUG - {len(items)} annonces trouvées")
            return items
        else:
            print("ℹ️ DEBUG - Aucune annonce trouvée.")
            return []
    else:
        print(f"❌ ERREUR - Impossible d'accéder aux annonces (Code {response.status_code})")
        return []

# Boucle principale
if __name__ == "__main__":
    print("✅ Le bot tourne correctement !")
    while True:
        results = search_vinted()
        
        for item in results:
            title = item.get("title", "Sans titre")
            price = item.get("price", {}).get("amount", "Inconnu")
            link = f"https://www.vinted.fr/items/{item.get('id')}"

            print(f"🔍 Produit trouvé : {title} - {price}€ ({link})")
            
            if price and float(price) <= 10:
                send_telegram_notification(f"🔥 Nouveau produit : {title} - {price}€ !\n🔗 {link}")

        print("🔄 Fin du cycle, prochaine vérification dans 60 secondes...")  
        time.sleep(60)  # Vérifie toutes les 60 secondes
