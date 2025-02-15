import os
import requests
import logging
import time
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

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

# **Fonction de recherche sur Vinted avec Selenium**
def search_vinted():
    """Scrape Vinted en ouvrant une page avec Selenium pour contourner les blocages."""
    url = "https://www.vinted.fr/catalog?search_text=PS1&price_to=10"

    # Configuration de Selenium avec un WebDriver Chrome
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Exécuter sans interface graphique
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Ouvrir la page et récupérer les annonces
    driver.get(url)
    driver.implicitly_wait(5)  # Attendre le chargement des éléments

    items = driver.find_elements(By.CLASS_NAME, "feed-grid__item")

    results = []
    for item in items:
        try:
            title = item.find_element(By.TAG_NAME, "h2").text.strip()
            price = item.find_element(By.CLASS_NAME, "currency-positive").text.strip().replace("€", "").replace(",", ".")
            print(f"✅ Produit trouvé : {title} - {price}€")
            results.append({"title": title, "price": price})
        except Exception:
            continue  # Si une annonce est mal formatée, on l'ignore

    driver.quit()
    return results

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
