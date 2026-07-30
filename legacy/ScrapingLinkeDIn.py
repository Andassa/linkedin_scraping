from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import pandas as pd
import re
import random
class ScrapingLinkeDIn :
    @staticmethod
    def hello(file):
        df = pd.read_excel(file)
        print(df)
        return 'ok'
    
    @staticmethod
    def loginLinkeDIn(driverParms:webdriver,usernameParms,passwordParms):
        """
        Login on LinkedIn.

        Parameters:
        driverParms (webdriver): The webdriver instance.
        usernameParms (str): The username for LinkedIn.
        passwordParms (str): The password for LinkedIn.

        Returns:
        str: An empty string.
        """
        driverParms.get("https://www.linkedin.com/")
        WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.ID, "session_key")))

        username = driverParms.find_element(By.ID,"session_key") 
        username.send_keys(usernameParms)

        time.sleep(2)

        pword =driverParms.find_element(By.ID,"session_password")
        pword.send_keys(passwordParms)

        time.sleep(2)
        sign_in_button = driverParms.find_element(By.XPATH,'//*[@type="submit"]')
       
        return  sign_in_button.click()    

    @staticmethod
    def search_people_with_link_and_return_section(driverParms:webdriver,linkParms):
        """
        Search people on LinkedIn with link.

        Parameters:
        driverParms (webdriver): The webdriver instance.
        linkParms (str): The link to the LinkedIn profile.

        Returns section 
        """
        driverParms.get(linkParms) 
        WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.XPATH, "//main//section[.//div[@id='experience']]")))
        return driverParms.find_element(By.XPATH, "//main//section[.//div[@id='experience']]")
    
    @staticmethod
    def collecter_liens_logos(section):
        """
        Collect logo links from a given section.

        Parameters:
        section (WebElement): The section element to collect logo links from.

        Returns:
        list: A list of logo links.
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
            except Exception as e:
                # Gérer les cas où la balise a[data-field='experience_company_logo'] n'est pas présente
                print(f"Une exception a été levée : {e}")
                pass

        return logo_links

    @staticmethod
    def process_excel_file(driverParms:webdriver, file_name:str):
        """
        Process an Excel file to search people on LinkedIn and store logo links.

        Parameters:
        driverParms (webdriver): The webdriver instance.
        file_name (str): The name of the Excel file.

        Returns:
        None
        """
        try:
            # Lire le fichier Excel
            df = pd.read_excel(file_name)

            # Parcourir chaque ligne du DataFrame
            #for index, row in df.iterrows():
            #Manomboka amin'ny page 182 , izany hoe raha 180 no eo , dia 182 izy no manomboka amin'ny excel
            for index, row in df.iloc[256:].iterrows():
                try:
                    print(f"Nombre de lignes traitées : {index}")
                    # Obtenir le lien LinkedIn de la ligne
                    linkedin_link = row['linkedIn']
                    
                    # Utiliser le lien pour rechercher la personne sur LinkedIn
                    section = ScrapingLinkeDIn.search_people_with_link_and_return_section(driverParms, linkedin_link)

                    # Obtenir tous le lien company
                    logo_links = ScrapingLinkeDIn.collecter_liens_logos(section)
                    #Obtenier le premier lien 
                    first_link = logo_links[0] if logo_links else None
                    
                    #Convertir en chaine pour faire recherche
                    url_en_chaine = str(first_link)

                    #S'il y a une mot search dans le link company 
                    if "search" in url_en_chaine:
                        #Ca veut dire qu'il est indépendant + nom entreprise ou ??
                        first_link="indépendant-" + ScrapingLinkeDIn.extraire_mot_cle_de_url(url_en_chaine)
                    
                    # Appeler get_information_company seulement si 'search' n'est pas dans first_link
                    else :
                        time.sleep(1)
                        #Scroll vers demi-page
                        scroll_script = "window.scrollTo(0, document.body.scrollHeight / 2);"
                        driverParms.execute_script(scroll_script)
                        time.sleep(5)
                        # Appeler get_information_company qui entre dans le linkedin de company et collete de donnees
                        info_company = ScrapingLinkeDIn.get_information_company(driverParms, first_link)
                        for key, value in info_company.items():
                            # Mise à jour de tableau excel après avoir collecter le donne de company
                            df.loc[index, key] = value
                    
                    # Stcoker le lien du premier company
                    df.loc[index, 'Link_Linkdin_company'] = first_link

                    # Enregistrer le DataFrame modifié dans le fichier source toutes les 5 lignes
                    if index % 5 == 0:
                        print('----------------------------index                      %5----------------------------')
                        #Enregistrer dans l'excel le donne collecté
                        df.to_excel(file_name, index=False)

                        #redirect vers autre , regarder la fonction radmon_redirect_acceuil_network_message
                        ScrapingLinkeDIn.radmon_redirect_acceuil_network_message(driverParms)

                    # Enregistrer le DataFrame modifié dans le fichier source toutes les 15 lignes
                    if index % 10 == 0 :
                        #Enregistrer dans l'excel le donne collecté
                        df.to_excel(file_name, index=False)

                        #redirect vers autre , regarder la fonction radmon_redirect_acceuil_network_message
                        ScrapingLinkeDIn.radmon_redirect_acceuil_network_message(driverParms)

                    #  toutes les 300 lignes il faut arreter le programme
                    if index == 300:
                       # break = couper le programme
                       break

                    time.sleep(3)
                    scroll_script = "window.scrollTo(0, document.body.scrollHeight / 2);"
                    driverParms.execute_script(scroll_script)
                    time.sleep(7)
                except Exception as e:
                    # print(f"Une erreur s'est produite lors du traitement de la ligne {index} : {e}")
                    continue

            #Enregistrer dans l'excel le donne collecté après avoir quitter le programme
            df.to_excel(file_name, index=False)
        except Exception as e:
            print(f"Une erreur s'est produite lors du traitement du fichier Excel : {e}")

    def get_information_company(driverParms,link_company):

            info_company = {
                'company_name': '',
                'Phone': '',
                'Website': '',
                'Industry': '',
                'Company size': '',
                'Headquarters': '',
                'Founded': '',
                'Specialties': '',
            }

            driverParms.get(link_company)
            WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.XPATH, "//main//section[@class='org-top-card artdeco-card']")))

            time.sleep(random.randint(3,5))

            section_profile=driverParms.find_element(By.XPATH, "//main//section[@class='org-top-card artdeco-card']")
            
            button_about = section_profile.find_element(By.XPATH, "//ul/li//a[text()='About']")
            button_about.click()

            # Attend que la section 'Overview' soit présente
            WebDriverWait(driverParms, 5).until(
                EC.presence_of_element_located((By.XPATH, "//section[.//h2[text()='Overview']]"))
            )

            section_overview=driverParms.find_element(By.XPATH, "//section[.//h2[text()='Overview']]//dl")

            time.sleep(2)

            for key in info_company.keys():
                try:
                    element=""
                    # find the element using XPath
                    if key == 'Phone':
                        element = section_overview.find_element(By.XPATH,f'//dt[text()="Phone"]/following-sibling::dd[1]//span[@dir="ltr"]')
                    else :
                        element = section_overview.find_element(By.XPATH,f'//dt[text()="{key}"]/following-sibling::dd[1]')

                    # store the text of the element
                    info_company[key] = element.text
                    print(element.text)

                except NoSuchElementException:
                    # if the element is not found, store 'Not found'
                    info_company[key] = 'Not found'
                    continue

            company_name = driverParms.find_element(By.XPATH,f'//main//section[@class="org-top-card artdeco-card"]//h1//span[@dir="ltr"]').text
            info_company['company_name'] = company_name
            print(info_company)
            return  info_company   
  
    def radmon_redirect_acceuil_network_message(driverParms):
        vradom=random.randint(0, 3)
        vradom_google=random.randint(0, 3)
        if vradom==vradom_google:
            ScrapingLinkeDIn.redirect_page_google_linkeDin(driverParms)
        else :
            if vradom == 0:
                ScrapingLinkeDIn.redirect_network_linkeDin(driverParms)
            if vradom == 1:
                ScrapingLinkeDIn.redirect_acceuil_linkeDin(driverParms)
            if vradom == 2:
                ScrapingLinkeDIn.redirect_message_linkeDin(driverParms)
            if vradom == 3:
                ScrapingLinkeDIn.redirect_notification_linkeDin(driverParms)


    def extraire_mot_cle_de_url(url):
        # Utiliser une expression régulière pour extraire le mot-clé après "keywords="
        match = re.search(r'\bkeywords=([^&]+)', url)
        
        if match:
            mot_cle = match.group(1)
            # Remplacer les "+" par des espaces
            mot_cle = mot_cle.replace("+", " ")
            return mot_cle
        else:
            return None
    
    def redirect_acceuil_linkeDin(driverParms):
        time.sleep(2)
        print('Home')
        driverParms.get("https://www.linkedin.com/feed/")
        WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "share-box-feed-entry__closed-share-box")))
        time.sleep(15)
        # Obtenir la hauteur de la page
        page_height = driverParms.execute_script("return document.body.scrollHeight")

        # Créer le script de défilement
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(8)
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(4)
    def redirect_network_linkeDin(driverParms):
        time.sleep(1)
        print('Network')
        driverParms.get("https://www.linkedin.com/mynetwork/")
        WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "mn-community-summary__section artdeco-dropdown")))
        time.sleep(7)
        # Obtenir la hauteur de la page
        page_height = driverParms.execute_script("return document.body.scrollHeight")

        # Créer le script de défilement
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(5)
        scroll_script = f"window.scrollTo(0, {random.randint(0, 0)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(2)
    def redirect_message_linkeDin(driverParms):
        time.sleep(3)
        print('Message')
        driverParms.get("https://www.linkedin.com/messaging/thread/new/")
        WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "msg-conversations-container__title-row")))
        time.sleep(5)
        # Obtenir la hauteur de la page
        page_height = driverParms.execute_script("return document.body.scrollHeight")

        # Créer le script de défilement
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(5)
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(4)
 
    def redirect_notification_linkeDin(driverParms):
        time.sleep(2)
        print('Notification')
        driverParms.get("https://www.linkedin.com/notifications/?filter=all")
        WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "artdeco-card nt-application__left-rail-main-card-container")))
        time.sleep(3)
        # Obtenir la hauteur de la page
        page_height = driverParms.execute_script("return document.body.scrollHeight")

        # Créer le script de défilement
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height/2)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(2)
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(3)
    def redirect_page_google_linkeDin(driverParms):
        time.sleep(2)
        print('Aller google')
        driverParms.get("https://www.google.com/search?q=hello")
        #Attendre jusqu'à ce que le classe ="MUFPAc" apparait
        # WebDriverWait(driverParms, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "MUFPAc")))
        time.sleep(10)
        # Obtenir la hauteur de la page
        page_height = driverParms.execute_script("return document.body.scrollHeight")

        # Créer le script de défilement
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height/2)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(15)
        scroll_script = f"window.scrollTo(0, {random.randint(0, page_height)});"
        # Exécuter le script de défilement
        driverParms.execute_script(scroll_script)
        time.sleep(3)
 
    
     
        