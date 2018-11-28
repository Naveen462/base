#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNIA TESTING SERVER CLIENT
===========================

"""
import json
import socket

from .exceptions import KaliExceptionOtsConnection
from .exceptions import KaliExceptionOtsInvalidHeader
from .exceptions import KaliExceptionValueError

from .COMMON.TLV import TLV
from .protocol_header import check_header
from .protocol_header import create_header

SOCK_TIMEOUT = 60
MAX_PACKET_SIZE = 65536


class ConnectionHandler(object):
    """
        ConnectionHandler class definition. Handle a connection

        Args:
            ip        (str): ots ip address
            port      (int): ots port
            socket    (object): socket object
            connected (bool): connection status
    """

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None
        self.connected = False
        self.connect(ip, port)

    def connect(self, ip, port):
        """Connect to given ip,port.

        Args:
            ip   (str): ots ip address
            port (int): ots port
        Raises:
            KaliOtsConnectionException:
             :exc:`~src.exceptions.KaliOtsConnectionException`
                if connection refused
            KaliExceptionValueError:
             :exc:`~src.exceptions.KaliExceptionValueError`
            if ip and port type is not correct

        """
        if self.connected:
            return True
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(SOCK_TIMEOUT)
            self.socket.connect((str(ip), int(port)))
            self.connected = True
        except ValueError as e:
            raise KaliExceptionValueError(e)
        except (OSError, socket.timeout) as e:
            raise KaliExceptionOtsConnection("Connection refused: %s" % e)
        return True

    def disconnect(self):
        """
           Close socket
        """
        self.connected = False
        self.socket.close()

    def reconnect(self):
        if self.connected:
            self.disconnect()
        return self.connect(self.ip, self.port)

    def is_connected(self):
        """
           Check if socket is connected

            Returns:
                bool: True if socket connected, False otherwise
        """
        return self.connected

    def communicate(self, json_):
        """
            Send a json to server and wait for answer

            Args:
                json_ (str): json data to be sent
            Returns:
                str: server response
            Raises:
                KaliOtsConnectionException:
                 :exc:`~src.exceptions.KaliExceptionKeyError`
                    if communication error
        """
        header = TLV()

        json_ = create_header(len(json_), 'json') + json_.encode()
        sent = 0
        try:
            # sending data
            while sent < len(json_):
                sent = self.socket.send(json_[sent:])
            # receiving header
            while not header.complete:
                byte = self.socket.recv(1)
                header.populate(byte)

            len_tlv = TLV()
            i = 0
            while not len_tlv.complete:
                byte = header.getVal()[i:i + 1]
                i += 1
                len_tlv.populate(byte)

            format_tlv = TLV()
            i = len(len_tlv.hexdump())
            while not format_tlv.complete:
                byte = header.getVal()[i:i + 1]
                i += 1
                format_tlv.populate(byte)

            if not (check_header(header) and check_header(
                    len_tlv) and check_header(format_tlv)):
                raise KaliExceptionOtsInvalidHeader(
                    "Invalid header: %s" % header.getTag())
            # receiving data
            data_length = int.from_bytes(len_tlv.getVal(), byteorder='big')
            data = b''
            while len(data) < data_length:
                data += self.socket.recv(1)
            if len(data) == 0:
                # If no data received, socket is disconnected
                raise OSError
            if data:
                return data.decode()
        except (OSError, BrokenPipeError) as e:
            self.disconnect()
            raise KaliExceptionOtsConnection("Communication error: %s" % e)


class OtsClient(object):
    """
        OtsClient class definition. Managing connections to ots

        Attributes:
            logger (object): logger object.
            connections (dict): dict of `~src.ots_client.ConnectionHandler`
    """

    def __init__(self, key, ip, port, logger):
        self.logger = logger
        self.connections = {}
        self.connect(key, ip, port)

    def send(self, key_label, interface, method, argument_dic=None):
        """
            Send a json command to specified ots and wait for response

            Args:
                key_label    (str):  connection key
                interface    (str):  target interface on ots
                method       (str):  method of interface to be executed
                argument_dic (dict): dict containing method arguments
            Returns:
                str: ots response
        """
        to_send = {
            'interface': interface,
            'method': method
        }
        if argument_dic:
            to_send.update({'argument_dic': argument_dic})
        json_to_send = self.json_pack(**to_send)
        self.debug("Sending %s to %s" % (method, interface))
        self.debug(json_to_send)
        try:

            returned = self.connections[key_label].communicate(json_to_send)
        except KaliExceptionOtsConnection:
            self.error("Unable to communicate with %s" % key_label)
            return False
        except KaliExceptionOtsInvalidHeader as e:
            self.error(e)
            return False
        self.debug("Omnia Test Server respond: %s" % returned)
        return self.json_unpack(returned, interface, method)

    def json_pack(self, **kwargs):
        """
            Format the arguments in function of ots json protocol

            Args:
                **kwargs: parameters requested to create json
            Keyword args:
                interface    (str):  target ots interface
                method       (str):  method to be executed on ots
                argument_dic (dict): dict containing method arguments
            Returns:
                str: json data
        """
        try:
            method_call = "%s" % kwargs["method"]
            if kwargs.get("argument_dic"):
                method_call = {"%s" %
                               kwargs["method"]: kwargs.get("argument_dic")}
            jdict = json.dumps(
                {"run": [
                    {"%s" % kwargs["interface"]: [method_call]}
                ]}
            )
        except KeyError as e:
            self.error(e)
            jdict = None

        except TypeError as e:
            self.error(e)
            jdict = None
        return jdict

    def json_unpack(self, json_data, interface, method):  # TODO improve this method
        """
           Parse json data to obtain ots response

            Args:
                json_data (str): json data to be parsed
                interface (str): interface on ots
                method    (str): method executed on ots
            Returns:
                str: json string
        """
        try:
            jdict = json.loads(json_data)
        except TypeError as e:
            self.error(e)
            return False

        for response in jdict:
            if response == 'return':
                for returned in jdict['return']:
                    for execute in returned[interface]:
                        if execute[method]['execution'] == "ok":
                            self.debug("Response is Ok")
                            return execute[method]['value']
                        else:
                            self.error('Problem in response')
        return False

    def connect(self, key, ip, port):
        """
           Connect to ots

            Args:
                key  (str): connection key
                ip   (str): ots ip address
                port (int): ots port
            Returns:
                object: ConnectionHandler object
        """
        self.debug("Connecting to: %s:%s" % (ip, port))
        if key not in self.connections:
            self.debug("Creating new connection %s" % key)
            conn = ConnectionHandler(ip, port)

            if conn.is_connected():
                self.connections[key] = conn
                self.debug("New Connection Started")
                return conn
        else:
            self.connections[key].connect(ip, port)

    def disconnect(self, key):
        """
           Connect to ots

            Args:
                key  (str): connection key
            Returns:
                bool: True if disconnection has been done properly
        """
        self.debug("Disconnecting from: %s" % key)
        if key not in self.connections:
            self.error("Key %s not present in connection dictionary" % key)
        else:
            self.connections[key].disconnect()

    def close(self, key):
        """
           Close connection to specified ots

            Args:
                key  (str): connection key
        """
        self.debug('Closing connection %s' % key)
        self.disconnect(key)
        del self.connections[key]

    def reconnect(self, key):
        """
           Reconnect to specified ots

            Args:
                key  (str): connection key
        """
        self.debug("Reconnecting connection %s" % key)
        self.connections[key].reconnect()

    def is_connected(self, key):
        """
           Check if specified ots is connected

            Args:
                key  (str): connection key
            Returns:
                bool: True if ots is connected, False otherwise
        """
        try:
            return self.connections[key].is_connected()
        except KeyError:
            self.error("Connection key %s doesn't exist" % key)
            return False

    def check_connection(self, key):
        """
           Check if specified ots is connected

            Args:
                key  (str): connection key
            Returns:
                bool: True if ots is connected, False otherwise
        """
        if self.send(key, "dbus", "ping", {}):
            self.debug("OTS %s connected!")
            return True
        else:
            self.debug("OTS %s not connected!" % key)
            return False

    def close_all(self):
        """
           Close all connections
        """
        while len(self.connections) > 0:
            self.close(list(self.connections.keys())[0])
        return True

    # LOGS METHODS
    def set_logger(self, logger):
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

    def info(self, mess):
        """
        Overrided by set log function
        """
        pass

    def passed(self, mess):
        """
        Overrided by set log function
        """
        pass

    def failed(self, mess):
        """
        Overrided by set log function
        """
        pass

    def skipped(self, mess):
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
