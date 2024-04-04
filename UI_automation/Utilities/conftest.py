import os
from selenium.webdriver.common.proxy import *
from seleniumwire import webdriver 
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options as ChromOption
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome import service
from webdriver_manager.opera import OperaDriverManager
from Constants.Constants import Constants

'''Sets browser to execute automation'''
def setupBrowser( cls,browserType=""):
                currentdirectory = os.getcwd()
                chromedriverExecutablepath = os.path.join(currentdirectory, "Drivers\chromedriver.exe")
    # match browserType :
    #     case Constants.FIREFOX:
    #         driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    #         cls.driver = driver
    #     case Constants.EDGE:
    #         options = EdgeOptions()
    #         options.add_argument('--allow-running-insecure-content')
    #         options.add_argument('--ignore-certificate-errors')
    #         driver = webdriver.Edge(service=EdgeService(EdgeChromiumDriverManager().install(),options=options))
    #         driver.implicitly_wait(10)
    #         cls.driver = driver
    #     case Constants.OPERA:
    #         webdriver_service = service.Service(OperaDriverManager().install())
    #         webdriver_service.start()

    #         driver = webdriver.Remote(webdriver_service.service_url)
    #         cls.driver= driver
    #     case _ :
                options = ChromOption()
                options.add_argument("--start-maximized")
                options.add_argument("--ignore-certificate-errors")
                options.add_experimental_option("excludeSwitches", ["enable-logging"])
                options.add_argument('--allow-running-insecure-content')
                options.add_argument("−−incognito");
                driver = webdriver.Chrome(service=ChromeService(executable_path=chromedriverExecutablepath), options=options)
                cls.driver = driver