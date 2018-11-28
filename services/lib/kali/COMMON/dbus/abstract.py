# Author: Manuel Sansone
# Rev 1: First Draft - MaSa

import dbus
import dbus.service
from gi.repository import GLib
import dbus.mainloop.glib
import threading


class DbusAbstract(object):
    def __init__(self):
        self.objbus = None
        self.interface = None
        self.interface_api = None
        self.interface_path = None
        self.remote_object = None
        self.api = None
        self.logger = None
        self.connected = False
        self.callback_object = None

    # LOGGING FUNCTION WRAPPER:
    def debug(self, message):
        if self.logger:
            self.logger.debug(message)

    def error(self, message):
        if self.logger:
            self.logger.error(message)

    def set_logger(self, logger_obj):
        """
        Logger setter
        :param logger_obj: any object with error and debug attributes
        :return: None
        """
        if None in (getattr(logger_obj, "debug"), getattr(logger_obj, "error")):
            raise AttributeError("Logger object might have debug and error functions")
        self.logger = logger_obj

    # DBUS CONNECTION UTILS
    def connect_to_dbus(self, protocol, host, port=33333):
        """
        Main function to connect to dbus
        :param protocol: (str) tcp for remote connection, None for internal connection
        :param host: (str) SPOT IP address
        :param port: (int) SPOT IP port (default = 33333)
        :return: (bool) True/False based on connection status
        """
        if not (type(protocol) == str and type(host) == str, type(port) == int):
            raise TypeError("Expected parameters: protocol [str], host[str], port[str], passed %s %s %s"
                            % (str(type(protocol)), str(type(host)), str(type(port)))
                            )
        connection_string = ""
        try:
            if protocol == "tcp":
                connection_string = "%s:host=%s,port=%d" % (protocol, host, port)
                self.objbus = dbus.bus.BusConnection(connection_string)
            else:
                connection_string = "host=%s,port=%d" % (host, port)
                self.objbus = dbus.SystemBus()
            self.connected = True
        except dbus.DBusException:
            self.logger.error("Can't connect to: " + connection_string)
            self.connected = False
        return self.connected
        
    def populate_connector(self):
        """
        :param:
        :return:
        """
        if None not in (self.interface, self.interface_path):
            self.remote_object = self.objbus.get_object(self.interface, self.interface_path, introspect=False)
            if self.interface_api is None:
                self.api = dbus.Interface(self.remote_object, dbus_interface=self.interface)
            else:
                self.api = dbus.Interface(self.remote_object, dbus_interface=self.interface_api)

    # DATA HANDLING UTILS
    @staticmethod
    def convert_dbus_to_array(dbus_array):
        """
        :param dbus_array: (dbus Array, dbus Byte) incoming message
        :return: (bytes) converted buffer
        """
        if type(dbus_array) == bytes:
            return dbus_array
        if type(dbus_array) in (dbus.Array, dbus.ByteArray):
            return b"".join(i.to_bytes(1, byteorder='big') for i in dbus_array)
        else:
            raise TypeError("Unattended type received")

    # DEAMON UTILS
    def set_calback_object(self, co):
        self.callback_object = co

    def get_callback(self, method, *args):
        if not isinstance(method, str):
            raise ValueError("Value passed for get_callback is a %s instead of string" % str(type(method)))
        if self.callback_object:
            attribute = getattr(self.callback_object, method)
            if not callable(attribute):
                raise TypeError("Method %s not callable" % method)
            if attribute:
                return attribute(args)
        else:
            return None

    def start_daemon(self, name):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        objbus = self.objbus
        dbus.service.BusName(name, objbus.connection_to_dbus)
        mainloop = GLib.MainLoop()
        threading.Thread(mainloop.run)
