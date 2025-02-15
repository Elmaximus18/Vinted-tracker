import os
import requests
import logging
import time
import subprocess
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

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

# **Télécharger Chrome et WebDriver manuellement**
def setup_chrome():
    """Télécharge et configure Chrome et WebDriver pour Railway."""
    print("🔧 Téléchargement de Chrome et WebDriver...")
    os.makedirs("/tmp/chrome", exist_ok=True)

    # Télécharger Chrome
    subprocess.run("wget -q -O /tmp/chrome/chrome-linux.zip https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb", shell=True)
    subprocess.run("dpkg -x /tmp/chrome/chrome-linux.zip /tmp/chrome/", shell=True)

    # Télécharger le WebDriver
    subprocess.run("wget -q -O /tmp/chrome/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip", shell=True)
    subprocess.run("unzip /tmp/chrome/chromedriver.zip -d /tmp/chrome/", shell=True)

    print("✅ Chrome et WebDriver configurés.")

# **Fonction de recherche sur Vinted avec Selenium**
def search_vinted():
    """Scrape Vinted en simulant un vrai navigateur avec Selenium."""
    setup_chrome()  # Installation de Chrome avant l'exécution

    url = "https://www.vinted.fr/catalog?search_text=PS1&price_to=10"

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920x1080")
    options.binary_location = "/tmp/chrome/opt/google/chrome/chrome"

    service = Service("/tmp/chrome/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    driver.implicitly_wait(5)

    try:
        items = driver.find_elements(By.CLASS_NAME, "feed-grid__item")
        results = []

        for item in items:
            try:
                title = item.find_element(By.TAG_NAME, "h2").text.strip()
                price = item.find_element(By.CLASS_NAME, "currency-positive").text.strip().replace("€", "").replace(",", ".")
                link = item.find_element(By.TAG_NAME, "a").get_attribute("href")

                print(f"✅ Produit trouvé : {title} - {price}€ ({link})")
                results.append({"title": title, "price": price, "link": link})
            except Exception:
                continue

        driver.quit()
        return results

    except Exception as e:
        print(f"❌ ERREUR - Impossible de récupérer les annonces : {e}")
        driver.quit()
        return []

# **Boucle principale qui surveille Vinted**
if __name__ == "__main__":
    print("✅ Le bot tourne correctement !")
    while True:
        results = search_vinted()
        
        for item in results:
            title = item.get("title", "Sans titre")
            price = item.get("price", "Inconnu")
            link = item.get("link", "#")

            print(f"🔍 Produit trouvé : {title} - {price}€ ({link})")
            
            if price and float(price) <= 10:
                send_telegram_notification(f"🔥 Nouveau produit : {title} - {price}€ !\n🔗 {link}")

        print("🔄 Fin du cycle, prochaine vérification dans 60 secondes...")  
        time.sleep(60)  # Vérifie toutes les 60 secondes
