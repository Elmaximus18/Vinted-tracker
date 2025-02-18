import os
import requests
import logging
import time
from telegram import Bot

# 🔧 Configuration des variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
VINTED_SESSION = os.getenv("VINTED_SESSION")

# 🔍 Vérification des tokens
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ ERREUR : TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID non défini !")
    exit(1)

if not VINTED_SESSION:
    print("❌ ERREUR : VINTED_SESSION non défini !")
    exit(1)

# 🛠️ Initialisation du bot Telegram
bot = Bot(token=TELEGRAM_TOKEN)

# 📝 Liste des annonces déjà envoyées pour éviter les doublons
seen_items = set()

# 🚀 Fonction d'envoi de notification Telegram
def send_telegram_notification(message):
    """Envoie une notification Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print(f"✅ Message envoyé : {message}")
        else:
            print(f"❌ ERREUR - Envoi échoué (Code {response.status_code}) : {response.text}")

    except Exception as e:
        print(f"❌ ERREUR - Échec de l'envoi : {e}")

# 🔍 Fonction pour récupérer les annonces Vinted
def search_vinted():
    """Récupère les annonces PS1 à 10€ max depuis Vinted."""
    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": "PS1",
        "price_to": 10,
        "order": "newest_first",
        "per_page": 5
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Cookie": f"VINTED_SESSION={VINTED_SESSION}"
    }
    
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ {len(data.get('items', []))} annonces trouvées")
        return data.get("items", [])
    elif response.status_code == 401:
        print("❌ ERREUR - Authentification échouée, vérifie le cookie VINTED_SESSION.")
    elif response.status_code == 403:
        print("❌ ERREUR - Accès refusé, vérifie l'User-Agent ou le cookie.")
    else:
        print(f"❌ ERREUR - Code {response.status_code} : {response.text}")

    return []

# 🔄 Boucle principale du bot
if __name__ == "__main__":
    print("✅ Le bot tourne correctement !")

    while True:
        results = search_vinted()
        
        for item in results:
            item_id = item["id"]
            title = item["title"]
            price = item["price"]["amount"]
            url = f"https://www.vinted.fr{item['path']}"

            # Vérifie si l'annonce a déjà été envoyée
            if item_id not in seen_items:
                seen_items.add(item_id)
                message = f"🔥 Nouveau produit trouvé : {title}\n💰 Prix : {price}€\n🔗 Lien : {url}"
                send_telegram_notification(message)

        print("🔄 Fin du cycle, prochaine vérification dans 60 secondes...\n")
        time.sleep(60)  # Attendre 60 secondes avant de relancer la recherche
