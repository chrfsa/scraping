import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup

# Chemin vers geckodriver
s = Service("/snap/bin/geckodriver")  # Assurez-vous que le chemin vers geckodriver est correct
driver = webdriver.Firefox(service=s)


# URL de base
base_url = "https://www.my-mooc.com/fr/categorie/"

try:
    # Accéder à la page de catégorie principale
    driver.get(base_url)
    time.sleep(3)  # Attendre le chargement de la page

    # Sélectionner la catégorie "Développement professionnel"
    category_title = "Développement professionnel"
    category_element = driver.find_element(By.XPATH, f"//h2[contains(text(), '{category_title}')]")
    category_element.location_once_scrolled_into_view
    time.sleep(1)

    # Sélectionner la sous-catégorie "Gestion d'entreprise"
    sub_category_url = driver.find_element(By.XPATH, "//a[@title=\"Gestion d'entreprise\"]").get_attribute("href")
    driver.get(sub_category_url)
    time.sleep(3)

    # Accéder au premier cours de la sous-catégorie
    course_element = driver.find_element(By.CLASS_NAME, "ais-infinite-hits--item")
    course_link = course_element.find_element(By.TAG_NAME, "a").get_attribute("href")
    driver.get(course_link)
    time.sleep(3)

    # Extraire les informations de cours avec BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Extraction des données spécifiques
    course_name = soup.find("h1", class_="mymoocapp-1qbrgns ejjtsdg6").get_text(strip=True) if soup.find("h1", class_="mymoocapp-1qbrgns ejjtsdg6") else "Non spécifié"
    duration = soup.find("span", class_="mymoocapp-edflexui-3v6sjc-label").get_text(strip=True) if soup.find("span", class_="mymoocapp-edflexui-3v6sjc-label") else "Non spécifié"
    rating = soup.find("span", class_="reviews-note").get_text(strip=True) if soup.find("span", class_="reviews-note") else "Non spécifié"

    # Intervenant
    intervenants_div = soup.find("div", class_="right mymoocapp-iclgu9 ebll6208")  # Cibler la div "right"

    if intervenants_div:
        intervenant = intervenants_div.find("strong").get_text(strip=True) if intervenants_div and intervenants_div.find("strong") else "Non spécifié"
    else:
        intervenant = "Non spécifié"

    # Éditeur
    editor_section = soup.find("div", class_="mymoocapp-g0c3wn ebll6203")
    if editor_section:
        editor_div = editor_section.find("div", {"data-testid": "styled#rich-editorial##body"})
        editor_text = editor_div.find("p").get_text(strip=True) if editor_div and editor_div.find("p") else "Non spécifié"
    else:
        editor_text = "Non spécifié"

    
    # Enregistrer les données dans un fichier CSV
    with open("cours_mymooc.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Catégorie", "Sous-catégorie", "Nom du cours", "Durée", "Avis", "Intervenant", "Éditeur"])
        writer.writerow([category_title, "Gestion d'entreprise", course_name, duration, rating, intervenant, editor_text])

finally:
    # Fermer le navigateur
    driver.quit()

print("Scraping terminé et données enregistrées dans 'cours_mymooc.csv'.")
