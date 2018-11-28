"""
.. module:: GVRlib.Logger
   :platform: Unix, Windows
   :synopsis: Logging management.
This module contains the *Logger* class.
"""


import os
import sys
import string
import logging
from time import gmtime, strftime
from binascii import hexlify
from colorama import Fore, Back, Style

class SignalHandler(logging.StreamHandler):

    def __init__(self, signal, parent=None):
        self.signal = signal
        logging.StreamHandler.__init__(self, self.signal)


FAIL = 26
PASS = 25
logging.addLevelName(FAIL, 'FAIL')
logging.addLevelName(PASS, 'PASS')
FORMATTER_STRING = '%(asctime)s %(levelname)s - %(message)s'


class Logger:
    """
    This class implement a flexible event logging system for
    *pyTools* applications and libraries.
    """

    def __init__(self, path, title, encoding="ascii"):
        """
        Initializes the *Logger* class.
        :Parameters:
            - *path* (string): Path to the log file.
            - *title* (string): Name of log file.
        """
        if path is not None and os.path.isfile(path):
            log_idx = path.index('.log')
            os.rename(path, (path[:log_idx] if log_idx > 0 else path) + '_' +
                      strftime("%Y%m%d_%H%M%S", gmtime(
                          os.path.getmtime(path))) + '.log')

        # DEFINE LOGGER

        self.logger = logging.getLogger(title)
        self.logger.setLevel(logging.DEBUG)

        # DEFINE FORMATTERS
        self.formatter = logging.Formatter(FORMATTER_STRING)

        # DEFINE HANDLERS
        self.file_handler = None
        self.console_handler = None
        self.signal_handler = None
        self.encoding = encoding
        self.setConsoleHandler()

        # START

    def __del__(self):
        # END
        if self.logger.hasHandlers():
            self.close()

    def setLevel(self, level):
        self.logger.setLevel(level)

    def setFileHandler(self, path):
        if self.file_handler is None:
            self.file_handler = logging.FileHandler(
                path, mode='a', encoding=self.encoding)
            self.file_handler.setLevel(logging.DEBUG)
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

    def removeFileHandler(self):
        if self.file_handler is not None:
            self.file_handler.close()
            self.logger.removeHandler(self.file_handler)
            self.file_handler = None

    def setConsoleHandler(self):
        if self.console_handler is None:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(logging.DEBUG)
            self.console_handler.stream = sys.stdout
            self.logger.addHandler(self.console_handler)

    def setConsoleHandlerFormatter(self, style, back, fore):
        if self.console_handler is not None:
            self.console_handler.setFormatter(
                logging.Formatter(
                    (style if style else "") +
                    (back if back else "") +
                    (fore if fore else "") +
                    FORMATTER_STRING +
                    Style.RESET_ALL
                )
            )

    def removeConsoleHandler(self):
        if self.console_handler is not None:
            self.logger.removeHandler(self.console_handler)
            self.console_handler = None

    def setSignalHandler(self, signal):
        if hasattr(signal, "write"):
            if self.signal_handler is None:
                self.signal_handler = SignalHandler(signal)
                self.signal_handler.setLevel(logging.DEBUG)
                self.signal_handler.setFormatter(self.formatter)
                self.logger.addHandler(self.signal_handler)

    def removeSignalHandler(self):
        self.signal_handler = None

    def close(self):
        """
        Closes up any resources used by the class.
        """
        self.removeSignalHandler()
        self.removeConsoleHandler()
        self.removeFileHandler()

    def clean_msg(self, msg):
        for char in msg:
            try:
                char.encode(self.encoding)
            except UnicodeEncodeError:
                msg = msg.replace(char, "<0x%s>" % "{:02X}".format(ord(char)))
        return msg

    def debug(self, msg):
        """
        Log a message string with the *DEBUG* level.
        :Parameters:
            - *msg* (string): Message to log.
        """
        msg = self.clean_msg(msg)
        self.setConsoleHandlerFormatter(Style.DIM, None, Fore.WHITE)
        self.logger.debug(msg)

    def info(self, msg):
        """
        Log a message string with the *INFO* level.
        :Parameters:
            - *msg* (string): Message to log.
        """
        msg = self.clean_msg(msg)
        self.setConsoleHandlerFormatter(Style.BRIGHT, None, Fore.BLUE)
        self.logger.info(msg)

    def warning(self, msg):
        """
        Log a message string with the *WARNING* level.
        :Parameters:
            - *msg* (string): Message to log.
        """
        msg = self.clean_msg(msg)
        self.setConsoleHandlerFormatter(Style.BRIGHT, Back.YELLOW, Fore.BLACK)
        self.logger.warning(msg)

    def error(self, msg):
        """
        Log a message string with the *ERROR* level.
        :Parameters:
            - *msg* (string): Message to log.
        """
        msg = self.clean_msg(msg)
        self.setConsoleHandlerFormatter(Style.BRIGHT, Back.RED, Fore.BLACK)
        self.logger.error(msg)

    def critical(self, msg):
        """
        Log a message string with the *CRITICAL* level.
        :Parameters:
            - *msg* (string): Message to log.
        """
        msg = self.clean_msg(msg)
        self.setConsoleHandlerFormatter(Style.BRIGHT, Back.RED, Fore.YELLOW)
        self.logger.critical(msg)

    def fail(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.logger.isEnabledFor(FAIL):
            message = self.clean_msg(message)
            self.setConsoleHandlerFormatter(Style.BRIGHT, None, Fore.RED)
            self.logger._log(FAIL, message, args, **kws)

    def passed(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.logger.isEnabledFor(PASS):
            message = self.clean_msg(message)
            self.setConsoleHandlerFormatter(Style.BRIGHT, None, Fore.GREEN)
            self.logger._log(PASS, message, args, **kws)

    def raw(self, msg):
        """
        Log a message string without formatting.
        :Parameters:
            - *msg* (string): Message to log.
        """
        if self.file_handler is not None:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(self.file_handler)
        if self.console_handler is not None:
            self.logger.removeHandler(self.console_handler)
            self.console_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(self.console_handler)
        if self.signal_handler is not None:
            self.logger.removeHandler(self.signal_handler)
            self.signal_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(self.signal_handler)
        self.logger.debug(self.clean_msg(msg))
        if self.file_handler is not None:
            self.logger.removeHandler(self.file_handler)
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)
        if self.console_handler is not None:
            self.logger.removeHandler(self.console_handler)
            self.console_handler.setFormatter(self.formatter)
            self.console_handler.stream = sys.stdout
            self.logger.addHandler(self.console_handler)
        if self.signal_handler is not None:
            self.logger.removeHandler(self.signal_handler)
            self.signal_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.signal_handler)

    def emit(self, message):
        if self.signal_handler is not None:
            self.signal_handler.emit(self.formatter.formatMessage(message))

    def checkResult(self, expectedDict, returnedDict, msg=''):
        """
        This method checks the expected result comparing two
        different dictionaries.
        :Parameters:
            - *expectedDict* (dictionary): Template dictionary for comparison.
            - *returnedDict* (dictionary): Dictionary to compare,.
        :Returns: ``True`` if both dictionaries must be equal
                (same keys and same values), ``False`` otherwise.
        """
        if expectedDict.keys() != returnedDict.keys():
            raise Exception("Mismatch of number of elements")
        if expectedDict == returnedDict:
            flag = 'PASS'
        else:
            flag = 'FAIL'
        if len(msg) > 0:
            msg = ' | ' + msg
        self.info('CHECK: ' + flag + msg +
                  ' Expected values=> ' + self.dictToString(
                      expectedDict) + ' Returned values=> '
                  + self.dictToString(returnedDict))
        return flag

    def dictToString(self, dictionary):
        """
        Utility method to convert dictionary to string.
        :Parameters:
            - *dictionary* (dictionary): Dictionary to convert.
        :Returns: A string representing dictionary content.
        """
        result = ''
        for key, value in dictionary.items():
            if isinstance(value, dict):
                entry = self.dictToString(value)
            else:
                entry = str(value)
                if not all(char in string.printable for char in entry):
                    entry = '{0} (hex)'.format(hexlify(entry))
            result += key + ':' + entry + '; '
        return result
