import socket
import time
import sys


class PiCaSoException(Exception):

    def __init__(self, message):
        super(PiCaSoException, self).__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class PiCaSoConnectionException(PiCaSoException):

    def __init__(self, message):
        super(PiCaSoConnectionException, self).__init__(message)


class PiCaSoCommandException(PiCaSoException):

    def __init__(self, message):
        super(PiCaSoCommandException, self).__init__(message)


class PiCaSoUnknownCommandException(PiCaSoException):

    def __init__(self, message):
        super(PiCaSoUnknownCommandException, self).__init__(message)


class PiCaSo:

    def __init__(self):
        self.__s = None
        self.__connected = False
        self.to = 0.5

    def connect(self, ip, port):
        # Connect to the server
        if sys.platform == "linux":
            self.__s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # activates after 1 second of idleness
            self.__s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
            # keepalive ping once every 3 seconds
            self.__s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
            # closes the connection after 5 failed ping
            self.__s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
        try:
            self.__s.connect((ip, port))
            self.__connected = True
        except (OSError, socket.timeout, ConnectionRefusedError) as e:
            self.__connected = False
            raise PiCaSoConnectionException("Pi.Ca.So connection refused: %s" % e)
        self.__s.send(b' ')
        response = b''
        while len(response) < 2:
            response += self.__s.recv(1)
        return True

    def is_connected(self):
        return self.__connected

    def send(self, message):
        if self.__s is None or not self.__connected:
            return False
        len_sent = 0
        while len_sent < len(message):
            len_sent = self.__s.send(message[len_sent:])
        # Receive a response
        response = b''
        while len(response) < 2:
            response += self.__s.recv(1)
        if response == message[:1] + b'1':
            raise PiCaSoCommandException('Pi.Ca.So command failed!')
        if response == message[:1] + b'2':
            raise PiCaSoUnknownCommandException('Pi.Ca.So command unknown!')
        return response

    def close(self):
        # Clean up
        self.__s.close()
        self.__connected = False

    def disconnect(self):
        self.close()

    def key_press(self, Key):
        self.send(('K' + Key).encode())

    def soft_key_press(self, SoftKey):
        self.send(('S' + SoftKey).encode())

    def card_reader_fw(self):
        self.send('F'.encode())

    def card_reader_rw(self):
        self.send('R'.encode())

    def key_sequence(self, Sequence, TimeOut=None):
        for s in Sequence:
            if len(s.strip()) > 0:
                self.send(('K' + s).encode())
                time.sleep(self.to if TimeOut is None else TimeOut)
            else:
                time.sleep(self.to)
