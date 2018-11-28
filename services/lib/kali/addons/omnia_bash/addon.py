"""
Omina Bash Addon
=================
Addon to execute commands on Omnia bash

"""
from ..abstract import KaliOtsAddOn


class KaliBashAddon(KaliOtsAddOn):

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
    def execute_command(self, command):
        """
        Send the bash command line through the OTS.
        Set as returned a list of 3 bytes arrays:
        - stdin;
        - stdout;
        - stderror;

        Args:
            command(str): Command line to send to server.
        Returns:
            bool: depending on OTS response
        """
        return self.send_command_to_ots('shell', 'execute',
                                        {'command_line': command})
