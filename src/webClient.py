from abc import ABC, abstractmethod
from typing import Dict
import config
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from requests.models import Response

class GenericWebClient(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def get(self, link : str, **kwargs):
        pass

class SeleniumClient(GenericWebClient):
    def __init__(self):
        self._setupSeleniumDriver()

    def _setupSeleniumDriver(self) -> None:
        options = Options()
        options.headless = False
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager('114.0.5735.90').install()), options = options)

    def get(self, link : str, **kwargs) -> Response:
        self.driver.get(link)

    def close(self) -> None:
        self.driver.close()

    def getOuterHtmlOfElementByXpath(self, elementName : str) -> str:
        return self.driver.find_element(By.XPATH, elementName).get_attribute('outerHTML')

class WebScraper(ABC):
    def __init__(self, web_client : GenericWebClient, base : str = None):
        self.web_client : GenericWebClient = web_client
        self.base : str = base
        if not self.base:
            self.base = web_client.base
        
    def getBase(self) -> str:
        return self.base
    
    @abstractmethod
    def _getSinglePandasTableFromLink(self, endpoint : str, **kwargs):
        pass

class SeleniumWebScraper(WebScraper):
    def __init__(self, web_client : SeleniumClient, base : str = None):
        super().__init__(web_client, base)
    
    def _getSinglePandasTableFromLink(self, endpoint : str, **kwargs) -> pd.DataFrame:
        elementName = kwargs.get('elementName', None)
        self.web_client.get(endpoint)
        try:
            html_table : str = self.web_client.getOuterHtmlOfElementByXpath(elementName)
        except:
            print(f"Wasn't able to identify element {elementName} at current web page: {endpoint}")
            return None
        res = pd.read_html(html_table, header = 1)
        
        if len(res) > 1:
            print("Identified more than one table - returning first one")    
        return res[0]
    
class ESPNScraper(SeleniumWebScraper):
    def __init__(self, web_client : SeleniumClient, login : Dict[str, str], base : str = 'espn.com'):
        super().__init__(web_client, base)
        self.login = login
        self._loginToSite()
        
    def _loginToSite(self) -> None:
        login_path = '/login'
        self.web_client.get('https://' + self.base + login_path)
        self._login(self.login['username'], self.login['password'])

    def _login(self, 
              user : str, 
              password : str) -> None:
        iframe = self.web_client.driver.find_element(By.NAME, "disneyid-iframe") # Or locate by other attributes
        self.web_client.driver.switch_to.frame(iframe)
        user_input = self.web_client.driver.find_element(By.XPATH, "//input[@type='email']")
        password_input = self.web_client.driver.find_element(By.XPATH,"//input[@type='password']")
        login_button = self.web_client.driver.find_element(By.XPATH, "//button")
        
        user_input.send_keys(user)
        password_input.send_keys(password)
        login_button.send_keys(Keys.RETURN)
        code = input("Enter the code sent to your email: ")

        code_input = self.web_client.driver.find_element(By.XPATH, "//input[@type='tel']")
        code_input.send_keys(code)

        continue_button = self.web_client.driver.find_element(By.XPATH, "//button")
        continue_button.send_keys(Keys.RETURN)
        

    def scrapeTeams(self, season : int, league_id : str):
        draft_recap_suffix = f'football/league/draftrecap?leagueId={league_id}&seasonId={season}'
        draft_recap_prefix = 'https://fantasy.'
        link = draft_recap_prefix + self.base + draft_recap_suffix
        self.web_client.get(link)
        
if __name__ == '__main__':
    config = config.Config('../config.ini')
    base_link = config.parse_section('reader')['espn_fantasy_base']
    link = base_link + 'football/league/draftrecap?leagueId=47097656&seasonId=20'
    
    espn_login = {}
    espn_login['username'] = config.parse_section('espn')['username']
    espn_login['password'] = config.parse_section('espn')['password']
    
    webclient1 = SeleniumClient()
    scraper1 = ESPNScraper(webclient1, espn_login)
    scraper1.scrapeTeams(2019, config.parse_section('espn')['league_id'])
    # scraper1.web_client.close()