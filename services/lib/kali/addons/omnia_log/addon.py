"""
Omnia Log Addon
===============
To work with Omnia logs
"""

from ..lib.Loglib.Loglib import LogLib
from ..abstract import KaliOtsAddOn


class KaliLogOmniaAddon(KaliOtsAddOn):

    def __init__(self, ots_label=None, **kwargs):
        """

        Arguments:
            ots_label(str): the ots connection label
            **kwargs;


        Keyword arguments:
            ip (str): IP address of OTS;
            port (int): listener port for OTS (10001);


        """
        KaliOtsAddOn.__init__(self, ots_label, **kwargs)
        self.wrapper = LogLib()
        self.connected = False
        self.wait_for_check = 2

    # MANDATORY METHODS
    def setup(self):
        """
        Setup method

        Returns:
            bool: True if addon was able to connect OTS, False otherwise
        """
        if self.connect(self.ip, self.port):
            self.analyze()
            return True

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

    def connect(self, ip, port):
        """
        Connect method is used to connect the OTS listener daemon

        Arguments:
            ip (str): IP address of OTS;
            port (int): listener port for OTS (10001);

        Keyword arguments:


        Returns:
            bool: depending on connection result
        """
        if self.connected:
            return True
        try:
            self.wrapper.add_tcp_handler(ip, port)
            self.connected = True
            return True
        except OSError:
            return False

    def disconnect(self):
        """
        This method is used to disconnect

        Arguments:

        Keyword arguments:

        Returns:
            bool: depending on connection result
        """
        if self.connected:
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
        return True

    def send_command(self, method):
        """
            Send command to ots and fill Kali checker with the server response

            Args:
                method(str): Method to be executed on ots
            Returns:
                Server response
        """
        if self.ots_client is None:
            self.error(
                'No OTSClient found: do Kali method start_connection_ots')
            return False
        elif not self.ots_client.is_connected(self.ots_label):
            self.error('Connection %s nor found' % self.ots_label)
            return False

        resp = self.send_command_to_ots(_interface='journal',
                                        _method=method,
                                        arg_dict={})

        self.checker.set_returned(resp)
        return resp
