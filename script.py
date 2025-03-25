from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

dossier_resultats = input("Nom du dossier de résultats : ").strip()

# Configurer Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

with open("assets/categories.txt", "r", encoding="utf-8") as f:
    categories = [line.strip() for line in f if line.strip()]

os.makedirs(dossier_resultats, exist_ok=True)

# Ville hardcodée
ville = "75001+-+Paris+1er+Arrondissement&loc=2.3359%2C48.862"


for categorie in categories:
    cat_encoded = (
        categorie.replace(" ", "+")
                .replace("/", "%2F")
                .replace(":", "%3A")
                .replace(",", "%2C")
                .replace("'", "%27")
    )
    
    url = f"https://france-renov.gouv.fr/annuaire-rge/recherche?localisation={ville}&distance=50&type={cat_encoded}"
    print(f"Traitement de : {categorie}")
    print(f"URL : {url}")
    
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".fr_company-container"))
        )
    except:
        print(f"Aucun résultat visible pour {categorie} après attente.")

    entreprises = driver.find_elements(By.CSS_SELECTOR, ".fr_company-container")
    resultats = []

    for e in entreprises:
        try:
            nom = e.find_element(By.TAG_NAME, "h3").text.strip()
            email = e.find_element(By.CSS_SELECTOR, "a[href^='mailto:']").get_attribute("href").replace("mailto:", "").strip()
            telephone = e.find_element(By.CSS_SELECTOR, "a[href^='tel:']").get_attribute("href").replace("tel:", "").strip()
            resultats.append(f"{nom};{email};{telephone}")
        except:
            continue

    # Fichier de sortie
    nom_fichier_sanitized = categorie.replace(' ', '_').replace('/', '_').replace(':', '_').replace(',', '_').replace("'", "_")
    nom_fichier = f"Paris__{nom_fichier_sanitized}.txt"
    with open(os.path.join(dossier_resultats, nom_fichier), "w", encoding="utf-8") as f:
        for ligne in resultats:
            f.write(ligne + "\n")

    print(f"{len(resultats)} résultats enregistrés dans {nom_fichier}")

driver.quit()
print("Terminé.")