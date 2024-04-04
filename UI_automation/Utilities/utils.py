from datetime import datetime
from urllib.parse import quote
import json
import os
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
from Constants.Constants import Constants
from selenium.common.exceptions import TimeoutException
from Constants.ApiConstants import ApiConstants
from Utilities.XLUtils import createWorkBook
import logging
from seleniumwire.utils import decode as sw_decode


def login(self, setup, pageAction=None, goToPage=None, key=None):
    """ this function will log in to datamotive node with provided credentials"""
    setupIp = ''
    if len(pageAction.get_cookies()) == 0:
        if key != None:
            self.driver.get(setup[key])
            setupIp = setup[key]
        else:
            self.driver.get(setup["sourceurl"])
            setupIp = setup["sourceurl"]
        pageAction.sendInputKeys((By.XPATH, "//input[@id='userName']"), setup["username"])
        pageAction.sendInputKeys((By.XPATH, "//input[@id='password']"), setup["password"])
        pageAction.onClick((By.XPATH, "//button[normalize-space()='Log In']"))
        getApiResponse(self, ApiConstants.LOGIN_API)
        url = f"{setupIp}/{goToPage}"
        self.driver.get(url)


def getApiResponse(self, api):
    """  This will get the response received from the provided api url"""
    try:
        encodedApi = quote(api, safe=':/?=&,')
        request = self.driver.wait_for_request(encodedApi, timeout=60)
        if request.response:
            bodyjson = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
            decodeBody = bodyjson.decode('utf-8')
            res = json.loads(decodeBody)
            return res
    except TimeoutException as ex:
        return None


def getResponseFromResponseArray(self, api):
    """Browser has value of the previously executed url below function will give the response for the provided url"""
    try:
        data = []
        encodedApi = quote(api, safe=':/?=&,')
        for request in self.driver.requests:
            if request.response and encodedApi in request.url:
                data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                data = data.decode("utf8")
                data = json.loads(data)
                break
        return data
    except TimeoutException as ex:
        return None


def loadFilePath(filename):
    """This function will search for the filename provided in the parameter and return its path"""

    path = os.path.realpath(
        os.path.join(os.path.dirname(__file__), '..', f'{filename}'))
    return path


def createReportFile():
    """this will create report directory and report file based on  that particular time every time code gets executed"""
    if not os.path.exists(Constants.REPORT_DIR_path):
        os.makedirs(Constants.REPORT_DIR_path)
    now = datetime.now()
    fileName = 'report' + now.strftime("%d-%m-%Y-%H-%M-%S") + '.xlsx'
    createWorkBook(os.path.join(Constants.REPORT_DIR_path, fileName))

    return fileName


def getLogger():
    """This will create logger object which we can use to add logs to the file"""

    '''to get the name of the test case file name at runtime'''
    logger = logging.getLogger(__name__)

    '''FileHandler class to set the location of log file'''

    fileHandler = logging.FileHandler('logfile.log', mode='w')

    '''Formatter class to set the format of log file'''
    formatter = logging.Formatter('[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                  '%m-%d %H:%M:%S')

    '''object of FileHandler gets formatting info from setFormatter #method'''

    fileHandler.setFormatter(formatter)

    '''logger object gets formatting, path of log file info with addHandler method'''
    logger.addHandler(fileHandler)

    '''setting logging level to INFO'''
    logger.setLevel(logging.INFO)

    return logger


'''On UI there is a lot of tables to get value in the cell of the table below function is used'''


def getCellValue(self, key, index=None):
    table = self.findElement((By.CLASS_NAME, 'table'))
    table_head = table.find_elements(by=By.CSS_SELECTOR, value='thead')
    ind = 0
    for h in table_head:
        row = h.find_elements(by=By.CSS_SELECTOR, value='tr')
        for r in row:
            header = r.find_elements(by=By.CSS_SELECTOR, value='th')
            for i, cel in enumerate(header):
                txt = cel.text
                if txt == key:
                    ind = i
                    break
    tBody = table.find_elements(by=By.CSS_SELECTOR, value='tbody')

    if index is not None:
        for body in tBody:
            row = body.find_elements(by=By.CSS_SELECTOR, value='tr')
            cells = row[index].find_elements(by=By.CSS_SELECTOR, value='th')
            val = cells[ind].text
            return val
    else:
        for body in tBody:
            row = body.find_elements(by=By.CSS_SELECTOR, value='tr')
            for r in row:
                cells = r.find_elements(by=By.CSS_SELECTOR, value='th')
                val = cells[ind].text
                return val


def getCell(self, key, index):
    table = self.findElement((By.CLASS_NAME, 'table'))
    tBody = table.find_elements(by=By.CSS_SELECTOR, value='tbody')
    for body in tBody:
        row = body.find_elements(by=By.CSS_SELECTOR, value='tr')
        cells = row[index].find_elements(by=By.CLASS_NAME, value='col-sm-7')
        return cells[index]
