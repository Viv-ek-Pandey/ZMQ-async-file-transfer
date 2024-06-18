from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from selenium.webdriver.common.action_chains import ActionChains
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
from selenium.webdriver.common.by import By


class CommonWebPageActions:
    '''
    All the common webpage events 
    '''
    def __init__(self, driver):
        self.driver = driver

    def getPageTitles(self):
        '''
        To return page title
        '''
        return self.driver.title


    def sendInputKeys(self, by_locator, text):
        '''
        To enter text in text input field
        '''
        self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.presence_of_element_located(by_locator)).send_keys(
            text)


    def onClick(self, by_locator):
        '''
        To click on element based on xpath
        '''
        try:
            self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
            WebDriverWait(self.driver, Constants.FOUR_MINUTE).until(EC.element_to_be_clickable(by_locator)).click()
        except TimeoutException as ex:
            return None


    def onAnimationClick(self, by_locator):
        '''
        To check checkbox
        '''
        try:
            self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
            WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.element_to_be_clickable(by_locator))
            element = WebDriverWait(self.driver, Constants.ONE_MINUTE).until(
                EC.presence_of_element_located(by_locator))
            ActionChains(self.driver).move_to_element(element).click().perform()
        except:
            None


    def findElement(self, locator):
        '''
        For finding element based on xpath
        '''
        try:
            self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
            WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.element_to_be_clickable(locator))
            element = WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.presence_of_element_located(locator))
            return element
        except TimeoutException as ex:
            return None


    def onEnter(self, by_locator):
        '''
        For Onenter event
        '''
        self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
        WebDriverWait(self.driver, Constants.TWENTY_SECONDS).until(
            EC.presence_of_element_located(by_locator)).send_keys(Keys.ENTER)


    def clearInputFields(self, by_locator):
        '''
        For clearing text input
        '''
        self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.presence_of_element_located(by_locator)).send_keys(
            Keys.CONTROL + 'a',
            Keys.BACKSPACE)


    def getCookies(self):
        '''
        For getting the browser cookies
        '''
        cookie_list = self.driver.get_cookies()
        return cookie_list


    def singleSelectFromDropdown(self, by_locator, text):
        '''
        Selecting option 
        '''
        self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.element_to_be_clickable(by_locator))
        element = WebDriverWait(self.driver, Constants.TWO_MINUTE).until(EC.presence_of_element_located((by_locator)))
        select = Select(element)
        try:
            select.select_by_visible_text(text)
        except NoSuchElementException:
            return None


    def searchSelectFromDropdown(self, by_locator, text):
        '''
        search and select option
        '''
        self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.element_to_be_clickable(by_locator))
        self.sendInputKeys(by_locator, text)
        sleep(Constants.THREE_SECONDS)
        self.onEnter(by_locator)


    def uploadFile(self, by_locator, path):
        '''
        Uploads file in input field
        '''
        try:
            element = self.findElement(by_locator)
            element.send_keys(path)
        except InvalidArgumentException:
            return f"invalid file path {path} or file does not exist"


    def scrollToFindElement(self, by_locator):
        '''
        Scroll to find element in webpage
        '''
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.element_to_be_clickable(by_locator))
        ele = self.findElement(by_locator)
        self.driver.execute_script("arguments[0].scrollIntoView();", ele)


    def waitUntil(self, by_locator):
        '''
        Wait Until Element is not found
        '''
        self.waitUntilElementDisappears((By.XPATH, XpathConstants.LOADER_XPATH))
        WebDriverWait(self.driver, Constants.FOUR_MINUTE).until(EC.presence_of_element_located(by_locator))


    def scrollTopToFindElement(self):
        '''
        Scroll to the top of the page
        '''
        self.driver.execute_script("window.scrollTo(0, document.body.scrollTop);")


    def waitUntilElementIsClickable(self, by_locator):
        '''
        wait Until Element is not clickable
        '''
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.element_to_be_clickable(by_locator))
        wt = WebDriverWait(self.driver, Constants.THREE_MINUTE)
        wt.until(EC.element_to_be_clickable(by_locator))


    def waitUntilElementDisappears(self, by_locator):
        '''
        Wait until element disappears
        '''
        WebDriverWait(self.driver, Constants.TWO_MINUTE).until(EC.invisibility_of_element_located(by_locator))
