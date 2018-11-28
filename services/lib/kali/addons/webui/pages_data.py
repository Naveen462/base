"""
CUSTOM BUTTONS LABEL
=====================

In this Dict are stored all input field.
The Key is the refer label,
by: is the method used to find the element,
value: is the value to look for.

"""
from selenium.webdriver.common.by import By
TEXT_FIELD = 'text'
N_FIELD = 'number'
CHECKBOX_FIELD = 'checkbox'
SELECT = 'select'
BTN = 'button'
FILE = 'file'
DIV = 'div'
LBL = 'label'

INPUTS_DICT = {
    'Home_Page': {
        'type': LBL,
        'by': By.XPATH,
        'value': '/html/body/div/div/div[1]/div/div[1]/div'
    },

    'GVR ID': {
        'type': TEXT_FIELD,
        'by': By.NAME,
        'value': 'siteid'
    },

    'Omnia Local ID': {
        'type': TEXT_FIELD,
        'by': By.NAME,
        'value': 'localId'
    },

    'Omnia Nickname': {
        'type': TEXT_FIELD,
        'by': By.NAME,
        'value': 'FDT_Nickname'
    },

    'Incremental logs': {
        'type': CHECKBOX_FIELD,
        'by': By.NAME,
        'value': 'incrementalLogsEnabled'
    },

    'Download Logs Every (mins)': {
        'type': TEXT_FIELD,
        'by': By.NAME,
        'value': 'input'
    },

    'Setup Wizard': {
        'type': BTN,
        'by': By.ID,
        'value': 'wizardButtonId'
    },

    'Password': {
        'type': TEXT_FIELD,
        'by': By.NAME,
        'value': 'password'

    },

    'NEXT_BTN': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/a[@ng-click="handleNext(mediaTableInWizard)"]'
    },

    'OMNIA_SAVE': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/button[@ng-click="omniaSave()"]'
    },

    'New_Config': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/button[@ng-click="newConfiguration()"]'
    },

    'Import_Config': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/button[@ng-click="importFile()"]'
    },

    'CONFIG_OPTIONS1': {
        'type': CHECKBOX_FIELD,
        'by': By.XPATH,
        'value': '//*/input[@id="checkbox1"]',
        'hidden': True
    },

    'CONFIG_OPTIONS2': {
        'type': CHECKBOX_FIELD,
        'by': By.XPATH,
        'value': '//*/input[@id="checkbox2"]',
        'hidden': True
    },

    'CONFIG_OPTIONS3': {
        'type': CHECKBOX_FIELD,
        'by': By.XPATH,
        'value': '//*/input[@id="checkbox3"]',
        'hidden': True
    },

    'Omnia (always present)': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/label[@for="checkbox1"]',
    },

    'WizardMedia': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/label[@for="checkbox2"]',
        'description': 'Checkbox in Wizard PopUp',
        'label_text': 'Media'
    },

    'GVR Cloud Remote Management': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/label[@for="checkbox3"]',
    },

    'IMPORT_TAB': {
        'type': TEXT_FIELD,
        'by': By.XPATH,
        'value': '//*/input[@ng-file-select="onFileSelect($files)"]'
    },

    'WIZARD': {
        'type': TEXT_FIELD,
        'by': By.XPATH,
        'value': '//*/input[@ng-file-select="onFileSelect($files)"]'
    },

    'UPDATE_TAB': {
        'type': TEXT_FIELD,
        'by': By.XPATH,
        'value': '//*/input[@ng-file-select="onFileSelect($files)"]'
    },

    'OMNIA_UTILITY_SYS_INFO': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/button[@ng-click="openSysInfoRetrieval()"]'
    },

    'OMNIA_UTILITY_EXPORT_CONFIG': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/button[@ng-click="exportCurrentConfig()"]'
    },

    'OMNIA_UTILITY_LOG': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/button[@ng-click="openLogRetrieval()"]'
    },

    'OMNIA_UTILITY_SET_DATATIME': {
        'type': BTN,
        'by': By.XPATH,
        'value':  '//*/button[@ng-click="openSetTimeAndDateModal()"]'
    },

    'OMNIA_UTILITY_ADVANCE_SETTINGS': {
        'type': BTN,
        'by': By.XPATH,
        'value':   '//*/button[@ng-click="openAdvancedSettingsModal()"]'
    },

    'OMNIA_UTILITY_UPDATE': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/button[@ng-click="openOmniaUpdateModal()"]'
    },

    'OMNIA_UTILITY_REBOOT': {
        'type': BTN,
        'by': By.XPATH,
        'value':  '//*/button[@ng-click="reboot()"]'
    },

    'DOWNLOADED_POPUP': {
        'type': LBL,
        'by': By.XPATH,
        'value': "//*[normalize-space(.)='Request has successfully completed']"
    },

    'ADMIN': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/li[@class="dropdown"]',
    },

    'LOGOUT': {
        'type': BTN,
        'by': By.XPATH,
        'value': '//*/a[@href="/logout"]',
    },

    'EXPORT': {
        'type': BTN,
        'by': By.CSS_SELECTOR,
        'value': 'method'  # TODO*/
    },

    'SIDE_A_TERMINAL_ID': {
        'type': N_FIELD,
        'by': By.ID,
        'value': 'mediaTable-sidea-terminalId'

    },

    'SIDE_B_TERMINAL_ID': {
        'type': N_FIELD,
        'by': By.ID,
        'value': 'mediaTable-sideb-terminalId'

    },
    'SIDE_A_PUMP_ID': {
        'type': N_FIELD,
        'by': By.ID,
        'value': 'mediaTable-sidea-pumpId'

    },
    'SIDE_B_PUMP_ID': {
        'type': N_FIELD,
        'by': By.ID,
        'value': 'mediaTable-sideb-pumpId'

    },
    'LOG_RETRIEVAL_OMNIA_OS': {
        'type': CHECKBOX_FIELD,
        'by': By.ID,
        'value': 'omniaOSSelected',
        'hidden': True,
        'label_text': 'Omnia (OS + Apps)',
        'description': 'Located in Log retrieval popup'


    },
    'LOG_RETRIEVAL_MEDIA_APP': {
        'type': CHECKBOX_FIELD,
        'by': By.ID,
        'value': 'mediaSelected',
        'hidden': True,
        'label_text': 'Media App',
        'description': 'Located in Log retrieval popup'

    },
    'LOG_RETRIEVAL_CLOUD_APP': {
        'type': CHECKBOX_FIELD,
        'by': By.ID,
        'value': 'cloudSelected',
        'hidden': True,
        'label_text': 'Cloud App',
        'description': 'Located in Log retrieval popup'

    },
    'LOG_RETRIEVAL_DATE_START': {
        'type': TEXT_FIELD,
        'by': By.NAME,
        'value': 'start',
        'label_text': 'Range of dates: from',
        'description': 'Located in Log retrieval popup'

    },
    'LOG_RETRIEVAL_DATE_END': {
        'type': TEXT_FIELD,
        'by': By.NAME,
        'value': 'end',
        'label_text': 'Range of dates: to',
        'description': 'Located in Log retrieval popup'


    },
}

LED_GREEN_IMG = "led-green-black-300px.png"
LED_BLACK_IMG = "led-black-300px.png"
LED_RED_IMG = "led-red-black-300px.png"

LED_DICT = {

    'Network status': ['SIDE A reachable', 'SIDE B reachable'],
    'Cloud status': ['Configured', 'Registered',
                     'Connected to GVR Cloud Server'],
    'Media status': ['Configured', 'Applause server reachable']


}

ELEMENT_DICT = {
    'img': 'src',
    'link': 'href',
    'table': 'text'
}
