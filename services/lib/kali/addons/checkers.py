#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
KALI CHECK RESULT
=================

"""
import time
from ..exceptions import *


class Checker:
    """Checker class definition.

    Attributes:
        expected (object): expected values.
        returned (object): returned values.
    """

    def __init__(self):
        self.expected = None
        self.returned = None
        self.logger = None
        self.timeout = None
        self.current_test = None

    def set_timeout(self, timeout):
        """
        Setter the default timeout value

        Args:
            timeout (float): seconds
        """
        self.timeout = timeout

    def check(self, callback, reset_callback=None):
        """
        Abstract method.

        Args:
            callback (method): function to be called to check the values. This
                method may return True/False.

        Returns:
            bool: True if callback , false otherwise.

        Raises:
            :exc:`~src.exceptions.KaliExceptionValueError`: if one of the
                returned or expected values has not been set or the callback
                function doesn't return a boolean.
                :param callback:
                :param reset_callback: Needed to reset expected and returned
                values to default
        """
        timeout_start = time.time()
        if not self.timeout:
            self.timeout = 1.0
        if None in (self.expected, self.returned):
            raise KaliExceptionValueError(
                "No value set for returned/expected value/s")
        answer = None
        while time.time() < timeout_start + self.timeout:
            answer = callback()
            if not isinstance(answer, bool):
                raise KaliExceptionValueError(
                    "Callback function doesn't return boolean value")
            if answer:
                return answer
        if reset_callback is None:
            self.reset()
        else:
            reset_callback()
        return answer

    def set_expected(self, expected_values):
        """
        Setter method for expected values.

        Args:
            expected_values (object): expected values.
        """
        self.expected = expected_values

    def set_returned(self, returned_values):
        """
        Setter method for returned values.

        Args:
            returned_values (object): returned values.
        """
        self.returned = returned_values

    def reset(self):
        """
        Reset expected and returned values.
        """
        self.expected = None
        self.returned = None

    def list_compare(self):
        """
        Compare method to check returned / expected lists.

        Returns:
            bool: True if list compare pass, false otherwise.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTypeError`: if one of the
                returned or expected values is not a list.
        """
        if (type(self.returned), type(self.expected)) != (list, list):
            raise KaliExceptionTypeError(
                "One of returned or expected value is not a list, " +
                "unable to perform list compare")
        # First step: check list lengths
        if len(self.returned) != len(self.expected):
            return False
        # Second step: check list identity
        expected = self.expected
        returned = self.returned
        _i = 0
        _l = len(returned)
        while _i < _l:
            if expected[_i] is not None:
                self.returned = returned[_i]
                self.expected = expected[_i]

                if self.different():
                    # Mismatch found
                    return False
            _i += 1
        # No mismatch found
        return True

    def dict_compare(self):
        """
        Compare method to check returned / expected dictionaries.

        Returns:
            bool: True if list compare pass, false otherwise.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTypeError`: if one of the
                returned or expected values is not a list.
        """
        if (type(self.returned), type(self.expected)) != (dict, dict):
            raise KaliExceptionTypeError(
                "One of returned or expected value is not a dictionary, " +
                "unable to perform dict compare")
        # First step: check list lengths
        if len(self.returned) != len(self.expected):
            return False
        if sorted(list(self.returned.keys())) != sorted(
                list(self.expected.keys())):
            return False
        returned_dict = self.returned
        expected_dict = self.expected
        for k in expected_dict.keys():
            if expected_dict[k] is None:
                continue
            if type(returned_dict[k]) in (dict, list):
                self.returned = returned_dict[k]
                self.expected = expected_dict[k]
                if isinstance(returned_dict[k], dict):
                    return self.dict_compare()
                else:
                    return self.list_compare()
            if expected_dict[k] != returned_dict[k]:
                return False
        return True

    def equal(self):
        """
        Compare method to check returned/expected object.

        Returns:
                bool: True if compare pass, false otherwise.
        """
        return self.check(self.__equal)

    def __equal(self):
        """
        Private method, compare returned and expected method.

        Returns:
            bool: True if list compare pass, false otherwise.
        """
        return self.expected == self.returned

    def different(self):
        """
        Compare method to check returned / expected object.

        Returns:
            bool: True if compare fails, false otherwise.
        """
        return self.check(self.__different)

    def __different(self):
        """
        Private method, compare returned and expected method

        Returns:
            bool: True if list compare fail, false otherwise.
        """
        return not self.__equal()

    def find(self):
        if isinstance(self.returned, dict):
            values_list = [value for value in self.returned.values()]
            for value in values_list:
                if self.expected in value:
                    return True
            return False
        if isinstance(self.returned, list):
            return self.check(self.__find_in_list, self.returned.clear)
        elif isinstance(self.returned, str):
            return self.check(self.__find_in_string)
        else:
            raise KaliExceptionTypeError(
                "Find not support for this kinde of object")

    def __find_in_string(self):
        return self.expected in self.returned

    def __find_in_list(self, ):
        if not isinstance(self.returned, list):
            raise KaliExceptionTypeError("")
        for line in self.returned:
            if line.find(self.expected) >= 0:
                return True
        return False

    def callback(self, callback):
        return callback(self.expected, self.returned)

    def set_logger(self, logger):
        """
        Set the logger object to Checker.

        Args:
            logger (object): Any object which provides these methods: debug,
                info, passed, failed, skipped, error, warning.

        Returns:
            bool: True if object has been set, false otherwise.

        Raises:
            :exc:`~src.exceptions.KaliExceptionTypeError`: if one of the
                required methods is not provided by the passed object.
        """
        self.debug = logger.debug
        self.error = logger.error
        self.warning = logger.warning
        self.failed = logger.failed
        self.passed = logger.passed
        self.skipped = logger.skipped

    def debug(self, mess):
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

    def failed(self, mess):
        """
        Overrided by set log function
        """
        pass

    def passed(self, mess):
        """
        Overrided by set log function
        """
        pass

    def skipped(self, mess):
        """
        Overrided by set log function
        """
        pass
