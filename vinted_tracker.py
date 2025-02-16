import os
import requests
import time
from telegram import Bot

# Variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
VINTED_SESSION = os.getenv("VINTED_SESSION")  # Récupération du cookie de session

# Vérification des variables d'environnement
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID or not VINTED_SESSION:
    print("❌ ERREUR : Une variable d'environnement est manquante !")
    exit(1)

print(f"✅ DEBUG - Token récupéré : {TELEGRAM_TOKEN}")
print(f"✅ DEBUG - Session Vinted récupérée : {VINTED_SESSION[:10]}...")  # Vérification du cookie

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

# Fonction de test de l'authentification Vinted
def test_vinted_auth():
    """Teste si le cookie de session permet d'accéder à Vinted."""
    url = "https://www.vinted.fr/api/v2/users/me"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": f"_vinted_session={VINTED_SESSION}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("✅ DEBUG - Authentification réussie avec le cookie Vinted !")
        print(f"Réponse : {response.json()}")
        return True
    else:
        print(f"❌ ERREUR - Le cookie est invalide (Code {response.status_code})")
        return False

# Fonction de recherche sur Vinted via API
def search_vinted():
    """Interroge l'API de Vinted pour récupérer des annonces en simulant un utilisateur connecté."""
    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": "PS1",
        "price_to": 10,
        "per_page": 5,  # Nombre d'annonces à récupérer
        "order": "newest_first"
    }
    
    # Ajouter un User-Agent et le cookie Vinted pour éviter l'erreur 401
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Cookie": f"_vinted_session={VINTED_SESSION}"
    }

    response = requests.get(url, params=params, headers=headers)
    
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

    # Test d'authentification avant de chercher des annonces
    if not test_vinted_auth():
        print("❌ ERREUR - Authentification échouée, vérifie le cookie VINTED_SESSION.")
        exit(1)

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
