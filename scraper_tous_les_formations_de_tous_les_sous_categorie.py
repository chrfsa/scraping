import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Liste de toutes les sous-catégories
SOUS_CATEGORIES = [ 
    "Éducation en ligne",
"Préparation d'examen"







]

# Chemin vers geckodriver
s = Service("/snap/bin/geckodriver")

def scrape_subcategory(driver, base_url, category_title, sous_categorie):
    try:
        driver.get(base_url)
        time.sleep(3)

        try:
            sous_category_element = driver.find_element(By.XPATH, f'//a[contains(@title, "{sous_categorie}")]')
            sous_category_url = sous_category_element.get_attribute("href")
            driver.get(sous_category_url)
            time.sleep(3)
        except Exception as e:
            print(f"Erreur lors de la sélection de la sous-catégorie {sous_categorie}: {e}")
            return []

        course_links = []
        while True:
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ais-infinite-hits--item"))
                )
                try:
                    load_more_button = driver.find_element(By.CLASS_NAME, "ais-infinite-hits--showmoreButton")
                    if load_more_button.is_displayed() and load_more_button.is_enabled():
                        load_more_button.click()
                        time.sleep(2)
                    else:
                        break
                except (NoSuchElementException, ElementNotInteractableException):
                    break
            except Exception as e:
                print(f"Erreur lors du chargement des cours pour {sous_categorie}: {e}")
                break

        current_courses = driver.find_elements(By.CLASS_NAME, "ais-infinite-hits--item")
        current_course_links = [course.find_element(By.TAG_NAME, "a").get_attribute("href") for course in current_courses]
        course_links.extend(current_course_links)

        courses_data = []
        for course_link in course_links:
            driver.get(course_link)
            time.sleep(3)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Vérification de la page introuvable
            if soup.find("h2", class_="mymoocapp-7dvx9c-title"):
                print(f"Page introuvable pour le cours {course_link}. Passage au cours suivant.")
                continue

            course_name_tag = soup.find("h1", class_="mymoocapp-1qbrgns ejjtsdg6")
            course_name = course_name_tag.get_text(strip=True) if course_name_tag else "Non spécifié"

            site_tag = soup.find("div", class_="source-from mymoocapp-15422f9 e2ogkr45")
            site = site_tag.get_text(strip=True) if site_tag else "Non spécifié"

            duration_tag = soup.find("span", class_="mymoocapp-edflexui-3v6sjc-label")
            duration = duration_tag.get_text(strip=True) if duration_tag else "Non spécifié"

            rating_tag = soup.find("span", class_="reviews-note")
            rating = rating_tag.get_text(strip=True) if rating_tag else "Non spécifié"

            intervenants_div = soup.find("div", class_="right mymoocapp-iclgu9 ebll6208")
            intervenants = "Non spécifié"
            if intervenants_div:
                try:
                    intervenant = intervenants_div.find("strong")
                    intervenants = intervenant.get_text(strip=True) if intervenant else "Non spécifié"
                except:
                    pass

            editor_text = "Non spécifié"
            editor_section = soup.find("div", class_="mymoocapp-g0c3wn ebll6203")
            if editor_section:
                try:
                    editor_div = editor_section.find("div", {"data-testid": "styled#rich-editorial##body"})
                    if editor_div and editor_div.find("p"):
                        editor_text = editor_div.find("p").get_text(strip=True)
                except:
                    pass

            courses_data.append([category_title, sous_categorie, course_name, site, duration, rating, intervenants, editor_text])

        return courses_data

    except Exception as e:
        print(f"Erreur générale pour {sous_categorie}: {e}")
        return []

def main():
    base_url = "https://www.my-mooc.com/fr/categorie/"
    category_title = "Education et enseignement"
    driver = webdriver.Firefox(service=s)

    try:
        all_courses_data = []
        for sous_categorie in SOUS_CATEGORIES:
            print(f"Scraping de la sous-catégorie : {sous_categorie}")
            sous_category_courses = scrape_subcategory(driver, base_url, category_title, sous_categorie)
            all_courses_data.extend(sous_category_courses)
            print(f"Nombre de cours pour {sous_categorie} : {len(sous_category_courses)}")

        with open("cours_mymooc_all_subcategories3.csv", mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Catégorie", "Sous-catégorie", "Nom du cours", "site", "Durée", "Avis", "Intervenant", "Éditeur"])
            writer.writerows(all_courses_data)

        print(f"Scraping terminé. Total des cours : {len(all_courses_data)}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
