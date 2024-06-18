from seleniumwire import webdriver

'''Sets browser to execute automation'''


def setupBrowser(cls, browserType=""):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("−−incognito")
    driver = webdriver.Chrome(options=options)
    cls.driver = driver
