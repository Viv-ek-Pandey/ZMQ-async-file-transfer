from selenium.webdriver.common.by import By
from Utilities.CommonWebPageActions import CommonWebPageActions
from Utilities.XLUtils import addTestResultToReportSheet
from Constants.Constants import Constants
from Constants.XpathConstants import XpathConstants
import traceback


class EmailActions(CommonWebPageActions):

    def __init__(self, driver):

        super().__init__(driver)
        self.driver = driver


    def email(self, data, filepath, logger):
        try :
            '''
            This function will execute email activity
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            emailAddress = data["emailAddress"]
            emailPassword = data["emailPassword"]
            smtpHost = data["smtpHost"]
            smtpPort = data["smtpPort"]
            logger.info(Constants.EMAIL_INITIATED_SUCCESSFULLY)
            if emailAddress and emailPassword and smtpHost and smtpPort:
                # To click settings section
                self.onClick((By.XPATH, XpathConstants.SETTINGS_SECTION_XPATH))
                # To click email section
                self.onClick((By.XPATH, XpathConstants.EMAIL_SECTION))
                # To click configure now button to configure email
                self.onClick((By.XPATH, XpathConstants.CONFIGURE_NOW_BUTTON_XPATH))
                # To find element modal content"""
                self.findElement((By.XPATH, XpathConstants.MODAL_CONTENT_XPATH))
                # To clear input fields of email address
                self.clearInputFields((By.XPATH, XpathConstants.EMAIL_ADDRESS_XPATH))
                # To enter email address
                self.sendInputKeys((By.XPATH, XpathConstants.EMAIL_ADDRESS_XPATH), emailAddress)
                # To clear input fields of email password
                self.clearInputFields((By.XPATH, XpathConstants.EMAIL_PASSWORD))
                # To enter email password
                self.sendInputKeys((By.XPATH, XpathConstants.EMAIL_PASSWORD), emailPassword)
                # To clear input fields of smtp host
                self.clearInputFields((By.XPATH, XpathConstants.SMTP_HOST))
                # To enter smtp host
                self.sendInputKeys((By.XPATH, XpathConstants.SMTP_HOST), smtpHost)
                # To clear input fields of smtp port
                self.clearInputFields((By.XPATH, XpathConstants.SMTP_PORT))
                # To enter smtp port
                self.sendInputKeys((By.XPATH, XpathConstants.SMTP_PORT), smtpPort)
                # To configure button
                self.onClick((By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))
                messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                if closeButton:
                    self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                addTestResultToReportSheet(filepath, Constants.EMAIL_TEST, Constants.EMAIL_HEADER, data, messagePopup)
                logger.info(messagePopup)
                if Constants.EMAIL_CONFIGURED in messagePopup:
                    return Constants.PASSED
                else:
                    return Constants.FAILED
            else:
                logger.error(Constants.INVALID_EMAIL_FIELDS)
                addTestResultToReportSheet(filepath, Constants.EMAIL_TEST, Constants.EMAIL_HEADER, data, Constants.INVALID_EMAIL_FIELDS)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())
    

    def emailRecipients(self, data, filepath, logger):
        try:
            '''
            This function will execute email recipient activity
            data: json data received from json file
            filepath: absolute file path where reports will be created
            logger: logger object
            '''
            emailAddress = data["emailAddress"]
            subscribedEvents = data["subscribedEvents"]
            logger.info(Constants.EMAIL_RECIPIENT_INITIATED_SUCCESSFULLY)
            if emailAddress and subscribedEvents:
                # To click settings section
                self.onClick((By.XPATH, XpathConstants.SETTINGS_SECTION_XPATH))
                # To click email section
                self.onClick((By.XPATH, XpathConstants.EMAIL_SECTION))
                # To click settings section
                self.onClick((By.XPATH, XpathConstants.ADD_BUTTON_XPATH)) 
                # To find element modal content
                self.findElement((By.XPATH, XpathConstants.MODAL_CONTENT_XPATH))
                # To clear input fields of email address
                self.clearInputFields((By.XPATH, XpathConstants.RECIPIENT_EMAIL_ADDRESS))
                # To enter email address
                self.sendInputKeys((By.XPATH, XpathConstants.RECIPIENT_EMAIL_ADDRESS), emailAddress)
                # To select each event
                for eachEvent in subscribedEvents:
                    self.singleSelectFromDropdown((By.XPATH, XpathConstants.SUBSCRIBED_EVENTS), eachEvent)
                # To configure button"""
                self.onClick((By.XPATH, XpathConstants.CONFIGURE_BUTTON_XPATH))
                messagePopup = self.findElement((By.XPATH, XpathConstants.MESSAGE_POPUP_XPATH)).text
                closeButton = self.findElement((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                if closeButton:
                    self.onClick((By.XPATH, XpathConstants.CLOSE_WIZARD_XPATH))
                addTestResultToReportSheet(filepath, Constants.EMAIL_TEST, Constants.EMAIL_RECIPIENT_HEADER, data, messagePopup)
                logger.info(messagePopup)
                if Constants.EMAIL_RECIEPIENT_CONFIGURED in messagePopup:
                    return Constants.PASSED
                else:
                    return Constants.FAILED
            else:
                logger.error(Constants.INVALID_EMAIL_FIELDS)
                addTestResultToReportSheet(filepath, Constants.EMAIL_TEST, Constants.EMAIL_RECIPIENT_HEADER, data, Constants.INVALID_EMAIL_FIELDS)
                return Constants.FAILED

        except Exception:
            logger.error(traceback.format_exc())
