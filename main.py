import os
import pandas as pd
import threading
import ctypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

# Configurer les logs pour déboguer facilement
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration pour empêcher la mise en veille de l'ordinateur
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

# Définir le chemin vers le chromedriver
service = Service('src/include/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service)

# Charger les mots depuis le fichier CSV
file_path = 'src/include/library/words.csv'
if os.path.exists(file_path):
    df = pd.read_csv(file_path, header=None, names=["word"])
    words = df["word"].tolist()
    logging.info(f"Nombre de mots chargés depuis le fichier: {len(words)}")
else:
    logging.error(f"Le fichier dictionnaire '{file_path}' est introuvable.")
    driver.quit()
    exit()

# Fonction de test d'un mot
def test_word(word, driver, search_box, lock):
    try:
        with lock:  # Verrouiller pour éviter les conflits d'accès avec Selenium
            logging.info(f"Testing word: {word}")
            search_box.clear()
            search_box.send_keys(str(word))
            search_box.send_keys(Keys.RETURN)

        # Attendre un bref instant pour permettre à la page de se mettre à jour
        time.sleep(0.3)

        # Vérifier si le mot est rejeté (présence du message d'erreur)
        element_error = driver.find_element(By.ID, "pedantix-error")
        if "Je ne trouve pas le mot" in element_error.text:
            with lock:
                # Supprimer le mot du CSV car il est incorrect
                words.remove(word)
                logging.info(f"Mot rejeté et supprimé: {word}")

    except Exception as e:
        logging.error(f"Erreur lors du test du mot '{word}': {e}")

# Accéder à la page
try:
    driver.get("https://cemantix.certitudes.org/pedantix")

    # Accepter les cookies et les règles si présents
    buttonCookie = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "fc-button-label"))
    )
    buttonCookie.click()

    buttonRule = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "dialog-close"))
    )
    buttonRule.click()

    # Localiser les éléments une seule fois
    search_box = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "pedantix-guess"))
    )

    lock = threading.Lock()
    threads = []

    # Utiliser plusieurs threads pour tester les mots plus rapidement
    for word in words:
        thread = threading.Thread(target=test_word, args=(word, driver, search_box, lock))
        thread.start()
        threads.append(thread)

        # Limiter le nombre de threads actifs pour éviter une surcharge
        if len(threads) >= 10:
            for t in threads:
                t.join()
            threads = []

    # Attendre que tous les threads terminent
    for t in threads:
        t.join()

    # Enregistrer les mots restants dans le fichier CSV
    pd.DataFrame({"word": words}).to_csv(file_path, index=False, header=False)
    logging.info(f"Processus terminé, mots mis à jour.")

except Exception as e:
    logging.error(f"Erreur: {e}")

finally:
    # Réinitialiser l'état de mise en veille du système
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)

    driver.quit()
