"""
Main OTS Addon
==============
handlings OTS 

"""
from ..abstract import KaliOtsAddOn


class KaliMainAddon(KaliOtsAddOn):

    def __init__(self, ots_label=None, **kwargs):
        KaliOtsAddOn.__init__(self, ots_label, **kwargs)

    # MANDATORY

    def setup(self):
        """
        Setup method

        Arguments:
            **kwargs: No arguments needed to load this addon

        Keyword arguments:
            None

        Returns:
            bool: True as default
        """
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
        return True

    # METHODS
    def send_command(self, command, service=None, user=None, ):
        """
        Send a command to Omnia Test Server Main controller.

        Args:
            command (str): Command line sended to server.
            service (str): the managed service
            user (str): The user owner of service
        Returns:
            bool: depending on OTS response
        """
        if self.ots_client is None:
            self.error(
                'No OTSClient found: do Kali method start_connection_ots')
            return False
        elif not self.ots_client.is_connected(self.ots_label):
            self.error('No connection %s found or is not connected' %
                       self.ots_label)
            return False
        resp = self.send_command_to_ots('main',
                                        command,
                                        {"service": service,
                                         "user": user})
        self.checker.set_returned(resp)
        return True

    def send_noarg_command(self, command):
        if self.ots_client is None:
            self.error(
                'No OTSClient found: do Kali method start_connection_ots')
            return False
        elif not self.ots_client.is_connected(self.ots_label):
            self.error('No connection %s found or is not connected' %
                       self.ots_label)
            return False
        resp = self.send_command_to_ots(interface='main',
                                        method=command,
                                        arg_dict={})
        self.checker.set_returned(resp)
        return True