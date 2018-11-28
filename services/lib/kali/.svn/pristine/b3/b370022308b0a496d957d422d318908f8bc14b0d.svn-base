#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KALI Custom Exceptions
======================

"""
from selenium.common.exceptions import WebDriverException


class KaliException(Exception):

    def __init__(self, message):
        super(KaliException, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class KaliExceptionTestCase(KaliException):

    def __init__(self, message):
        super(KaliExceptionTestCase, self).__init__(message)


class KaliExceptionRemoveError(KaliException):

    def __init__(self, message):
        super(KaliExceptionRemoveError, self).__init__(message)


class KaliExceptionTypeError(KaliException, TypeError):

    def __init__(self, message):
        super(KaliExceptionTypeError, self).__init__(message)


class KaliExceptionKeyError(KaliException, KeyError):

    def __init__(self, message):
        super(KaliExceptionKeyError, self).__init__(message)


class KaliExceptionValueError(KaliException, ValueError):

    def __init__(self, message):
        super(KaliExceptionValueError, self).__init__(message)


class KaliExceptionSetupError(KaliException):

    def __init__(self, message):
        super(KaliExceptionSetupError, self).__init__(message)


class KaliExceptionWebUiDriver(KaliException, WebDriverException):

    def __init__(self, message):
        super(KaliExceptionWebUiDriver, self).__init__(message)


class WebUIWrongPageException(KaliExceptionWebUiDriver):
    pass


class WebUIMissArgException(KaliExceptionWebUiDriver):
    pass


class WebUIWrongArgTypeException(KaliExceptionWebUiDriver):
    pass


class KaliExceptionOtsConnection(KaliException):

    def __init__(self, message):
        super(KaliExceptionOtsConnection, self).__init__(message)


class KaliExceptionOtsInvalidHeader(KaliException):

    def __init__(self, message):
        super(KaliExceptionOtsInvalidHeader, self).__init__(message)


class KaliExceptionAttributeError(KaliException):

    def __init__(self, message):
        super(KaliExceptionAttributeError, self).__init__(message)
