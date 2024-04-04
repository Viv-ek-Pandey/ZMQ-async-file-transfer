from time import sleep
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from selenium.webdriver.common.action_chains import ActionChains
from Constants.Constants import Constants

'''All the common webpage events '''


class CommonWebPageActions:

    def __init__(self, driver):
        self.driver = driver

    def getPageTitles(self):
        return self.driver.title

    '''To enter text in text input field'''

    def sendInputKeys(self, by_locator, text):
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.presence_of_element_located(by_locator)).send_keys(text)

    '''To click on element based on xpath'''

    def onClick(self, by_locator):
        WebDriverWait(self.driver, Constants.FOUR_MINUTE).until(EC.element_to_be_clickable(by_locator)).click()

    '''To check checkbox'''

    def onAnimationClick(self, by_locator):
        try:
            element = WebDriverWait(self.driver, Constants.THIRTY_SECONDS).until(EC.presence_of_element_located(by_locator))
            ActionChains(self.driver).move_to_element(element).click().perform()
        except:
            None

    '''For finding element based on xpath'''

    def findElement(self, locator):
        try:
            element = WebDriverWait(self.driver, Constants.THREE_MINUTE).until(EC.presence_of_element_located(locator))
            return element
        except TimeoutException as ex:
            return None

    '''For Onenter event'''

    def onEnter(self, by_locator):
        WebDriverWait(self.driver, Constants.TWENTY_SECONDS).until(EC.presence_of_element_located(by_locator)).send_keys(Keys.ENTER)

    '''For clearing text input'''

    def clearInputFields(self, by_locator):
        WebDriverWait(self.driver, Constants.ONE_MINUTE).until(EC.presence_of_element_located(by_locator)).send_keys(Keys.CONTROL + 'a',
                                                                                                   Keys.BACKSPACE)

    '''For getting the browser cookies'''

    def get_cookies(self):
        cookie_list = self.driver.get_cookies()
        return cookie_list

    def singleSelectFromDropdown(self, by_locator, text):
        '''Selecting option '''
        element = WebDriverWait(self.driver, Constants.TWO_MINUTE).until(EC.presence_of_element_located((by_locator)))
        select = Select(element)
        sleep(1)
        try:
            select.select_by_visible_text(text)
        except NoSuchElementException:
            return None

    def searchSelectFromDropdown(self, by_locator, text):

        '''search and select option'''

        self.sendInputKeys(by_locator, text)
        sleep(3)
        self.onEnter(by_locator)

    def uploadFile(self, by_locator, path):

        '''Uploads file in input field'''
        try:
            element = self.findElement(by_locator)
            element.send_keys(path)
        except InvalidArgumentException:
            return f"invalid file path {path} or file does not exist"

    def scrollToFindElement(self, by_locator):

        '''Scroll to find element in webpage'''

        ele = self.findElement(by_locator)
        self.driver.execute_script("arguments[0].scrollIntoView();", ele)

    def waitUntil(self, by_locator):
        WebDriverWait(self.driver, Constants.FOUR_MINUTE).until(EC.presence_of_element_located((by_locator)))
