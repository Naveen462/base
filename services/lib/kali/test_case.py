# -*- coding: utf-8 -*-
"""
Abstract KALI Test Case
=======================

"""
from .addons.dbus.addon import KaliDbusOmniaAddon
from .addons.main.addon import KaliMainAddon
from .addons.omnia_bash.addon import KaliBashAddon
from .addons.omnia_log.addon import KaliLogOmniaAddon
from .addons.omnia_picaso.addon import KaliPicasoAddon
from .addons.omnia_serial.addon import KaliSerialOmniaAddon
from .addons.omnia_ftclient.addon import KaliFTClient
from .addons.webui.addon import KaliWebUiAddon
from .define import VALID_KEYS_COMPATIBILIES
from .exceptions import KaliExceptionKeyError
from .exceptions import KaliExceptionTestCase


class KaliTestResultManager:
    """Class to create a test result.

    Args:
        steps_result (list): list of bool representing steps results.
        result (bool):  result of test case.
    """

    def __init__(self):
        """Class setup."""
        self.steps_result = []
        self.result = None

        self._closed = False

    def add_passed(self):
        """
        Register a step as 'passed'.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTestCase` if TestCase is closed.
        """
        if self._closed:
            raise KaliExceptionKeyError(
                'Cannot register step result: TestCase is closed.')
        self.steps_result.append(True)

    def add_failed(self):
        """
        Register a step as 'failed'.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTestCase` if TestCase is closed.
        """
        if self._closed:
            raise KaliExceptionKeyError(
                'Cannot register step result: TestCase is closed.')
        self.steps_result.append(False)

    def close(self):
        """
        Calculate test result and deny registration of additional step results.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTestCase` if TestCase is already
            closed or no steps results have been registered.
        """
        if self._closed:
            raise KaliExceptionKeyError(
                'Cannot close TestCase: it is already closed')
        if not self.steps_result:
            raise KaliExceptionKeyError(
                'Cannot close TestCase: no steps results registered')
        if False in self.steps_result:
            self.result = False
        else:
            self.result = True
        self._closed = True

    def is_closed(self):
        """
        Check status.

        Returns:
            bool: True if TestCase is closed, False otherwise.
        """
        return self._closed


class KaliTestCase:
    """Main object ot create new test for Kali automation"""

    def __init__(self, kali, logger, test_title, test_number, **kwargs):
        """
        Args:
            kali (obj): The kali object to run tests
            logger (obj): A object logger to write the logs
            test_title (str): The title of the test
            test_number (str): The string number of the test
            kwargs (dict): All need to setup new addon to do the test
        """
        self.kali = kali
        self.tags = []
        self.test_title = test_title
        self.logger = logger
        self.test_number = test_number
        self.compatibilities = {}
        self.kwargs = kwargs
        self.attended = False
        self.destructive_list = []
        self.__notes = ""
        self._test_duration = 0.0
        self.__dict__.update(**kwargs)

    def set_notes(self, note):
        """
        Add notes to test.

        Args:
            note(str): the note text
        """
        self.__notes += note

    def get_notes(self):
        """Get the test note"""

        return self.__notes

    def set_tags(self, tags):
        """
            Set a list of tags

            Params:
                tags(list): list of tags
        """
        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
            self.tags = tags

    def add_tags(self, tags):
        """
            Add a tag to tags list

            Params:
                tags(list): list of tags
        """
        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
            self.tags.extend(tags)

    def set_duration(self, seconds):
        """To determinate the duration of test in seconds.
            Args:
                seconds (float): the duration time of the test
        """
        try:
            self._test_duration = float(seconds)
        except TypeError:
            self.logger.error("Set Test duration Wrong Type")

    def get_duration(self):
        """Return the test duration time in seconds."""
        return self._test_duration

    def set_distructive_lan(self):
        """Set Disctructive lan mode on."""
        self.destructive_list.append('Lan')

    def set_distructive_media(self):
        """Set Disctructive media mode on."""
        self.destructive_list.append('Media')

    def set_distructive_cloud(self):
        """Set Disctructive cloud mode on."""
        self.destructive_list.append('Cloud')

    def is_destructive(self, mode=None):
        """
        To determine if test is destructive for something

        Args:
            mode (str): The area you want to check if will be destroyed
            ['Lan', 'Media', 'Cloud', .... ]


        Returns:
            bool: if mode gived True if the mode is discructive or False if not
            list: if mode is None return the entire list

        """
        if mode:
            return mode in self.destructive_list
        return self.destructive_list

    def set_attended(self, flag):
        """
        Set the flag attended

        Args:
            flag (bol): True if test is attended or False if the test is
            automatable

        """
        self.attended = flag

    def is_attended(self):
        """To determinate if test is attended

            Returns:
                bool: True is attended by user action False is not

        """

        return self.attended

    def required_ots(self, ots_label):
        """
        Add this methond inside the sutup of tests need:
        the OminiaTestServerClient


        Args:
            ots_label (str): The name used to create the Otsc object

        """
        self.__add_otsc(ots_label)

    def set_new_ots(self, ots_label, ip, port):
        """To create new ots client

        ots_ip (str): the ip off ots
        ots_port (str): ots port for connection
        """
        self.__add_otsc(ots_label, ip, port)

    def required_webui_addon(self, addon_name):
        """
        Add this on KaliTestCase's objects setup method if you
        need to use: :src:webui addon

        Args:
            addon_name (str): The name/key of the webui addon you want to
                use/create

        Required to create addon:
            kwargs:'ip' and 'port'
        """
        self.__add_addon(addon_name, KaliWebUiAddon, 'add_omnia_webui_addon')

    def required_omnia_dbus_addon(self, addon_name):
        """
        Add this on KaliTestCase 's objects setup method if you need to use:
        omnia dbus addon

        Args:
            addon_name (str): The name/key of the webui addon you want to
            use/create

        Required to create addon:
            kwargs:'ip' and 'port'

        """
        self.__add_addon(addon_name, KaliDbusOmniaAddon,
                         'add_omnia_dbus_addon')

    def required_omnia_main_addon(self, addon_name):
        """
        Add this on KaliTestCase 's objects setup method if you need to use:
        Main addon to controll OTS.

        Args:
            addon_name (str): Key value to identify addon.

        Required to create addon:
            kwargs: 'command', 'service', 'user', 'key_label'

        """
        self.__add_addon(addon_name, KaliMainAddon, 'add_omnia_main_addon')

    def required_omnia_serial_addon(self, addon_name):
        """
        Add this on KaliTestCase 's objects setup method if you need to use:
        Omnia serial addon.

        Args:
            key (str): Key value to identify addon

        Required to create addon:
            **kwargs**: com_port, baud_rate

        Raises:
            KaliExceptionKeyError::exc:`src.exceptions.KaliExceptionKeyError`
                if key is already present.
            KaliExceptionSetupError::exc:`src.exceptions.KaliExceptionSetupError`
                if addon setup fails.

        """
        # kwargs_list = ['com_port', 'baud_rate']
        self.__add_addon(addon_name, KaliSerialOmniaAddon,
                         'add_omnia_serial_addon')

    def required_omnia_log_addon(self, addon_name):
        """
        Add this on KaliTestCase 's objects setup method if you need to use:
        omnia log addon

        Args:
            key (str): Key value to identify addon.

        Required to create addon:
            ip (str): ip address for addon setup.
            port (int): port number for addon setup.

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError:
            :exc:`src.exceptions.KaliExceptionKeyError` if key is already
                present.
            KaliExceptionSetupError:
            :exc:`src.exceptions.KaliExceptionSetupError` if addon setup fails.
        """
        self.__add_addon(addon_name, KaliLogOmniaAddon, 'add_omnia_log_addon')

    def required_omnia_bash_addon(self, addon_name):
        """
        Add this on KaliTestCase 's objects setup method if you need to use:
         :exc:`~src.addons.omnia_bash.addon` object to handle omnia bash addon


        Args:
            addon_name (str): Key value to identify addon.

        Required to create addon:
            **kwargs**: hostname,port

        Raises:
            KaliExceptionKeyError:
            :exc:`src.exceptions.KaliExceptionKeyError` if key is arleady
                present.
            KaliExceptionSetupError:
            :exc:`src.exceptions.KaliExceptionSetupError` if addon setup fails.
        """
        self.__add_addon(addon_name, KaliBashAddon, 'add_omnia_bash_addon')

    def required_omnia_fts_client_addon(self, addon_name):
        """
        Add this on KaliTestCase 's objects setup method if you need to use:
        :exc:`~src.addons.omnia_ftclient.addon` object to handle ftclient addon

        Args:
            addon_name (str): Key value to identify addon.

        Required to create addon:
            **kwargs**: hostname,port

        Raises:
            KaliExceptionKeyError:
            :exc:`src.exceptions.KaliExceptionKeyError` if key is arleady
                present.
            KaliExceptionSetupError:
            :exc:`src.exceptions.KaliExceptionSetupError` if addon setup fails.
        """
        self.__add_addon(addon_name, KaliFTClient,
                         'add_omnia_fts_client_addon')

    def required_omnia_picaso_addon(self, addon_name):
        """
        Add this on KaliTestCase 's objects setup method if you need to use:
        omnia picaso addon

        Args:
            addon_name (str): Key value to identify addon.

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError: :exc:`~src.exceptions.KaliExceptionKeyError`
             if key is already present.
            KaliExceptionSetupError:
            :exc:`~src.exceptions.KaliExceptionSetupError` if addon setup fails
        """
        self.__add_addon(addon_name, KaliPicasoAddon, 'add_omnia_picaso_addon')

    def add_required_addons(self, addons_list):
        """To add multiple required addons by the packege addon and kali label
        name

        Args:
            addons_list (list): A list of tuple within the addon packege name
                and the addon key/label name for Kali

        eg: add_required_addons([("omnia_log", 'aa'), ('omnia_bash','bb'),
         ('webui', 'cc')])

        """
        for addon, name in addons_list:
            getattr(self, "required_%s_addon" % addon)(name)

    def __add_otsc(self, ots_label, ip=None, port=None):
        """Check and add eventualy ots client for Kali

        Args:
            ots_label(str): ots connection key
            ip (str): ots ip
            port (str): ots port
        """
        if not self.kali.check_connection_ots(ots_label):
            if not ip:
                ip = self.ots_ip
            if not port:
                port = self.ots_port
            connected = self.kali.start_connection_ots(ots_label, ip, port)
            if not connected:
                self.logger.error("Wrong ots_ip or ots_port setted")

    def __add_addon(self, addon_name, addon_class_obj, add_method):
        """
        Add or update or do nothing to the kali addon

        Args:
            addon_name (str): the key/name of the kali addon
            addon_class_obj (obj): The orginal addon class
            addon_method (str): The name of add addon method of Kali object
        """

        if addon_name not in self.kali.addons.keys():
            getattr(self.kali, add_method)(addon_name, **self.kwargs)
        # if will find some difference, the addon will be reloaded
        elif addon_name in self.kali.addons.keys():
            addon = self.kali.get_addon_by_name(addon_name)
            data_dict = self.kwargs
            addon_dict = addon.__dict__
            differences = {key: data_dict[key]
                           for key in addon_dict if key in data_dict}
            if len(differences) > 0:
                self.kali.reload_addon(addon_name, **differences)

    def get_compatibilities_dict(self):
        """Return the a dict within all criticity."""
        return self.compatibilities

    def set_compatibility(self, comp_key, comp_val):
        """Use it to add specific compatibility version to test or use it
            to declare the dustrutive actions inside test.

        Args:
            comp_key('str'): Key must be present in VALID_KEYS_COMPATIBILIES
            list
            comp_val (True/False/None): The value of compatibility key

        TODO: compatibility mode

        """

        if comp_key in VALID_KEYS_COMPATIBILIES:
            self.compatibilities[comp_key] = comp_val
        else:
            self.logger.error('Key %s not supported' % comp_key)

    def set_compatibilities(self, compatibilities):
        """Set many compatibilities.

        Args:
            compatibilities(list): list of tuples: compatibility key,
            compatibility value

        """
        for key, value in compatibilities:
            self.set_compatibility(key, value)

    def is_compatible_with(self, key_):
        """Check if test is compatible with args gived.

        Args:
            key_(str): the key you want to check
        Returns:
            boll: True if is compatible, if not retunr False

        """
        try:
            return self.compatibility[key_]
        except KeyError:
            return True

    def set_addon_name(self, addon_name):
        """Change the addon name used to run test."""
        self.addon_name = addon_name

    def set_test_tile(self, title):
        """Change the title of the actual test."""
        self.test_title = title

    def set_logger(self, logger):
        """Change the logger."""
        self.logger = logger

    def log_test_title(self):
        """Use logger to log the test title."""
        self.logger.debug(self.test_title)

    def run(self):
        """ Must to be used for execute the entire test."""
        raise KaliExceptionTestCase('You must to use this method')

    def setup(self):
        """
        Must to be used for sets the required addons and compatibilities to run

        """
        raise KaliExceptionTestCase('You must to use this method')
