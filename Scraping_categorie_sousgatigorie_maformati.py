import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup

# Chemin vers geckodriver
s = Service("/snap/bin/geckodriver")  # Assurez-vous que le chemin vers geckodriver est correct
driver = webdriver.Firefox(service=s)

# URL de la page à scraper
url = "https://www.maformation.fr/en-ligne?utm_source=google&utm_medium=cpc&utm_campaign=19908456149&utm_term=149008481233&utm_content=my%20mooc&gad_source=1&gclid=Cj0KCQjwpvK4BhDUARIsADHt9sQsOcbTKBxoXImRYz6hvJpAI4i2s9fr8zyeKkKufn-PZg5vyYtLE5IaApP7EALw_wcB"

# Ouvrir la page
driver.get(url)
time.sleep(2)  # Attendre que la page charge

# Cliquer sur "Toutes les catégories" pour afficher le menu complet
try:
    toutes_categories = driver.find_element(By.XPATH, "//div[contains(@class, 'hyperlink-tag__content') and contains(., 'Toutes les catégories')]")
    toutes_categories.click()
    time.sleep(2)  # Attendre que le menu charge
except Exception as e:
    print("Erreur lors du clic sur 'Toutes les catégories':", e)
    driver.quit()

# Préparer les données à écrire dans le CSV
data = []

# Parcourir chaque catégorie principale et ses sous-catégories
while True:
    try:
        # Trouver toutes les catégories principales de nouveau après chaque retour
        categories = driver.find_elements(By.CSS_SELECTOR, '[data-cy="xxl-menu-category-item"]')

        # Parcourir chaque catégorie par son index pour éviter des erreurs de StaleElementReference
        for i in range(len(categories)):
            # Recharger les éléments de catégorie après chaque retour
            categories = driver.find_elements(By.CSS_SELECTOR, '[data-cy="xxl-menu-category-item"]')
            category = categories[i]  # Sélectionner l'élément par index

            # Récupérer le nom de la catégorie principale
            category_title = category.find_elements(By.TAG_NAME, "span")[0].text.strip()

            # Cliquer sur la catégorie principale
            category.click()
            time.sleep(2)

            # Extraire le titre de la catégorie affichée
            displayed_category_title = driver.find_element(By.CSS_SELECTOR, '[data-cy="xxl-menu-category-title"]').text.strip()

            # Vérifier que le titre affiché correspond au titre attendu
            if displayed_category_title != category_title:
                print(f"Mismatch dans le titre de la catégorie: {displayed_category_title} vs {category_title}")
            
            # Récupérer toutes les sous-catégories
            sous_categories = driver.find_elements(By.CSS_SELECTOR, 'span')
            sous_categories_texts = [sous_cat.text.strip() for sous_cat in sous_categories if sous_cat.text.strip()]

            # Ajouter les données pour la catégorie et ses sous-catégories
            for sous_categorie in sous_categories_texts:
                data.append([category_title, sous_categorie])

            # Revenir en arrière pour la liste des catégories
            retour = driver.find_element(By.CSS_SELECTOR, '[data-cy="xxl-menu-btn-back"]')
            driver.execute_script("arguments[0].click();", retour)  # Utiliser JavaScript pour le clic retour
            time.sleep(2)

    except Exception as e:
        print("Erreur lors du traitement d'une catégorie:", e)
        break  # Arrêter la boucle si une erreur survient

# Écrire les résultats dans un fichier CSV
with open('categories_sous_categories_maformation.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Catégorie', 'Sous-catégorie'])  # En-têtes
    writer.writerows(data)  # Contenu

print("Les données ont été enregistrées dans categories_sous_categories.csv avec succès.")

# Fermer le navigateur
driver.quit()
