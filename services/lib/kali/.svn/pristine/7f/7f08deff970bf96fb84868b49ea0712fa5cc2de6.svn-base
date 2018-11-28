#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADDONS ABSTRACT MODULE
=======================

"""

from ..exceptions import *
from .checkers import Checker
import time


class KaliAddOn(object):
    """
    Kali addon abstract class.

    Attributes:
        logger (object): logger object
        checker (object): :class:`~src.addons.checkers.Checker`
    """

    def __init__(self, **kwargs):
        self.logger = None
        self.checker = Checker()
        self.wait_for_check = None
        self.check_timeout = None
        self.test_case = None
        self.addon_type = ""
        self.__dict__.update(**kwargs)
        self.kwargs = kwargs

    # Mandatory functions
    def close(self):
        """
        **Mandatory!** Close method for the addon.

        Raises:
            NotImplementedError: if the addon does not implement this method.
        """
        raise NotImplementedError("close method not overridden")

    def setup(self):
        """
        **Mandatory!** Setup method for the addon.

        Raises:
            NotImplementedError: if the addon does not implement this method.
        """
        raise NotImplementedError("setup method not overridden")

    # Checker utils
    def set_check(self, value):
        """
        Setter method for expected value.

        Args:
            value (object): expected value.
        """
        self.checker.set_expected(value)

    def set_check_timeout(self, timeout):
        """
        Setter the default timeout value

        Args:
            timeout (int/float): seconds
        """
        try:
            timeout = float(timeout)
        except ValueError as e:
            raise KaliExceptionValueError(e)
        self.checker.set_timeout(timeout)
        self.check_timeout = timeout

    def get_result(self, test, **kwargs):
        """
        Get test result.

        Args:
            test (str): test type (eg. 'equal')

        Returns:
            bool: True if test passed, false otherwise.

        Raises:
            :exc:`~src.exceptions.KaliExceptionValueError`: if test type does not exist.
        """
        timeout_start = time.time()
        timeout = 1.0
        if self.check_timeout:
            timeout = self.check_timeout

        if self.wait_for_check is not None:
            time.sleep(self.wait_for_check)
        check_method = getattr(self.checker, test, None)
        if check_method is None:
            raise KaliExceptionValueError(
                "Unexpected test value passed: %s" % test)
        expeted = self.checker.expected
        returned = self.checker.returned
        answer = False
        while time.time() < timeout_start + timeout:
            answer = check_method(**kwargs)
            if answer:
                self.passed("Check passed!")
                if self.checker.current_test:
                    self.checker.current_test.add_passed()
                return answer
            self.checker.set_returned(returned)
            self.set_check(expeted)
        self.failed("Check failed!")
        if self.checker.current_test:
            self.checker.current_test.add_failed()
        return answer

    # Logger utils

    def set_logger(self, logger):
        """
        Set logger object

        Args:
            logger (object): logger object.
        """
        self.debug = logger.debug
        self.error = logger.error
        self.warning = logger.warning
        self.failed = logger.failed
        self.passed = logger.passed
        self.skipped = logger.skipped
        self.checker.set_logger(logger)

    def debug(self, message):
        """
        Overrided by set log function
        """
        pass

    def error(self, message):
        """
        Overrided by set log function
        """
        pass

    def warning(self, message):
        """
        Overrided by set log function
        """
        pass

    def failed(self, message):
        """
        Overrided by set log function
        """
        pass

    def passed(self, message):
        """
        Overrided by set log function
        """
        pass

    def skipped(self, message):
        """
        Overrided by set log function
        """
        pass

    def set_ots_client(self, ots_client):
        self.ots_client = ots_client

    # Test cases utils
    def set_current_test(self, current_test):
        self.checker.current_test = current_test

    # Other utils
    '''
    def check_kwargs(self, kwargs_expected, kwargs_received):
        check = True
        for k in kwargs_expected:
            if k not in kwargs_received:
                self.error("Unable to find argument: %s" % k)
                check = False
            elif type(kwargs_received[k]) is not kwargs_expected[k]:
                self.error("Argument %s doesn't match type required
                            (%s instead of %s)" %
                            (k, type(kwargs_received[k]).__name__,
                             kwargs_expected[k].__name__)
                           )
                check = False
        return check
    '''


class KaliOtsAddOn(KaliAddOn):

    def __init__(self,  ots_label=None, **kwargs):
        KaliAddOn.__init__(self, **kwargs)
        self.ots_client = None
        self.ots_label = ots_label

    def set_ots_client(self, ots_client, ots_label):
        self.ots_client = ots_client
        self.ots_label = ots_label

    # OTS utils
    def send_command_to_ots(self, interface, method, arg_dict):
        if self.ots_client is None:
            self.error(
                'No OTSClient found: do Kali method start_connection_ots')
            return False
        elif not self.ots_client.is_connected(self.ots_label):
            self.error('No connection %s found or is not connected' %
                       self.ots_label)
            return False

        resp = self.ots_client.send(key_label=self.ots_label,
                                    interface=interface,
                                    method=method,
                                    argument_dic=arg_dict)
        if resp:
            self.checker.set_returned(resp)
            return resp
        return resp
