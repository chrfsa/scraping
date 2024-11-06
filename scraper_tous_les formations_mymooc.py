import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chemin vers geckodriver
s = Service("/snap/bin/geckodriver")
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
    sub_category_url = driver.find_element(By.XPATH, "//a[@title=\"Marketing\"]").get_attribute("href")
    driver.get(sub_category_url)
    time.sleep(3)

    # Liste pour stocker les liens des cours
    course_links = []

    # Cliquer sur "Voir plus de ressources" jusqu'à ce que le bouton disparaisse
    while True:
        try:
            # Attendre que les éléments de cours soient chargés
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ais-infinite-hits--item"))
            )

            
            # Chercher le bouton "Voir plus de ressources"
            try:
                load_more_button = driver.find_element(By.CLASS_NAME, "ais-infinite-hits--showmoreButton")
                load_more_button.click()
                time.sleep(2)  # Attendre le chargement des nouveaux éléments
            except NoSuchElementException:
                # Si le bouton n'est plus présent, sortir de la boucle
                break

        except Exception as e:
            print(f"Erreur lors du chargement des cours : {e}")
            break
    current_courses = driver.find_elements(By.CLASS_NAME, "ais-infinite-hits--item")
    current_course_links = [course.find_element(By.TAG_NAME, "a").get_attribute("href") for course in current_courses]
    course_links.extend(current_course_links)
    # Liste pour stocker les informations des cours
    courses_data = []

    # Boucle à travers chaque cours pour récupérer les informations
    for course_link in course_links:
        driver.get(course_link)
        time.sleep(3)

        # Extraire les informations de cours avec BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extraction des données spécifiques
        course_name = soup.find("h1", class_="mymoocapp-1qbrgns ejjtsdg6").get_text(strip=True) if soup.find("h1", class_="mymoocapp-1qbrgns ejjtsdg6") else "Non spécifié"
        site = soup.find("div", class_="source-from mymoocapp-15422f9 e2ogkr45").get_text(strip=True)
        duration = soup.find("span", class_="mymoocapp-edflexui-3v6sjc-label").get_text(strip=True) if soup.find("span", class_="mymoocapp-edflexui-3v6sjc-label") else "Non spécifié"
        rating = soup.find("span", class_="reviews-note").get_text(strip=True) if soup.find("span", class_="reviews-note") else "Non spécifié"

        # Intervenant
        intervenants_div = soup.find("div", class_="right mymoocapp-iclgu9 ebll6208")
        intervenants = "Non spécifié"
        if intervenants_div:
            try:
                intervenant = intervenants_div.find("strong").get_text(strip=True)
                if intervenant:
                    intervenants = intervenant
            except:
                pass

        # Éditeur
        editor_text = "Non spécifié"
        editor_section = soup.find("div", class_="mymoocapp-g0c3wn ebll6203")
        if editor_section:
            try:
                editor_div = editor_section.find("div", {"data-testid": "styled#rich-editorial##body"})
                if editor_div and editor_div.find("p"):
                    editor_text = editor_div.find("p").get_text(strip=True)
            except:
                pass

        # Ajouter les données du cours à la liste
        courses_data.append([category_title, "Marketing", course_name, site, duration, rating, intervenants, editor_text])

    # Enregistrer les données dans un fichier CSV
    with open("cours_mymooc2.csv", mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Catégorie", "Sous-catégorie", "Nom du cours", "site", "Durée", "Avis", "Intervenant", "Éditeur"])
        writer.writerows(courses_data)

finally:
    # Fermer le navigateur
    driver.quit()

print("Scraping terminé et données enregistrées dans 'cours_mymooc.csv'.")