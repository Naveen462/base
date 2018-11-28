"""
FTClient Addon
===============
Omnia File Trsasfer addon

"""
from ..abstract import KaliOtsAddOn


class KaliFTClient(KaliOtsAddOn):

    def __init__(self, ots_label=None, **kwargs):
        """
        Keyword arguments:
            client_index (int): accepted value 0 or 1;
        """
        KaliOtsAddOn.__init__(self, ots_label, **kwargs)

    # MANDATORY

    def setup(self):
        """
        Setup method

        Arguments:
            **kwargs: list of arguments required to initialize the object

        Returns:
            bool: True if the object hals been initialized, False otherwise
        """
        if self.client_index is None:
            return False
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
    def set_wait(self, wait):
        """
        Send a command to selected FTS Client through the OTS.
        The value set will be waited before answering to FTS after a 
        'file_available' query received.
        If the command is properly executed, set as returned a dictionary with
        following details:
        - "message": a message validating the setting;

        Args:
            wait(int): Value for waiting before answering to FTS.

        Returns:
            bool: depending on OTS command execution
        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'set_wait', {'wait': wait})

    def set_exit_code(self, exit_code):
        """
        Send a command to selected FTS Client through the OTS.
        The value set will be returned to FTS after a 'file_available'
        query received.
        If the command is properly executed, set as returned a dictionary with
        following details:
        - "message": a message validating the setting;

        Args:
            exit_code(int): Value used to answer to FTS.
        Returns:
            bool: depending on OTS command execution
        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'set_exit_code', {'answer': exit_code})

    def set_stdout(self, output):
        """
        Send a command to selected FTS Client through the OTS.
        The value set will be returned to FTS after a 'file_available' query
        received.
        If the command is properly executed, set as returned a dictionary with
        following details:
        - "message": a message validating the setting;

        Args:
            output(str): Value used to answer to FTS.
        Returns:
            bool: depending on OTS command execution
        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'set_stdout', {'stdout': output})

    def set_stderr(self, error):
        """
        Send a command to selected FTS Client through the OTS.
        The value set will be returned to FTS after a 'file_available' query
        received.
        If the command is properly executed, set as returned a dictionary with
        following details:
        - "message": a message validating the setting;

        Args:
            error(str): Value used to answer to FTS.

        Returns:
            bool: depending on OTS command execution
        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'set_stderr', {'stderr': error})

    def set_mode(self, mode):
        """
        Send a command to selected FTS Client through the OTS.
        The only accepted values are: 'direct' and 'auto'.
        In 'direct' mode: the answer returned to FTS after a 'file_available'
        query is composed by the object's
        parameters;
        In 'auto' mode: the answer's parameters are calculated based on file
        name received;
        If the command is properly executed, set as returned a dictionary with
        following details:
        - "message": a message validating the setting;

        Args:
            mode(str): Value for answering mode
            (accepted values: 'auto' / 'direct').

        Returns:
            bool: depending on OTS command execution
        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'set_mode', {'mode': mode})

    def subscribe_to(self, extension_str, bus_name, interface, timeout):
        """
        Send a command to FTS Client through the OTS.
        This command will trigger a 'subscribe_to' call to FTS interface.
        If the command is properly executed, set as returned a dictionary
        with following details:
        - "answer_list", a list composed by:
        - exit code (int);
        - standard error (str);
        - standard output (str);

        Args:
            extension_str(str): Extension string
            bus_name(str): Bus name sent to FTS
            interface(str): Interface sent to FTS
            timeout(str): Timeout sent to FTS

        Returns:
            bool: depending on OTS command execution
            
        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'subscribe_to_fts',
                                        {'accepted_extensions': extension_str,
                                         'passed_busname': bus_name,
                                         'passed_interface': interface,
                                         'timeout': timeout}
                                        )

    def get_list(self):
        """
        Send a command to FTS Client through the OTS.
        This command will return the list of package sent by the FTS to the
        FTS client.
        If the command is properly executed, set as returned a dictionary with
        following details:
        - "list", a list of touples composed by:
        - incoming path (str);
        - signed flag (int);
        Returns:
            bool: depending on OTS command execution

        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'get_list', {})

    def clear_list(self):
        """
        Send a command to FTS Client through the OTS.
        This command will clear the list of package sent by the FTS to
        the FTS client.
        If the command is properly executed, set as returned a dictionary with
        following details:
        - "message": a message validating the setting;


        Returns:
            bool: depending on OTS command execution
        """
        return self.send_command_to_ots('ftc%d' % self.client_index,
                                        'clear_list', {})
