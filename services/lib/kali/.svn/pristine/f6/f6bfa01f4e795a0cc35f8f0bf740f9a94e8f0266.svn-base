"""
Omnia Serial Comunication Addon
===============================
Addon to comunicate with Omnia via serial port

"""
from ..lib.Loglib.Loglib import LogLib
from ..abstract import KaliAddOn


class KaliSerialOmniaAddon(KaliAddOn):

    def __init__(self):
        KaliAddOn.__init__(self)
        self.wrapper = LogLib()
        self.port_open = False
        self.wait_for_check = 2

    # MANDATORY METHODS
    def setup(self, **kwargs):
        """
        Setup method

        Arguments:
            **kwargs;


        Keyword arguments:
            com_port (str): serial port;
            baud_rate (int): serial connection baudrate;

        Returns:
            bool: True if serial connection has been done, False otherwise
        """
        if self.open_serial(kwargs['com_port'], kwargs['baud_rate']):
            self.analyze()
            return True
        else:
            return False

    def close(self):
        """
        Close method

        Arguments:
            No arguments needed to close the addon

        Keyword arguments:


        Returns:
            bool: True as default
        """
        self.wrapper.close()
        return True

    def open_serial(self, com_port, baud_rate):
        """
        This method is used to open the serial connection

        Arguments:
            com_port (str): serial port;
            baud_rate (int): serial connection baudrate;

        Keyword arguments:


        Returns:
            bool: depending on connection result
        """
        if self.port_open:
            return True
        try:
            self.wrapper.add_serial_handler(com_port=com_port,
                                            baud_rate=baud_rate)
            self.port_open = True
            return True
        except OSError:
            return False

    def close_serial(self):
        """
        This method is used to close the serial connection

        Arguments:

        Keyword arguments:

        Returns:
            bool: depending on connection result
        """
        if self.port_open:
            self.wrapper.close()

    def analyze(self):
        """
        This method is used to set the returned value

        Arguments:

        Keyword arguments:

        Returns:
            bool: True as default
        """
        self.checker.set_returned(self.wrapper.cache)

    def write(self, **kwargs):
        """
        This method is used to write buffer to serial connection

        Arguments:
            kwargs;
        Keyword arguments:

        Returns:
            bool: True as default
        """
        self.wrapper.write(kwargs['string'])
