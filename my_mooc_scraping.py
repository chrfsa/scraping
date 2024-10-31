import requests
from bs4 import BeautifulSoup
import csv

# URL de la page à scraper
url = "https://www.my-mooc.com/fr/categorie/"

# Envoyer la requête pour obtenir le HTML de la page
response = requests.get(url)

# Vérifier que la requête a réussi
if response.status_code == 200:
    # Initialiser BeautifulSoup pour parser le HTML
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Supprimer les balises <script> et <style>
    for script in soup(["script", "style"]):
        script.decompose()  # Supprime la balise du DOM

    # Trouver la catégorie principale
    categories = soup.find_all("div", class_="category__children__item")
    
    # Préparer les données à écrire dans le CSV
    data = []

    # Parcourir chaque catégorie
    for category in categories:
        # Récupérer le titre de la catégorie
        category_title = category.find("h2", class_="category__children__title").get_text(strip=True)
        
        # Trouver les sous-catégories
        subcategories = category.find_all("div", class_="category__sub-children__item")
        
        # Extraire les titres des sous-catégories
        subcategory_titles = [subcat.get_text(strip=True) for subcat in subcategories]

        # Ajouter les données à la liste
        for subcat in subcategory_titles:
            data.append([category_title, subcat])

    # Écrire dans le fichier CSV
    with open('categories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Category', 'Subcategory'])  # Écrire l'en-tête
        writer.writerows(data)  # Écrire les données

    print("Les données ont été écrites dans categories.csv avec succès.")
else:
    print(f"Erreur: Impossible de récupérer la page, code d'erreur {response.status_code}")
