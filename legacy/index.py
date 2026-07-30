from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ScrapingLinkeDIn import ScrapingLinkeDIn

import time

def main():
    try :
        options = webdriver.ChromeOptions() 
        # # Setup the Chrome driver
        driver =webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)

        scrapingLinkeDIn = ScrapingLinkeDIn()

        # Utilisez la méthode loginLinkeDIn pour vous connecter à LinkedIn
        scrapingLinkeDIn.loginLinkeDIn(driver, "REDACTED", "REDACTED")
        
        time.sleep(60)
        # Utilisez la méthode search_people_with_link pour aller sur le profil LinkedIn que vous voulez scraper
        scrapingLinkeDIn.process_excel_file(driver,"./scalezia.xlsx")

        # Fermez le navigateur une fois que vous avez terminé
        driver.quit()
        # scrapingLinkeDIn.hello("./scalezia.xlsx")
        
    except Exception as e:
        print(f"---")


if __name__ == "__main__":
    main()