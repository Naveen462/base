#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KALI
====

"""

import os
from collections import OrderedDict
from configparser import ConfigParser
from configparser import NoSectionError, NoOptionError
from .exceptions import KaliExceptionKeyError
from .exceptions import KaliExceptionSetupError
from .exceptions import KaliExceptionValueError
from .exceptions import KaliExceptionTypeError
from .exceptions import KaliExceptionRemoveError
from .exceptions import KaliExceptionTestCase
from .exceptions import KaliExceptionOtsConnection
from .addons.abstract import KaliOtsAddOn
from .addons.dbus.addon import KaliDbusOmniaAddon
from .addons.omnia_log.addon import KaliLogOmniaAddon
from .addons.omnia_serial.addon import KaliSerialOmniaAddon
from .addons.webui.addon import KaliWebUiAddon
from .addons.omnia_bash.addon import KaliBashAddon
from .addons.omnia_picaso.addon import KaliPicasoAddon
from .addons.omnia_ftclient.addon import KaliFTClient
from .addons.main.addon import KaliMainAddon
from .define import LOG_LEVEL
from .test_case import KaliTestResultManager
from .ots_client import OtsClient


class Kali(object):
    """Kali class definition.

    Args:
        addons (dict): loaded addons dictionary.
        logger (object): logger object.
        test_cases (OrderedDict): OrderedDict of :exc:`~src.test_case.TestCase`
            objects.
        ots_client (object): :exc:`~src.ots_client.OtsClient` object to handle 
        ots connections
    """

    def __init__(self):
        self.addons = {}
        self.logger = None
        self.test_cases = OrderedDict()
        self.ots_client = None
        self._accepted_tags = None
        self._refused_tags = None

        self._cur_test_case = None

    @property
    def accepted_tags(self):
        return self._accepted_tags

    @accepted_tags.setter
    def accepted_tags(self, tags):
        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
            self._accepted_tags = tags

    @property
    def refused_tags(self):
        return self._refused_tags

    @refused_tags.setter
    def refused_tags(self, tags):
        if isinstance(tags, list) and all(isinstance(tag, str) for tag in tags):
            self._refused_tags = tags

    def __del__(self):
        try:
            self.close()
        except ImportError:
            print('Remember to close Kali [.close()]')

    # KALI METHODS
    def close(self):
        if self.ots_client:
            self.ots_client.close_all()
        for key in self.addons.keys():
            self.addons[key].close()

    # OTS METHODS
    def start_connection_ots(self, conn_key, ip, port):
        """
        This methods allows to add a OTS client to Kali object.
        OTS client is an object aimed to communicate with OTS server in order
        use services provided by it (dbus, journalctl, bash)

        Args:
            conn_key (str): A label to index the client.
            ip (str): IP address of target OMNIA with OTS server up and running
            port (int): OTS TCP port (10000).

        Returns:
            bool: True if object has been set, false otherwise.

        Raises:
        """
        try:
            if not self.ots_client:
                self.ots_client = OtsClient(conn_key, ip, port, self.logger)
                if self.logger:
                    self.ots_client.set_logger(self.logger)
            else:
                self.ots_client.connect(conn_key, ip, port)
        except KaliExceptionOtsConnection as e:
            self.error(str(e))
            return False
        self.debug("OTS connection %s created" % conn_key)
        # redundant ??
        for key in self.addons.keys():
            if isinstance(self.addons[key], KaliOtsAddOn):
                self.addons[key].set_ots_client(self.ots_client, conn_key)
        return True

    def close_connection_ots(self, conn_key):
        """
        Disconnect and remove target connection from OTS client dictionary

        Args:
            conn_key (str): A label to index the client.

        Returns:
            bool: True if object has been set, false otherwise.

        Raises:
            :exc:
            `~src.exceptions.KaliExceptionTypeError` if a conn_key is not a str
        """
        if not isinstance(conn_key, str):
            raise KaliExceptionTypeError(
                "Connection key passed is a %s instead of str" %
                type(conn_key).__name__)
        if self.ots_client is None:
            self.error(
                "No OTS client created yet, unable to close connection %s" %
                conn_key)
            return False
        return self.ots_client.close(conn_key)

    def disconnect_connection_ots(self, conn_key):
        if self.ots_client is None:
            self.error(
                "No OTS client created yet, unable to disconnect from %s" %
                conn_key)
            return False
        return self.ots_client.disconnect(conn_key)

    def reconnect_connection_ots(self, conn_key):
        if self.ots_client is None:
            self.error(
                "No OTS client created yet, unable to close connection %s" %
                conn_key)
            return False
        return self.ots_client.reconnect(conn_key)

    def check_connection_ots(self, conn_key, expected=None):
        if self.ots_client is None:
            self.error(
                "No OTS client created yet, unable to close connection %s" %
                conn_key)
            return False
        connection_status = self.ots_client.check_connection(conn_key)
        if None not in (self._cur_test_case, expected):
            if expected == connection_status:
                self._cur_test_case.add_passed()
            else:
                self._cur_test_case.add_failed()
        return connection_status

    # LOGS METHODS
    def set_logger(self, logger):
        """
        Set the logger object to Kali class and all addon already created.

        Args:
            logger (object): Any object which provides these methods: debug,
                info, passed, failed, skipped, error, warning.

        Returns:
            bool: True if object has been set, false otherwise. In case of
            positive execution
            Kali logger functions (debug, info, passed, failed, skipped, error,
            warning)
            will be overrided by logger methods.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTypeError`: if one of the
                required methods is not provided by the passed object.
        """
        for level in LOG_LEVEL:
            method = getattr(logger, level, None)
            if method is None or not callable(method):
                raise KaliExceptionTypeError(
                    "Logger object doesn't provide all needed methods.\
Missing %s" % level)

        self.logger = logger
        for addon_name in self.addons:
            self.addons[addon_name].set_logger(self.logger)
        if self.ots_client:
            self.ots_client.set_logger(self.logger)
        self.debug = logger.debug
        self.error = logger.error
        self.warning = logger.warning
        self.failed = logger.failed
        self.passed = logger.passed
        self.skipped = logger.skipped
        self.info = logger.info

    def debug(self, mess):
        """
        Overrided by set log function
        """
        pass

    def info(self, mess):
        """
        Overrided by set log function
        """
        pass

    def passed(self, mess):
        """
        Overrided by set log function
        """
        pass

    def failed(self, mess):
        """
        Overrided by set log function
        """
        pass

    def skipped(self, mess):
        """
        Overrided by set log function
        """
        pass

    def error(self, mess):
        """
        Overrided by set log function
        """
        pass

    def warning(self, mess):
        """
        Overrided by set log function
        """
        pass

    # ADDONS HANDLING METHODS
    def __new_addon(self, key, addon_type, **kwargs):
        """
        Private function used by Kali to add a new addon.

        Args:
            key (str): A label in order to index the new addon.
            addon_type (different types): one of any addon defined in
            `~src.addons`
            kwargs (different types): list of (optional) parameters needed to
            load the addon

        Returns:
            bool: True if object has been set, otherwise an exception will be
            raised up.

        Raises:
            :exc:`~src.exceptions.KaliExceptionKeyError`: if the label has
            been already used.
            :exc:`~src.exceptions.KaliExceptionSetupError`: when was unable to
            start the addon for any reason.
        """
        # Checking if key already exists
        if key in self.addons:
            raise KaliExceptionKeyError(
                "Key %s already present in addons list" % key)
        # Creating new addon and setting standard object
        new = addon_type(**kwargs)
        if self.logger:
            new.set_logger(self.logger)
        # Adding connection Object
        if isinstance(new, KaliOtsAddOn):
            new.set_ots_client(self.ots_client, kwargs['ots_label'])
        # Running setup initialization
        if new.setup():
            self.addons[key] = new
            new.debug("Addon %s (%s) added successfully" %
                      (key, type(new).__name__))
            return True
        else:
            raise KaliExceptionSetupError(
                "Unable to setup addon %s " % type(new))

    def remove_addon(self, key):
        """
        Utility to remove a created addon.

        Args:
            key (str): The label pointing the addon desired to be removed.

        Returns:
            bool: True if object has been removed, otherwise an exception will
            be raised up.

        Raises:
            :exc:`~src.exceptions.KaliExceptionKeyError`: if the label is not
            preset into Kali's addons keys.
            :exc:`~src.exceptions.KaliExceptionValueError`: if addon close
            method is not callable or not defined.
            :exc:`~src.exceptions.KaliExceptionRemoveError`: when close
            function was not run properly.
        """
        # Checking if requested key exist
        if key not in self.addons:
            raise KaliExceptionKeyError(
                "Key %s is not present in addons list" % key)
        addon = self.addons[key]
        # Checking if close() method is callable
        if not callable(addon.close):
            raise KaliExceptionValueError(
                "Addon %s is not callable" % type(self.addons[key]).__name__)
        # Running close addon method
        if addon.close():
            addon.debug(str(addon) + " correctly removed")
            del self.addons[key]
            return True
        else:
            raise KaliExceptionRemoveError(
                "Addon %s cannot be removed" % str(addon))

    def add_omnia_fts_client_addon(self, key, **kwargs):
        """
        Add a new Omnia File Transfer Service Client addon referenced by key.

        Args:
            key (str): Key value to identify the addon.
            **kwargs: parameters requested for addon setup.

        Keyword args:
            client_index (int): accepted value 0 or 1;
            key_label (str): The Ots label

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError:
            :exc:`~src.exceptions.KaliExceptionKeyError`
            if key is already present.
            KaliExceptionSetupError:
            :exc:`~src.exceptions.KaliExceptionSetupError`
            if addon setup fails.
        """
        self.__new_addon(key, KaliFTClient, **kwargs)

    def add_omnia_dbus_addon(self, key, **kwargs):
        """
        Add a new Omnia Dbus addon referenced by key.

        Args:
            key (str): Key value to identify the addon.
            **kwargs: parameters requested for addon setup (ip, port).

        Keyword args:
            ip (str): ip address for addon setup.
            port (int): port number for addon setup.
            key_label (str): The Ots label

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError:
            :exc:`~src.exceptions.KaliExceptionKeyError` if key is alreadyl
            present.
            KaliExceptionSetupError:
            :exc:`~src.exceptions.KaliExceptionSetupError` if addon setup fails
        """
        self.__new_addon(key, KaliDbusOmniaAddon, **kwargs)

    def add_omnia_log_addon(self, key, **kwargs):
        """
        Add a new Omnia log addon referenced by key.

        Args:
            key (str): Key value to identify addon.
            **kwargs: parameters requested for addon setup (ip, port).

        Keyword args:
            ip (str): ip address for addon setup.
            port (int): port number for addon setup.
            key_label (str): The Ots label

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError:
            :exc:`src.exceptions.KaliExceptionKeyError` if key is alread
            present.
            KaliExceptionSetupError:
            :exc:`src.exceptions.KaliExceptionSetupError` if addon setup fails.
        """
        self.__new_addon(key, KaliLogOmniaAddon, **kwargs)

    def add_omnia_serial_addon(self, key, **kwargs):
        """
        Add a new Omnia serial addon referenced by key.

        Args:
            key (str): Key value to identify addon.
            **kwargs: parameters requested for addon setup (com_port,baud_rate)

        Keyword args:
            com_port (int): COM port number for addon setup.
            baud_rate (int): BAUD rate value for addon setup.

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError:
            :exc:`src.exceptions.KaliExceptionKeyError` if key is already
            present.
            KaliExceptionSetupError:
            :exc:`src.exceptions.KaliExceptionSetupError` if addon setup fails.

        """
        self.__new_addon(key, KaliSerialOmniaAddon, **kwargs)

    def add_omnia_webui_addon(self, key, **kwargs):
        """
        Add a new Omnia webui addon referenced by key.

        Args:
            key (str): Key value to identify addon.
            **kwargs: parameters requested for addon setup (serial_port).

        Kwargs:
            url(str): [**Mandatory**] WebUi interface base url.
            wait (int): Time to wait in seconds for an element to appear in a
            page. Default is 30s.
            browser(str): either 'Firefox' or 'Chrome'. Defaults to 'Chrome'.
            download_folder(str): file download path. Defaults to 'download' in
            working dir.

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError: :exc:`~src.exceptions.KaliExceptionKeyError`
            if key is arleady present.
            KaliExceptionSetupError:
            :exc:`~src.exceptions.KaliExceptionSetupError` if addon setup fails
        """
        self.__new_addon(key, KaliWebUiAddon, **kwargs)

    def add_omnia_bash_addon(self, key, **kwargs):
        """
        Add to Kali a new Omnia Bash addon referenced by key
        Args:
            key (str): Key value to identify addon.
            **kwargs: parameters requested for addon setup (hostname,port).

        Keyword args:
            otsc_label (str): The OtsClient Connection label

        Returns:
            bool: True if addon has been created, raise an exception otherwise.
        Raises:
            KaliExceptionKeyError:
            :exc:`src.exceptions.KaliExceptionKeyError` if key is arleady
                present.
            KaliExceptionSetupError:
            :exc:`src.exceptions.KaliExceptionSetupError` if addon setup fails.
        """
        self.__new_addon(key, KaliBashAddon, **kwargs)

    def add_omnia_picaso_addon(self, key, **kwargs):
        """
        Add a new Omnia picaso addon referenced by key.

        Args:
            key (str): Key value to identify addon.
            **kwargs: parameters requested for addon setup (ip, port).

        Keyword args:
            ip (str): ip address for addon setup.
            port (int): port number for addon setup.

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        Raises:
            KaliExceptionKeyError: :exc:`~src.exceptions.KaliExceptionKeyError`
             if key is already present.
            KaliExceptionSetupError:
            :exc:`~src.exceptions.KaliExceptionSetupError` if addon setup fails
        """
        self.__new_addon(key, KaliPicasoAddon, **kwargs)

    def add_omnia_main_addon(self, key, **kwargs):
        """
        Add a new Omnia Main addon to controll OTS.

        Args:
            key (str): Key value to identify addon.
            **kwargs**: parameters requested for addon setup.

        Keyword args:
            command (str): Command line sended to server.
            service (str): the managed service
            user (str): The user owner of service
            key_label (str): The Ots label

        Returns:
            bool: True if addon has been created, raise an exception otherwise.

        """

        self.__new_addon(key, KaliMainAddon, **kwargs)

    def do_addon_method(self, key, requested_method, **kwargs):
        """
        Execute an addon method.

        Args:
            key (str): Key value to identify addon.
            requested_method (str): requested addon method.
            **kwargs**: parameters to pass to the addon.

        Returns:
            object: addon specific.

        Raises:
            :exc:`~src.exceptions.KaliExceptionKeyError`: if the requested
                method is not callable.
        """
        if key not in self.addons:
            raise KaliExceptionKeyError("No addon found with key %s " % key)
        method = getattr(self.addons[key], requested_method)
        if method is None or not callable(method):
            raise KaliExceptionValueError(
                "Addon %s doesn't provide method %s or it is not callable"
                % (str(type(self.addons[key])), requested_method))
        return method(**kwargs)

    # CHECKER METHODS
    def set_check(self, key, expected):
        """
        Set the expected returned value for the test.

        Args:
            key (str): key value to identify the addon.
            expected (object): expected returned value for the test.

        Raises:
            :exc:`~src.exceptions.KaliExceptionKeyError`: if no addon with the
                specified key is found.
        """
        if key not in self.addons:
            raise KaliExceptionKeyError("No addon found with key %s " % key)
        self.addons[key].set_check(expected)

    def get_result(self, key, operation, **kwargs):
        """
        Run the test and evaluate returned data with the specified operation.
        Store the test result in the current TestCase object if present and
        open.

        Args:
            key (str): key value to identify the addon.
            operation (str): operation for evaluating returned data.

        Returns:
            bool: True if test passed, False otherwise.

        Raises:
            :exc:`~src.exceptions.KaliExceptionKeyError`: if no addon with the
                specified key is found.
        """
        if key not in self.addons:
            raise KaliExceptionKeyError("No addon found with key %s " % key)
        result = self.addons[key].get_result(operation, **kwargs)

        if self._cur_test_case is not None:
            if not self._cur_test_case.is_closed():
                if result:
                    self._cur_test_case.add_passed()
                else:
                    self._cur_test_case.add_failed()
        return result

    def set_check_timeout(self, key, time):
        """
        Setter the default timeout value.

        Args:
            key (str): key value to identify the addon.
            time (float): seconds.
        """
        return self.addons[key].set_check_timeout(time)

    # TEST CASES METHODS
    def start_test_case(self, number, title):
        """
        Register and start a new test case.

        Parameters:
            number (str): test case number.
            title (str): test case title.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTestCase` if a TestCase is
                currently open or another TestCase with the same number and name
                is already registered.
        """
        if self._cur_test_case is not None:
            if not self._cur_test_case.is_closed():
                raise KaliExceptionTestCase(
'The current TestCase is open: close it before starting a new one.')
        elif (number, title) in self.test_cases:
            raise KaliExceptionTestCase(
                "TestCase number {} named '{}' already registered!".format(
                    number, title))
        else:
            self.logger.debug("Starting test case %s %s" % (number, title))
            self.test_cases[(number, title)] = KaliTestResultManager()
            self._cur_test_case = self.test_cases[(number, title)]
            for addon_key in self.addons:
                self.addons[addon_key].set_current_test(self._cur_test_case)

    def end_test_case(self):
        """
        Close the current test case.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTestCase` if a TestCase is
                already closed or there is no open TestCase.
        """
        if self._cur_test_case is None:
            raise KaliExceptionTestCase(
                'Cannot close the current TestCase: no open TestCase.')
        elif self._cur_test_case.is_closed():
            raise KaliExceptionTestCase(
                'Cannot close the current TestCase: TestCase is already closed.')
        else:
            self.logger.debug("Ending test case")
            self._cur_test_case.close()
            self._cur_test_case = None

    def test_case_result(self):
        """
        Return the current test case result.

        Returns:
            bool: current test case result.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTestCase` if the current
                TestCase is open or there is no current TestCase.
        """
        if self._cur_test_case is None:
            raise KaliExceptionTestCase(
                'Cannot get the current TestCase result: there is no TestCase.')
        elif not self._cur_test_case.is_closed():
            raise KaliExceptionTestCase(
                'Cannot get the current TestCase result: TestCase is open.')
        else:
            return self._cur_test_case.result

    def run(self, KaliTestObj,
            max_duration=None,
            **kwargs):
        """
        Execute Test
        Args:
            KaliTestObj(obj): A KaliTest object
            max_duration (float): if settled will be executed only the tests
            that have minor duration time
            kwargs(dict): All the test needed parameters

        """
        test_obj = KaliTestObj(kali=self, logger=self.logger, **kwargs)
        try:
            test_obj.setup()
        except AttributeError as e:
            self.logger.error("Something wrong in test setup: %s" % e)
            self.close()
            return False
        if self.check_refused_tags(test_obj) and self.check_accepted_tags(test_obj):
            if max_duration and test_obj.get_duration() > max_duration:
                return False
            self.start_test_case(test_obj.test_number, test_obj.test_title)
            notes = ""
            if len(test_obj.get_notes()) > 0:
                notes = test_obj.get_notes()
                self.logger.info("NOTE: %s" % notes)
            test_obj.run()
            if notes != test_obj.get_notes():
                self.logger.info("NOTE: %s" % test_obj.get_notes())
            self.end_test_case()
            return True
        else:
            self.logger.skipped("TEST SKIPPED")
        return False

    def check_refused_tags(self, test_case):
        """
        Check if a test case contains a refused tags (if set)

        Params:
            test_case(obj): KaliTestCase object to be checked
        """
        return not self.refused_tags or not any(tag in self.refused_tags for tag in test_case.tags)

    def check_accepted_tags(self, test_case):
        """
        Check if a test case contains all the accepted tags (if set)

        Params:
            test_case(obj): KaliTestCase object to be checked
        """
        return not self.accepted_tags or all(tag in test_case.tags for tag in self.accepted_tags)

    def get_addon_by_name(self, addon_name):
        """
        Return the addon object have the name gived

            Args:
                addon_name(str): The key label of the addon
        """
        try:
            return self.addons[addon_name]
        except KeyError:
            raise KaliExceptionKeyError(
                "No addon found with key %s " % addon_name)

    def reload_addon(self, addon_name, **kwargs):
        #import pdb;pdb.set_trace()
        self.addons[addon_name].__dict__.update(**kwargs)
        # self.addons[addon_name].close()
        self.addons[addon_name].setup()

    def get_addon_attr(self, addon_name, attr):
        try:
            value = getattr(self.addons[addon_name], attr)
        except AttributeError:
            value = None
        if not value:
            addons_config = os.path.join(os.path.dirname(__file__),
                                         'addons_configs.ini')
            cfg = ConfigParser()
            cfg.read(addons_config)
            addon_type = getattr(self.addons[addon_name], 'addon_type')
            value = cfg.get(addon_type, attr)
        return value

    def prettyprint_test_cases_result(self):
        """
        Return a pretty-printed string with results of each TestCase.

        +-------+----------+----------+
        |  NUM  |   TITLE  |  RESULT  |
        +-------+----------+----------+
        |  01   |  TestA   |  passed  |
        +-------+----------+----------+
        |  02   |  TestB   |  failed  |
        +-------+----------+----------+

        Returns:
            str: pretty-printed string with results of each TestCase.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTestCase` if a TestCase is open
            or there are no TestCases.
        """
        if not self.test_cases:
            raise KaliExceptionTestCase(
                'Cannot print results: the are no recorded TestCases.')
        elif self._cur_test_case and not self._cur_test_case.is_closed():
            raise KaliExceptionTestCase(
                'Cannot print results: the current TestCase is open.')

        pretty = str()

        # find longest name and number
        lmax_name = 5
        lmax_num = 3
        for k in self.test_cases.keys():
            num, name = k
            if len(str(num)) > lmax_num:
                lmax_num = len(str(num))
            if len(name) > lmax_name:
                lmax_name = len(name)

        # print header
        padding = 2
        sep = '+' + ('-' * (lmax_num + (padding * 2))) + '+' + \
              ('-' * (lmax_name + (padding * 2))) + '+' + \
              ('-' * (len('result') + (padding * 2))) + '+'
        pretty += sep + '\n'
        pretty += '|' + (' ' * padding) + 'NUM' + \
                  (' ' * (padding + (lmax_num - len('num')))) + '|' + \
                  (' ' * padding) + 'TITLE' + \
                  (' ' * (padding + (lmax_name - len('name')))) + '|' + \
                  (' ' * padding) + 'RESULT' + (' ' * padding) + '|'
        pretty += '\n'
        pretty += sep + '\n'

        # print testcases result
        for k, test in self.test_cases.items():
            num, name = k
            result = 'passed' if test.result else 'failed'
            pretty += '|' + (' ' * padding) + str(num) + \
                      (' ' * (padding + (lmax_num - len(str(num))))) + '|' + \
                      (' ' * padding) + name + \
                      (' ' * (padding + (lmax_name - len(name)))) + '|' + \
                      (' ' * padding) + result + (' ' * padding) + '|'
            pretty += '\n'
            pretty += sep + '\n'

        pretty += '|' + (' ' * padding) + 'total' + \
            (' ' * (padding + (lmax_num - 5)))\
            + '|' + (' ' * padding) + str(len(self.test_cases.items()))

        return pretty
