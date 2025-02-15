import requests
import time
import logging
from telegram import Bot
import os

# Variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
VINTED_URL = os.getenv("VINTED_URL")
CHECK_INTERVAL = 60  # Vérification toutes les 60 secondes

# Initialisation du bot Telegram
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

if TELEGRAM_TOKEN is None or TELEGRAM_TOKEN == "":
    print("❌ ERREUR : TELEGRAM_TOKEN est vide ou non défini !")
    exit(1)  # Arrête le script si le token est absent

print(f"✅ DEBUG - Token récupéré : {TELEGRAM_TOKEN}")  # Debug pour vérifier le token
bot = Bot(token=TELEGRAM_TOKEN)

# Configuration des logs
logging.basicConfig(
    filename="vinted_tracker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_vinted_product():
    """Récupère les informations du produit Vinted."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(VINTED_URL, headers=headers)
        response.raise_for_status()
        
        if "price" in response.text:
            price = extract_price(response.text)
            return price
        else:
            return None
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des données Vinted : {e}")
        return None

def extract_price(html_content):
    """Extrait le prix depuis le HTML de la page."""
    import re
    match = re.search(r'"price":(\d+\.\d+)', html_content)
    if match:
        return float(match.group(1))
    return None

def send_telegram_notification(message):
    """Envoie une notification Telegram."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logging.info(f"Notification envoyée : {message}")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi du message Telegram : {e}")

if __name__ == "__main__":
    last_price = None
    while True:
        current_price = get_vinted_product()
        if current_price is not None and (last_price is None or current_price < last_price):
            send_telegram_notification(f"🛍️ Nouveau prix détecté sur Vinted : {current_price}€ !")
            last_price = current_price
        time.sleep(CHECK_INTERVAL)
