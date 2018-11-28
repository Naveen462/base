"""
Dbus Omina Addon
=================
Handlings the onboard dbus services

"""

from ..abstract import KaliOtsAddOn


class KaliDbusOmniaAddon(KaliOtsAddOn):
    """
    Omnia dbus addon.

    Attributes:
        Same as :exc:`~src.addons.abstract.KaliOtsAddOn`

    """

    def __init__(self, ots_label=None, **kwargs):
        """
        Arguments:
            **kwargs: No arguments needed to load this addon

        Keyword arguments:
            None


        """
        KaliOtsAddOn.__init__(self, ots_label, **kwargs)

    # MANDATORY METHODS
    def setup(self):
        """
        Setup method

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

    def send_command(self, func):
        """
            Send command to ots and fill Kali checker with the server response

            Args:
                func(str): Method to be executed on OTS

            Returns:
                Server response
        """
        return self.send_command_to_ots('dbus', func, arg_dict={})

    def do_method(self, interface, method, passed_args):
        """
            Wrapper to send command to ots and fill Kali checker with
            the server response

            Args:
                interface(str): one of these values allowed by OTS;
                method(str): required method for selected interface, details
                on OTS documentation
                passed_args (list): list of arguments required by method called

            Returns:
                bool: depending on proper execution
        """
        args = {
            "interface": interface,
            "method": method,
            'arg_dict': self._get_args(passed_args)
        }
        return self.send_command_to_ots("dbus", "do_method", arg_dict=args)

    def _get_args(self, passed_args):
        args_dict = {}
        i = 0
        for arg in passed_args:
            k = "arg_%d" % i
            args_dict.update({k: arg})
            i += 1
        return args_dict

    def do_generic_method(self,
                          interface,
                          interface_path,
                          method,
                          passed_args):
        """
            Wrapper to send command to ots and fill Kali checker with the
            server response

            Args:
                interface(str): one of these values allowed by OTS;
                interface_path(str): one of these values allowed by OTS;
                method(str): required method for selected interface, details
                on OTS documentation
                passed_args (list): list of arguments required by method called

            Returns:
                bool: depending on proper execution
        """
        args = {"interface": interface,
                "interface_path": interface_path,
                "method": method,
                'arg_dict': self._get_args(passed_args)
                }

        return self.send_command_to_ots('dbus',
                                        'do_generic_method',
                                        arg_dict=args)
