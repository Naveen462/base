#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import threading
from time import sleep
from binascii import hexlify
from serial import Serial, SerialException

EOL = "\n"
EOLb = b"\n"


class HandlerAbstract(threading.Thread):
    def __init__(self, cache):
        threading.Thread.__init__(self)
        self.size = 0
        self.limit = None
        self.cache = cache
        self.status = True
        self.not_recorded = None

    def run(self):
        while self.status:
            self.get_loglines()
            sleep(.001)

    def set_limit(self, limit):
        self.limit = limit

    def get_size(self):
        return self.size

    def append_line(self, lines):
        if self.limit is not None and self.size + len(lines.replace(EOL, "")) > self.limit:
            return False
        lines_list = lines.split(EOL)
        if self.not_recorded is not None:
            lines_list[0] = self.not_recorded + lines_list[0]
            self.not_recorded = None
        for singleline in lines_list[:-1]:
            self.cache.append(singleline)
            self.size += len(singleline)
        if len(lines_list[-1]) > 0:
            self.not_recorded = lines_list[-1]
        return True

    def get_loglines(self):
        raise NotImplementedError("get_loglines not implemented")

    def close(self):
        raise NotImplementedError("close not implemented")

    def get_log_size(self):
        return self.size

    def stop(self):
        self.status = False


class HandlerTcp(HandlerAbstract):
    def __init__(self, ip, port, cache):
        super(HandlerTcp, self).__init__(cache)
        self.s = socket.socket()
        self.port = port
        self.ipadd = ip
        if not self.tcp_connect():
            raise IOError("Unable to connect to %s:%d" % (ip, port))

    def tcp_connect(self):
        try:
            self.s.connect((self.ipadd, self.port))
            connection = True
        except ConnectionRefusedError:
            connection = False
        return connection

    def tcp_disconnect(self):
        if self.s is not None:
            self.s.close()
            self.s = None

    def close(self):
        self.tcp_disconnect()

    def get_loglines(self):
        try:
            buffer = 1
            data = self.s.recv(buffer)
        except (BrokenPipeError, OSError, AttributeError):
            self.tcp_disconnect()
            return False
        try:
            data = data.decode('utf-8')
        except UnicodeDecodeError:
            data = "Unexpected char received: " + hexlify(data).decode('utf-8').upper()
        self.append_line(data)
        return True


class HandlerSerial(HandlerAbstract):
    def __init__(self, cache, com_port, baud_rate):
        super(HandlerSerial, self).__init__(cache)
        self.serial = Serial()
        self.SerialHandler = True
        self.serial.port = com_port
        self.serial.baudrate = baud_rate
        self.string = None
        self.line = None
        if not self.serial_interface():
            self.close_serial()

    def get_loglines(self):
        self.get_serial()

    def serial_interface(self):
        try:
            self.serial.open()
        except SerialException:
            return False
        return self.serial.is_open

    def get_serial(self):
        while True:
            try:
                line = self.serial.readline().decode("utf-8")
                self.append_line(line)
            except UnicodeDecodeError:
                pass

    def send(self, string):
        if isinstance(string, str):
            string += EOL
            self.line = string.encode()
        if isinstance(string, bytes):
            string += EOLb
            self.line = string
        try:
            self.serial.write(self.line)
        except SerialException:
            self.string = None
            return False
        self.string = None
        return True

    def close(self):
        self.close_serial()

    def close_serial(self):
        self.serial.close()
        return self.serial.is_open


class HandlerInput(HandlerAbstract):
    def __init__(self, cache):
        super(HandlerInput, self).__init__(cache)

    def close(self):
        pass

    def get_loglines(self):
        self.cache.append(input('>>'))


class LogLib(object):
    def __init__(self):
        self.length = []
        self.cache = []
        self.cache_backup = []
        self.handlers = []
        self.res = 0
        self.count = 0

    def __del__(self):
        self.close()

    def set_limit(self, limit):
        handler_limit = limit // len(self.handlers)
        for handler in self.handlers:
            handler.set_limit(handler_limit)
        if len(self.handlers) > 0:
            self.handlers[0].set_limit(self.handlers[0] + limit % len(self.handlers))

    def add_tcp_handler(self, ip, port):
        new_handler = HandlerTcp(ip, port, cache=self.cache)
        new_handler.start()
        self.handlers.append(new_handler)

    def add_serial_handler(self, com_port, baud_rate):
        new_handler = HandlerSerial(self.cache, com_port, baud_rate)
        new_handler.start()
        self.handlers.append(new_handler)

    def add_input_handler(self):
        new_handler = HandlerInput(self.cache)
        new_handler.start()
        self.handlers.append(new_handler)

    def clear(self):
        self.cache.clear()

    def backup(self, limit):
        self.cache_backup.extend(self.cache)
        if len(self.cache_backup) >= limit:
            del self.cache_backup[0:len(self.cache)]
        return len(self.cache_backup)

    def get_size(self):
        size = 0
        for handler in self.handlers:
            size += handler.get_size()
        return size

    def dump(self):
        return EOL.join(x for x in self.cache)

    def close(self):
        for handler in self.handlers:
            handler.close()
            handler.stop()

    def write(self, string):
        for handler in self.handlers:
            try:
                if callable(getattr(handler, 'send')):
                    handler.send(string)
            except AttributeError:
                continue
