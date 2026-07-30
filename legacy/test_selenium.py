#pip install webdriver_manager
#pip install selenium
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# Setup Chrome options
options = webdriver.ChromeOptions() 

# Setup the Chrome driver
driver =webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
driver.get("https://www.linkedin.com/")
driver.implicitly_wait(5)

username = driver.find_element(By.ID,"session_key") 
username.send_keys("REDACTED")
time.sleep(3)

pword =driver.find_element(By.ID,"session_password")
pword.send_keys("REDACTED")
time.sleep(3)

sign_in_button = driver.find_element(By.XPATH,'//*[@type="submit"]')

sign_in_button.click()
time.sleep(25)


def collecter_liens_logos(section):
    """
    Fonction pour collecter les liens des logos à partir d'une section donnée.
    """
    logo_links = []

    # Récupérer toutes les balises li dans la section "experience"
    experience_list_items = section.find_elements(By.XPATH, ".//div[contains(@class, 'pvs-list__outer-container')]//ul//li")

    # Parcourir chaque élément de la liste dans la section "experience"
    for item in experience_list_items:
        # Récupérer le lien du logo de l'entreprise
        try:
            logo_link = item.find_element(By.XPATH, ".//a[@data-field='experience_company_logo']").get_attribute("href")
            # Ajouter le lien à la liste
            logo_links.append(logo_link)
        except:
            # Gérer les cas où la balise a[data-field='experience_company_logo'] n'est pas présente
            pass

    return logo_links

driver.get("https://www.linkedin.com/in/sarah-rajaobelison-5819876a/") 
time.sleep(5)

# Récupérer la section unique qui contient un div avec l'identifiant "experience"
section = driver.find_element(By.XPATH, "//main//section[.//div[@id='experience']]")

# Collecter les liens des logos à partir de cette section
logo_links = collecter_liens_logos(section)

# Afficher les liens des logos
print("Liens des logos des entreprises:")
for link in logo_links:
    print(link)

driver.quit()

