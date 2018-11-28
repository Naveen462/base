"""
WebUi Automation Addon
========================
Addon to automate actions in webui
"""
import os
import glob
from time import sleep
import time
from datetime import datetime
from datetime import timedelta
import shutil
# from time import strftime
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import StaleElementReferenceException
from .pages_data import INPUTS_DICT, BTN, \
    LED_DICT, LED_GREEN_IMG, LED_BLACK_IMG, LED_RED_IMG, ELEMENT_DICT, \
    CHECKBOX_FIELD
from ..abstract import KaliAddOn
from ...exceptions import *


class KaliWebUiAddon(KaliAddOn):
    """


    """

    def __init__(self, **kwargs):
        KaliAddOn.__init__(self, **kwargs)

        self.is_logged = False
        self.driver = None
        self.addon_type = 'webui'

    # MANDATORY
    def setup(self):
        """
        **Mandatory Kali method**

        Args:
            **kwargs**: keyword arguments.
            ip(str): [**Mandatory**] WebUi interface base url.
            port(str): The port of the webui default 3000
            wait (int): Time to wait in seconds for an element to appear in a
                page. Default is 30s.
            browser(str): choose between Firefox,Chrome. Default is Chrome
            download_folder(str): the path where to download files. Default is
                'download' in working dir.

        """
        self.display = Display(visible=True, size=(1280, 720))
        self.display.start()
        self.download_folder = self.kwargs.get(
            'download_folder') or "%s/download" % os.getcwd()
        browser = self.kwargs.get('browser') or 'Chrome'
        self.driver = None
        n_try = 0
        try:
            self.__configure(browser)
        except ConnectionResetError as e:
            print('NOT CONFIG')
            n_try += 1
            sleep(0.5)
            if n_try <= 3:
                self.close()
                self.setup()
            else:
                raise KaliExceptionWebUiDriver(e)
        self.driver.set_window_size(1280, 720)
        base_url = self.ip
        omnia_port = self.kwargs.get('port', '3000')
        self.base_url = "http://%s:%s" % (base_url, omnia_port)
        if not self.check_timeout:
            self.check_timeout = 5
        self.driver.get(self.base_url)
        return True

    def __configure(self, browser):
        if browser == 'Chrome':
            self.__config_chrome()
        elif browser == 'Firefox':
            self.__config_firefox()
        else:
            raise KaliExceptionWebUiDriver(
                'No config found for %s browser. Try: Chrome or Firefox'
                % browser)

    def __config_chrome(self):
        chromeOptions = webdriver.ChromeOptions()
        prefs = {"download.default_directory": self.download_folder}
        chromeOptions.add_experimental_option("prefs", prefs)
        # chromedriver = "path/to/chromedriver.exe" #
        # executable_path=chromedriver,
        self.driver = webdriver.Chrome(chrome_options=chromeOptions)

    def __config_firefox(self):
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", self.download_folder)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk",
                          "application/x-msdos-program")
        self.driver = webdriver.Firefox(firefox_profile=fp)

    def close(self):
        """Called when the test is finish"""
        self.display.stop()
        self.driver = None

    def start(self, url, browser='Chrome'):
        """Dosent Work"""
        return True  # dosent work anymore
        self.setup(browser=browser, url=url)

    def set_wait_timeout(self, seconds):
        """To set up the main timeout to wait before fail.

        Args:
            seconds(int): time to wait element in seconds

        """
        try:
            self.check_timeout = float(seconds)
        except Exception:
            self.logger.erro("Timeout not setted, wrong format, use float")
    # INTERNAL

    def __str__(self):
        return "KALI WebUi Automation Addon"

    def __return_visible_element(self, elements):
        """
        Find the visible element in the page

        **internal method**

        Args:
            elements (list): List of Selenium Objects

        Returns:
            Object: the first Selenium object visible.

        """
        for element in elements:
            self.driver.execute_script(
                "return arguments[0].scrollIntoView(false);", element)
            if element.is_displayed():
                return element
            # elif element.is_clickable():
            #     return element
            # lif element.is_enabled():
            #  return element
        return None

    def __find_visible_by(self, locator_method, name, hidden=False):
        """Looks for the first visible element in the page.

        Args:
            locator_method (str): a method to find the element
             by the value gave [eg. 'find_elements_by_xpath']
            name (str): the name of the value are looking for.

        Returns:
            Element: the selenium element you are looking for.
        """

        element_present = EC.presence_of_element_located(
            (locator_method, name))
        # On negative cases the code below the following line is not reachable
        try:
            WebDriverWait(self.driver, self.check_timeout).until(
                element_present)
        except TimeoutException:
            return False
        if hidden:
            return self.driver.find_elements(by=locator_method, value=name)[0]
        elements = self.driver.find_elements(by=locator_method, value=name)
        return self.__return_visible_element(elements)

    def __find_and_set_by_xpath(self, xpath, value):
        """
        **internal method**

        Set value to  input field locate in the xpath gave

            Args:
                xpath(str): The selenium xpath to find input
                value (str): The value you wants to put inside the input
        """
        element = self.__return_visible_element(
            self.driver.find_elements_by_xpath(xpath))
        element.clear()
        element.send_keys(value)

    def __find_by_approximation(self, label, _type):
        """
        Find the input (_type) adjacent to the label gave

        **internal method**

        Args:
            label (str): The visible label string that referred to input
            _type (str): The input type (eg. text, select, checkbox)

        Returns:
            Object: Selenium element
        """
        label_element = self.__find_visible_by(
            By.XPATH,
            "//*[normalize-space(.)='" + label + "']")
        _input = self.driver.execute_script(
            "var label = arguments[0];return $(label).find(''+arguments[1]+'')",
            label_element, _type)

        if not _input:
            _input = self.driver.execute_script(
                "var label = arguments[0];return $(label)" +
                ".find( 'input[type='+arguments[1]+']')",
                label_element, _type)
            if not _input:
                _input = self.driver.execute_script(
                    "var label = arguments[0]; return $(label).next()",
                    label_element)
        try:
            _input = _input[0]
        except KeyError:
            pass
        except IndexError:
            return None
        if _input.tag_name != _type and _input.get_attribute('type') != _type:
            _input = self.driver.execute_script(
                "var element = arguments[0]; var in_type = arguments[1];\
                 return $(element).find(in_type)", _input, _type)
            try:
                _input = _input[0]
            except IndexError:
                return None
            except TypeError:
                pass
        return _input

    def __get_element(self, label, _type=None):
        """
        Get Selenium element by label

        **internal method**

        Args:
            label (str): The visible label string that referred to input
            _type (str):(*not mandatory*) The input type (text,select,checkbox)
                    check if type gives matching with Selenium element found.

        Returns:
            Object: Selenium element
        """

        in_type = _type

        if label in INPUTS_DICT:
            element = INPUTS_DICT[label]
            in_type = element['type']
            hidden = element.get('hidden')
            # TODO DRY
            if hidden:
                element = self.__find_visible_by(
                    element['by'], element['value'], hidden)
            else:
                element = self.__find_visible_by(
                    element['by'], element['value'])
        else:
            element = self.__find_by_approximation(label, _type)
            if element:
                in_type = element.tag_name
                if _type and _type != in_type:
                    if element.get_attribute('type'):
                        in_type = element.get_attribute('type')
                    if _type != in_type:
                        raise WebUIWrongArgTypeException("Label does not\
                            match with the %s type or element" % _type)
                return element
            #import pdb;pdb.set_trace()
            raise WebUIWrongArgTypeException(
                'Element not found label: ' + label)
        return element

    def __set_return_by_element(self, element):
        """
        Set checker returned True if element gave is not None or False

        **internal**

        Args:
            element (obj): Selenium object

        Returns:
            bool: True if element is not None or False.
        """
        if element:
            self.checker.set_returned(True)
            return True
        self.checker.set_returned(False)
        return False

    def __led_satus_from_img(self, led_img_url):
        file_name = os.path.split(led_img_url)[1]
        if file_name == LED_GREEN_IMG:
            return "Green"
        elif file_name == LED_BLACK_IMG:
            return 'Black'
        elif file_name == LED_RED_IMG:
            return 'Red'
        else:
            raise KaliExceptionWebUiDriver('No valid led file')

    def __angular_status(self):
        try:
            java_script_to_load_angular = """
            var injector = window.angular.element('body').injector();
            var $http = injector.get('$http');
            return ($http.pendingRequests.length === 0);"""
            angualar_js = "return angular.element(document).injector()" +\
                ".get('$http').pendingRequests.length === 0"
            return self.driver.execute_script(angualar_js)
        except WebDriverException:
            # No Angular Founded
            return True

    def __js_document_status(self):
        return self.driver.execute_script("return document.readyState")

    def __wait_js_angular(self):
        timeout_start = time.time()
        timeout = 1.0
        if self.check_timeout:
            timeout = self.check_timeout
        while not self.__angular_status() or not self.__js_document_status():
            if time.time() > timeout_start + timeout:
                break
        return True

    # METHODS

    # angular wait return
    # angular.element(document).injector().get('$http').pendingRequests.length
    # === 0

    def get_leds_status(self, visible):
        """ To get the actual status of led in homepage

        Args:
            visible(bool): if it is set to False, it checks the status of the LED whether it is visible or not

        """
        self.__wait_js_angular()
        led_status_dict = {}
        for key in LED_DICT:
            led_status_dict[key] = {}
            if visible:
                section = self.__find_visible_by(
                    By.XPATH, "//h4[contains(text(), '%s')]" % key)
            else:
                section = self.driver
            for led_label in LED_DICT[key]:
                labeldiv = section.find_element_by_xpath(
                    "//h4[contains(text(), '%s')]" +
                    "/following::div[contains(text(), '%s')]" %
                    (key, led_label))

                img_div = labeldiv.find_element_by_xpath(
                    ".//following-sibling::div")
                led_status = None
                timeout_start = time.time()
                while not led_status or led_status == 'Black':
                    led_status_img = img_div.find_element_by_css_selector(
                        "img")
                    try:
                        led_status_image = led_status_img.get_attribute("src")
                    except StaleElementReferenceException:
                        continue
                    led_status = self.__led_satus_from_img(led_status_image)
                    if time.time() > timeout_start + 2:
                        break
                led_status_dict[key][led_label] = led_status
        return led_status_dict

    def led_status(self, section, label, visible):
        """
        Set checker returned with the color of the led are you checking for
        Args:
            section (str): Section of leds (see LED_DICT on pages_data.py)
            label (str): Label of the specific led to check
            visible (bool): needed if led is not visible

        """
        leds_status_dict = self.get_leds_status(visible)
        try:
            self.checker.set_returned(leds_status_dict[section][label])
        except KeyError as e:
            raise KaliExceptionWebUiDriver("No Led found <%s>" % e)

    def led_is(self, section, label, color, visible):
        """Check if Led color is the same given.

        Args:
            section (str): Section of leds (see LED_DICT on pages_data.py)
            label (str): Label of the specific led to check
            color (str): The aspetted led color
            visible (bool): needed if led is not visible

        Return:
            The get_result(bool): true or false

        """
        self.checker.set_expected(color)
        self.led_status(section, label, visible)
        return self.get_result('equal')

    def led_is_green(self, section, label, visible=True):
        """Check if led is Green.

        Args:
            section (str): Section of leds (see LED_DICT on pages_data.py)
            label (str): Label of the specific led to check
            visible (bool): needed if led is not visible
        Return:
            The get_result(bool): true or false

        """
        return self.led_is(section, label, 'Green', visible)

    def led_is_red(self, section, label, visible=True):
        """Check if led is Red.

        Args:
            section (str): Section of leds (see LED_DICT on pages_data.py)
            label (str): Label of the specific led to check
            visible (bool): needed if led is not visible
        Return:
            The get_result(bool): true or false
        """
        return self.led_is(section, label, 'Red', visible)

    def led_is_black(self, section, label, visible=True):
        """Check if led is Blac.

        Args:
            section (str): Section of leds (see LED_DICT on pages_data.py)
            label (str): Label of the specific led to check
            visible (bool): needed if led is not visible
        Return:
            The get_result(bool): true or false
        """
        return self.led_is(section, label, 'Black', visible)

    def page_refresh(self):
        self.driver.refresh()

    def scroll_on_save(self):
        save_button = self.driver.find_element_by_css_selector(
            'div.col-lg-8:nth-child(4) > button:nth-child(2)')
        self.driver.execute_script(
            "return arguments[0].scrollIntoView();", save_button)

    def scroll_down(self, popup=None, label=None):
        """Util to scroll the web page to the bottom.

        Args:
            popup (bool): if setted will scroll the popup
            label (str): mandatory if popup is true, the label of 
             the element  to scroll to

        """

        if popup:
            element = self.__get_element(label, 'input')
            self.driver.execute_script(
                "return arguments[0].scrollIntoView();", element)
        else:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

    def scroll_modal(self):
        """Use it to scroll the modal popup"""
        # modal-content
        sleep(1)
        self.driver.execute_script(
            "return $('.slide-frame').scrollTop($('.slide-frame').height() +\
 $('.modal-body').height()+10);")
        sleep(3)

    def press_key(self, key, n=1):
        """
        :param key: input keyboard parameter
        Possible key parameters:
        { ADD, ALT, ARROW_DOWN ,ARROW_LEFT, ARROW_RIGHT, ARROW_UP,
        BACK_SPACE, CANCEL, CLEAR, COMMAND, CONTROL,DECIMAL ,DELETE ,DIVIDE
        DOWN ,END ,ENTER ,EQUALS ,ESCAPE ,F1 ,F10 ,F11 ,F12 ,F2 ,F3 ,F4 ,F5
        ,F6 ,F7 ,F8 ,F9 ,HELP ,HOME ,INSERT ,LEFT ,LEFT_ALT ,LEFT_CONTROL,
        LEFT_SHIFT ,META ,MULTIPLY ,NULL,NUMPAD0 ,NUMPAD1 ,NUMPAD2 ,NUMPAD3
        ,NUMPAD4 ,NUMPAD5 ,NUMPAD6 ,NUMPAD7 ,NUMPAD8 ,NUMPAD9 ,PAGE_DOWN
        ,PAGE_UP ,PAUSE ,RETURN ,RIGHT ,SEMICOLON ,SEPARATOR ,SHIFT ,SPACE
        ,SUBTRACT ,TAB ,UP  }

        :param n: specifies the number of times the key is pressed
        
        :return: True or False

        """
        keyboard_key = Keys.__str__(key)
        actions = ActionChains(self.driver)
        for _ in range(n):
            actions = actions.send_keys(keyboard_key)
        try:
            actions.perform()
            return True
        except:
            # TODO: specify a right exception
            return False

    def open_url(self, url):
        """Use it to directly open a url in the browser."""
        self.driver.get(url)

    def refresh(self):
        """Use it to refrash the current page."""
        self.is_logged = False
        rf_button = self.driver.find_element_by_css_selector(
            '.centerStyle > button:nth-child(1)')
        while True:
            try:
                rf_button.click()
                return
            except ElementClickInterceptedException:
                continue

    def click_on_save(self, ):
        """Use it to click the Save button."""
        save_btn = self.__find_visible_by(By.XPATH,
                                          "//*[contains(text(), 'Save')]")
        if save_btn:
            save_btn.click()
            return True
        return False

    def click_on_cancel(self):
        """Use it to click on Cancel button."""
        cancel_btn = self.__find_visible_by(By.CSS_SELECTOR,
                                            ".btn[value='Cancel']")
        if cancel_btn:
            cancel_btn.click()
            return True
        return None

    def click_on_logout(self):
        """Use it to click on Logout button."""
        if self.click_button('ADMIN') and self.click_button('LOGOUT'):
            self.is_logged = False
            return True

    def __find_clickable(self, label):
        element_present = EC.element_to_be_clickable(
            (By.XPATH, "//*[normalize-space(.)='" + label + "']"))

    def click_button(self, label, double=False, button=None, hidden=False):
        """
        Click on visible button with have the text of the label.

        Args:
            label (str): the text inside the button
            double (bool): double click on element
            button (element): Used to directly click on given Selenium button element
            hidde (bool): To specify if the button is visible or not

        Returns:
            True: if the button was found
            False: if no button found
        """
        self.__wait_js_angular()
        actionchains = None
        if double:
            actionchains = webdriver.ActionChains(self.driver)
        if label in INPUTS_DICT:
            if INPUTS_DICT[label]['type'] == BTN:
                button = self.__find_visible_by(INPUTS_DICT[label]['by'],
                                                INPUTS_DICT[label]['value'],
                                                hidden)
        else:
            element_present = EC.element_to_be_clickable(
                (By.XPATH, "//*[normalize-space(.)=\"" + label + "\"]"))
            try:
                WebDriverWait(self.driver, self.check_timeout).until(
                    element_present)
                button = self.driver.find_element_by_xpath(
                    "//*[normalize-space(.)=\"" + label + "\"]")
            except TimeoutException:
                # is a input ??
                element_present = EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "*[value=\"" + label + "\"]"))
                WebDriverWait(self.driver, self.check_timeout).until(
                    element_present)
                button = self.driver.find_element_by_css_selector(
                    "*[value=\"" + label + "\"]")
        try:
            if not double:
                self.driver.execute_script(
                    "return arguments[0].scrollIntoView(false);", button)
                button.click()
                return True
            actionchains.double_click(button)
            return True
        except WebDriverException:
            # print("EXCEPTION: %s" % e)
            timeout_start = time.time()
            timeout = 1.0
            if self.check_timeout:
                timeout = self.check_timeout
            while time.time() < timeout_start + timeout:
                try:
                    if not double:
                        button.click()
                        return True
                    actionchains.double_click(button)
                    return True
                except WebDriverException:
                    continue
            raise KaliExceptionWebUiDriver('Button not found')

    def click_to_close(self):
        """Use it to click on 'x' or on Close button, to close the modal popup.
        """
        self.ng_click(function='dismiss()')

    def ng_click(self, function):
        """ Click button only when the ng-click function are filled
            Args:
                function(str): Angular function to trigger on click

        """
        element = self.__find_visible_by(By.CSS_SELECTOR,
                                         "*[ng-click='" + function + "']")
        element.click()

    def resize_window(self, sizes):
        """ Resize the browser window
        Args:
            sizes (tuple): width, height in pixels
        """
        self.driver.set_window_size(sizes[0], sizes[1])

    def set_value(self, value, label=None, input_type=None, obj=None):
        """
        Sets value to a input element

        Args:
            label (str): The visible label string that referred to input
            value (str/bool): The value you wants to put inside the input
                If input was a combo select, value must be
                the string matching the option to be selected
            input_type : TDB
            obj : TDB
        Returns:
            bool: True if element founded and value set

        Raises:
            WebUIWrongArgTypeException
        """
        element = obj
        in_type = input_type
        if label in INPUTS_DICT and not obj:
            selected = INPUTS_DICT[label]
            element = self.__find_visible_by(selected['by'], selected['value'])
            in_type = selected['type']
        if element:
            if in_type == 'text':
                element.clear()
                element.send_keys(value)
            elif in_type == 'checkbox':
                if not isinstance(value, bool):
                    raise WebUIWrongArgTypeException(
                        "%s value must be boolean"
                        % label)
                if (value is False and element.is_selected()) or \
                        (value is True and not element.is_selected()):
                    element.click()
            elif in_type == 'select':
                Select(element).select_by_visible_text(value)
            else:
                return False
        return True

    def set_select(self, label, option):
        """
        Selects the option matching 'option' for the combo-box labeled 'label'

        Args:
            label (str): The visible label string that referred to select box
            option (str): The option you wants to select

        Returns:
            bool: True/False if element is present and set
        """
        element = self.__get_element(label, _type='select')

        if element:
            return self.set_value(option, obj=element, input_type='select')

    def set_input(self, label, value):
        """
        Sets value to a input element

        Args:
            label (str): The visible label string that referred to input
            value (str): The value you wants to put inside the input

        Returns:
            bool: True/False if element is present and set
        """
        element = self.__get_element(label, 'input')
        if element:
            return self.set_value(value, obj=element, input_type='text')

    def set_checkbox(self, label, check):
        """
        Check un check the checkbox

        Args:
            label (str): The visible label string that referred to input
            check (bool): True if you want check False if want to uncheck

        Returns:
            bool: True/False if element is present and set
        """
        element = self.__get_element(label, 'checkbox')
        if element:
            return self.set_value(check, obj=element, input_type='checkbox')

    def set_datetime(self, date):
        """
        Set given date in correct way to next dateTime input

        Args:
            label (str): The visible label string that referred to input
            date (str): Date tou want to set (Eg. 2018/04/20 13:00)
        Returns:
            bool: True/False if element is present and set
        #TODOO use the label to find specific input dateTime
        """
        element = self.__find_visible_by(By.ID, 'dateTime')
        self.set_value(value=date, input_type='text', obj=element)

    def upload_file(self, file_path, hidden=False):
        """Set file to upload

        Args:
            file_path (str): The file path location
            hidden (bool): if the input field is not visible
        """
        element = self.__find_visible_by(
            By.CSS_SELECTOR, 'input[type="file"]', hidden=hidden)
        if not element:
            raise WebUIMissArgException('No input file found in page!')
        try:
            element.send_keys(file_path)
        except WebDriverException:

            raise KaliExceptionWebUiDriver('File: %s not found' % file_path)
        return True

    def click_to_download(self, button_label, file_name=None):
        """
        Download file in download folder

        insert in "check returned" the name of downloaded file

        Args:
            button_label(str): **mandatory** The button label
            file_name(str): rename the download file, with this string

        """

        self.click_button(button_label)
        element_present = EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".showSweetAlert.visible"))
        WebDriverWait(self.driver, self.check_timeout).until(
            element_present)
        sleep(1)
        return_file_name = max(glob.iglob('%s/*.*' % self.download_folder),
                               key=os.path.getctime)
        if file_name:
            new_file_path_name = os.path.join(self.download_folder, file_name)
            shutil.move(return_file_name, new_file_path_name)
            return_file_name = new_file_path_name
        self.checker.set_returned(return_file_name)

    def find_select(self, label):
        """
        Check if combo select box is present in the current page.

        if the select combo was found, "checker returned" is True else is False

        Args:
            label(str): The visible label string that referred to combo select

        Returns:
            bool: True/False if the select combo box element was found
        """
        try:
            self.__get_element(label, 'select')
            self.checker.set_returned(True)
        except TimeoutException:
            self.checker.set_returned(False)

    def find_input(self, label):
        """
        Check if input is present in the current page.
        if the input was found, "checker returned" is True else is False

        Args:
            label(str): The visible label string that referred to input

        """
        try:
            self.__get_element(label, 'text')
            self.checker.set_returned(True)
        except TimeoutException:
            self.checker.set_returned(False)

    def find_checkbox(self, label):
        """
        Check if checkbox is present in the current page.

        if the checkbox was found, "checker returned" is True else is False

        Args:
            label(str): The visible label string that referred to checkbox


        """
        try:
            self.__get_element(label, 'checkbox')

            self.checker.set_returned(True)
            return True
        except TimeoutException:
            self.checker.set_returned(False)
            return False

    def checkbox_status(self, label):
        """Use it to get the status of a checkbox.

        Args:
            label (str): the checkbox label

        Return:
            bool: true if is checked or false if not

        Notes:
            the result of the check is set in set_returned method


        """
        if self.find_checkbox(label):

            checkbox = self.__get_element(label, 'checkbox')

            if checkbox.is_selected():
                self.checker.set_returned(True)
                return True
            else:
                self.checker.set_returned(False)
                return False

    def get_value(self, label, _type=None):
        """
        Get value of a input element

        Set in Kali returned, the value of the input, None if element not found

        Args:
            label (str): **mandatory** The visible label string that referred
                            to input
            _type (str): the type of input (text,select,checkbox)

        Returns:
            True: Element is present
            False: Element not found

        """
        self.__wait_js_angular()
        found = self.__get_element(label, _type)
        if found:
            if found.tag_name == 'input':
                if found.get_attribute('type') == 'checkbox':
                    self.checker.set_returned(found.is_selected())
                    return found.is_selected()
                self.checker.set_returned(found.get_attribute('value'))
                return found.get_attribute('value')
            elif found.tag_name == 'select':
                pass  # TODO
            self.checker.set_returned(found.text)
            return found.text
        self.checker.set_returned('')
        return False

    def get_value_and_check(self, label, expected, _type=None, result='equal'):
        """
        Check if element (input, select, tc ecc) have the gived value

        Args:
            label(str): the element reference label
            expected(str): The value you expect to find
            _type(str): The elemnt type you need to check in eg(input,td....)
            result(str): TThe result of the check you expected
        """
        self.get_value(label, _type)
        self.set_check(expected)
        self.get_result(result)

    def find_text(self, text):
        """
        Check if text is present inside Html Dom.
        If is a value of tag (button) or is the text inside tag is indifferent

        Set Kali returned: True if text is present, otherwise False

        Args:
            text (str): The string you are looking for.

        Returns:
            True: if text was found
            False: if text is not present in the page.

        """
        #//*[contains(.,"successfully exported")]')
        self.__wait_js_angular()
        text = text.strip()
        element = self.__find_visible_by(
            By.XPATH, '//*[contains(.,"' + text + '")]')
        if element:
            self.checker.set_returned(True)
            return True
        element_present = EC.visibility_of_element_located(
            (By.XPATH, "//*[normalize-space(.)='" + text + "']|//*[@value='" +
                text + "']|//*[@placeholder='" + text + "']|//*[text()='" +
             text + "']"))
        try:
            WebDriverWait(self.driver, self.check_timeout).until(
                element_present)
        except TimeoutException:
            self.checker.set_returned(False)
            return False
            self.checker.set_returned(True)
            return True

    def find_text_and_check(self, text, expected=True, result='equal'):
        """Search text in page.

        Args:
            text(str): Text want to find in page
            expected (bool): Expected result
            result (str): Serach type (same of checkers)

         """
        self.find_text(text)
        self.set_check(expected)
        return self.get_result(result)

    def find_element(self, _type, value):
        element_attribute = ELEMENT_DICT[_type]
        search_path = "%s[%s$='%s']" % (_type, element_attribute, value)
        if self.__find_visible_by(By.CSS_SELECTOR, search_path):
            self.checker.set_returned(True)
            return True
        self.checker.set_returned(False)
        return False

    def find_element_and_check(self, _type, value, expected=True):
        """ Looking for a html element in the page.

        Args:
            _type (str): the type of the element lik: input, select, td
            value (str):  the value inside the element
            expected (bool): Expected result (true if you think to find the
            element or false if want to check that the element is
            no present)

        """
        self.find_element(_type, value)
        self.set_check(expected)
        self.get_result('equal')

    def check_login(self, psw):
        self.set_value(psw, label='Password')
        self.click_button('Login')
        if self.__find_visible_by(
                INPUTS_DICT['Home_Page']['by'],
                INPUTS_DICT['Home_Page']['value']):
            self.is_logged = True
            self.checker.set_returned(True)
            return True
        self.checker.set_returned(False)
        return False

    def send_key(self, key_button):
        element = self.driver.switch_to.active_element
        key_to_send = None
        try:
            key_to_send = getattr(Keys, key_button)
        except AttributeError:
            key_to_send = key_button
        element.send_keys(key_to_send)

    # MACRO

    def macro_wait_and_check_uptime(self,
                                    wait_minutes=1,
                                    time_label='Up Time',
                                    click_button=None):
        new_date = None
        datetime_obj = None
        ele_text = self.get_value(label=time_label, _type='td')
        string_time = "up "
        if ('hour' in ele_text and not 'hours' in ele_text):
            string_time += "%H hour"
        elif 'hours' in ele_text:
            string_time += "%H hours"
        if ', ' in ele_text:
            string_time += ', '
        if 'minute' in ele_text and not 'minutes' in ele_text:
            string_time += "%M minute"
        elif 'minutes' in ele_text:
            string_time += "%M minutes"
        # TODO WEEKS AND DAYS

        datetime_obj = datetime.strptime(ele_text, string_time)
        date_up = datetime_obj + timedelta(minutes=wait_minutes)
        new_hour = date_up.strftime('%H')
        new_mins = date_up.strftime('%M')
        if new_hour.startswith('0'):
            new_hour = new_hour[1:2]

        if int(new_mins) > 0:
            new_date = "up %s hours, %s minutes" % (new_hour, new_mins)
        else:
            new_date = 'up %s hours' % new_hour
        # print(new_date)
        sleep(60 * wait_minutes)
        if click_button:
            self.click_button(click_button)
        # print(self.get_value(label=time_label, _type='td'))
        self.get_value_and_check(
            label=time_label, _type='td', expected=new_date)

    def macro_ip_configurator(self,
                              side_selection,
                              side_a,
                              ip_a,
                              netmask,
                              gateway,
                              dns_1,
                              dns_2,
                              twowire,
                              side_b=None,
                              ip_b=None):
        fuel_pos = ['//*/input[@name="spot1Disp"]',
                    '//*/input[@name="spot2Disp"]']

        ip_conf = ['//*/input[@name="SPOT1"]',
                   '//*/input[@name="SPOT2"]',
                   '//*/input[@ng-model="currentConfig.PBLNETMSK"]',
                   '//*/input[@ng-model="currentConfig.gateway"]',
                   '//*/input[@ng-model="currentConfig.DNS1"]',
                   '//*/input[@ng-model="currentConfig.DNS2"]']

        media = ['//*/input[@name="mediaTable-sidea-terminalId"]',
                 '//*/input[@name="mediaTable-sidea-pumpId"]',
                 '//*/input[@name="mediaTable-sideb-terminalId"]',
                 '//*/input[@name="mediaTable-sideb-pumpId"]',
                 '//*/input[@name="mediaTable-idleLoopEnabled"]',
                 '//*/input[@name="mediaTable-idleLoopDelay"]',
                 '//*/input[@name="mediaTable-idleLoopDelayFromBusy"]',
                 '//*/input[@name="mediaTable-busyLoopEnabled"]',
                 '//*/input[@name="mediaTable-busyLoopDelay"]',
                 '//*/input[@name="mediaTable-serverIp"]',
                 '//*/input[@name="mediaTable-volume"]']

        save_media = '//*/button[@ng-click="setMediaApp(mediaTable)"]'
        save_date_time = '//*/button[@ng-click="setDateTimeZone()"]'
        save_wizard = '//*/button[@class="confirm"]'

        wiz_tabs = ['//*/div[@ng-switch-when="omnia"]',
                    '//*/legend',
                    '//*/div[@ng-switch-when="cloud"]']

        date_label = '//*/input[@id="dateTime"]'
        try:
            if side_selection == "single":
                for element in self.driver.find_elements_by_name(
                        "Dispenser_Type"):
                    if element.is_displayed():
                        Select(element).select_by_visible_text("Single side")
                        break
            elif side_selection == "dual":
                for element in self.driver.find_elements_by_name(
                        "Dispenser_Type"):
                    if element.is_displayed():
                        Select(element).select_by_visible_text("Dual side")
                        break
        except ElementNotInteractableException:
            raise WebUIWrongPageException(
                "Wrong WebUI page selected, please check")
        # Two wire mode selection
        try:
            Select(self.driver.find_element_by_name("TwoWire_Mode")
                   ).select_by_visible_text(twowire)
        except NoSuchElementException:
            pass
        # IP CONFIGURATION
        self.__find_and_set_by_xpath(fuel_pos[0], side_a)
        self.__find_and_set_by_xpath(ip_conf[0], ip_a)
        if side_selection == "dual":
            if side_b and ip_b:
                # FUEL POSITION AND IP ADD SIDE B
                self.__find_and_set_by_xpath(fuel_pos[1], side_b)
                self.__find_and_set_by_xpath(ip_conf[1], ip_b)
            else:
                raise WebUIMissArgException("Missed Required Args")
        # NETMASK
        self.__find_and_set_by_xpath(ip_conf[2], netmask)

        # GATEWAY
        self.__find_and_set_by_xpath(ip_conf[3], gateway)
        # SCROLLING PAGE DOWN
        self.scroll_on_save()

        # DNS
        self.__find_and_set_by_xpath(ip_conf[4], dns_1)
        self.__find_and_set_by_xpath(ip_conf[5], dns_2)
        # Next ==>
        next_btn_present = EC.presence_of_element_located(
            (By.XPATH, '//*/a[@ng-click="handleNext(mediaTableInWizard)"]'))
        WebDriverWait(self.driver, self.check_timeout).until(next_btn_present)

        try:
            sleep(1)
            if self.driver.find_element_by_xpath(self.next).is_displayed():
                self.driver.find_element_by_xpath(self.next).click()
        except NoSuchElementException:
            pass

        # Save
        try:
            sleep(1)
            if self.driver.find_element_by_xpath(
                    self.omnia_save).is_displayed():
                self.driver.find_element_by_xpath(self.omnia_save).click()
        except NoSuchElementException:
            pass

    def macro_login(self, password=None):
        """
        Automatic login in webui.

        """

        element_present = EC.presence_of_element_located(
            (By.XPATH, '/html/body/div/form/div[3]/span[2]'))
        WebDriverWait(self.driver, self.check_timeout).until(element_present)
        ppn = self.__find_visible_by(By.XPATH,
                                     '/html/body/div/form/div[3]/span[2]')
        if not password:
            password = ppn.text[-6:]
        self.check_login(psw=password)

    def macro_cloud_remote_config(self,
                                  gvr_id=None,
                                  nickname=None,
                                  inc_logs_enable=None,
                                  wheninc=None,
                                  click_cancel=False,
                                  click_save=True,
                                  pre_check=True, ):
        """Use this function to configure the GVR CLoud/Remote Management page.

        Args:
            gvr_id (int): 'GVR ID' in the page
            nickname (str): 'Omnia Nickname' in the page
            inc_logs_enable (bol): 'Incremental logs' checkbox in the page
            wheninc (int): 'Download Logs Every (mins)' in the page
            click_cancel (bool): if set to true cancel button will be clicked
            click_save (bool): if set to true save button will be clicked
            pre_check (bool): Determinate if must to be do a python pre check
            off the parameters gave

        Returns:
            bool: Description of return value

        Raises:
            WebUIWrongArgTypeException: raised when input is not well formatted

        """

        if gvr_id:
            if pre_check:
                try:
                    int(gvr_id)
                except ValueError:
                    raise WebUIWrongArgTypeException(
                        'GVR ID: must be a integer')
            site_id_element = self.find_visible_by(
                "find_element_by_id", "siteid")
            site_id_element.clear()
            site_id_element.send_keys(gvr_id)
        if nickname:
            nick_element = self.__find_visible_by(By.ID, "FDT_Nickname")
            nick_element.clear()
            nick_element.send_keys(nickname)
        if inc_logs_enable is not None:
            try:
                bool(inc_logs_enable)
            except ValueError:
                raise WebUIWrongArgTypeException(
                    'Incremental logs: must be a boolean')
            inc_checkbox = self.find_visible_by("incrementalLogsEnabled", 'id')
            if (inc_logs_enable is False and inc_checkbox.isSelected()) or \
                    (inc_logs_enable is True and not inc_checkbox.isSelected()):
                inc_checkbox.click()
        if wheninc:
            if pre_check:
                try:
                    int(wheninc)
                except ValueError:
                    raise WebUIWrongArgTypeException(
                        'Download Logs Every (mins): must be a integer')
            when_inc_element = self.find_visible_by("wheninc", 'id')
            when_inc_element.clear()
            when_inc_element.send_keys(wheninc)
        if click_cancel:
            self.click_cancel()
        if click_save:
            self.click_save()
