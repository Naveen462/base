#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. module:: GVRlib.means 
   :platform: Unix, Windows
   :synopsis: TODO.
TODO. 
"""


import sys
import os
import shutil
import array
import time
import signal
import subprocess
from stat import ST_MODE, S_IMODE, S_IWRITE
from . import config

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    enums['items'] = dict((value, key) for key, value in enums.items())
    enums['list'] = sequential
    return type('Enum', (), enums)

Hue = enum('Black', 'Red', 'Green', 'Brown', 'Blue', 'Purple', 'Cyan', 'LightGray', 'DarkGray', 'LightRed', 'LightGreen', 'Yellow', 'LightBlue', 'LightPurple', 'LightCyan', 'White')

def color(sentence, forePigment = None, backPigment = None):
    if forePigment is None and backPigment is None: return sentence
    escape = '\x1b'
    paint = '['
    if forePigment is not None:
        if Hue.Black <= forePigment <= Hue.LightGray:  paint += str(forePigment + 30)
        elif Hue.DarkGray <= forePigment <= Hue.White: paint += '1;' + str(forePigment + 30)
        else:
            error._lay('Color Fail ===> Foreground hue not exist: "' + str(forePigment) + '"!')
            raise Error
    if backPigment is not None:
        if forePigment is not None: paint += ';'
        if Hue.Black <= backPigment <= Hue.LightGray:  paint += str(backPigment + 32)
        else:
            if Hue.DarkGray <= backPigment <= Hue.White: error._lay('Color Fail ===> Background hue cannot be bright!')
            else: error._lay('Color Fail ===> Background hue not exist: "' + str(backPigment) + '"!')
            raise Error
    paint += 'm'
    return escape + paint + sentence + escape + '[0m'

def isAString(obj):
    try: return isinstance(obj, basestring)
    except NameError: return isinstance(obj, str)

def Print(text, newline = True, stderr = False):
    if config.printEdit is None:
        out = sys.stderr if isinstance(text, ErrorMessage) or stderr else sys.stdout
        if isAString(text):
            out.write(text)
            if newline: out.write('\n')
            else: out.flush()
        else:
            for line in text: out.write(line + '\n')
    else:
        if config.dispatchHolder is not None and config.dispatchHolder.isEnabled():
            if text is None: text, newline = config.dispatchHolder.getMessage()
            else:
                config.dispatchHolder.setMessage(text, newline)
                return
        teCursor = config.printEdit.textCursor()
        teCursor.movePosition(config.endTextEdit)
        config.printEdit.setTextCursor(teCursor)
        if stderr or isinstance(text, ErrorMessage): config.printEdit.insertHtml('<font color=red>' + text.__str__() + '</font><br>')
        else:
            if isAString(text):
                if newline: config.printEdit.insertPlainText(text + '\n')
                else: config.printEdit.insertPlainText(text)
            else:
                for line in text: config.printEdit.insertPlainText(line + '\n')
        vertScrollBar = config.printEdit.verticalScrollBar()
        vertScrollBar.setValue(vertScrollBar.maximum())

class Error(EnvironmentError):
    pass

class ErrorMessage:
    def __init__(self, message): self.message = message
    def _lay(self, message): self.message = message
    def _put(self): Print(self.message)
    def __str__(self): return self.message
error = ErrorMessage('An undefined error occurs!')

class rtErrorMessage(ErrorMessage):
    def _set(self, func, path, exc_info):
        try:
            if not os.access(path, os.W_OK): # Is the error an access error?
                os.chmod(path, S_IWRITE)
                func(path)
            else: raise
        except:
            self.message = 'rmtree Fail ===> ' + str(exc_info[1]) + '!'
            raise OSError
rmtree_error = rtErrorMessage('An undefined error occurs!')

def rmtree(path, skip_missing = False, rmtree_error = rmtree_error):
    '''Recursively delete a directory tree (This FIX wrong python2 version).
    # Code:
    if sys.version_info[0] < 3:
    if os.path.islink(path) or not os.path.isdir(path):
        rmtree_error._lay('rmtree Fail ===> Not found or is not a directory: "' + path + '"!')
        raise OSError'''
    if os.path.exists(path):
        if os.path.islink(path) or not os.path.isdir(path):
            rmtree_error._lay('rmtree Fail ===> It is not a directory: "' + path + '"!')
            raise OSError
    else:
        if skip_missing: return
        else:
            rmtree_error._lay('rmtree Fail ===> Directory not found: "' + path + '"!')
            raise OSError
    try: shutil.rmtree(path, onerror = rmtree_error._set)
    except OSError: raise

class NonBlockGetChar(object):
    def __enter__(self):
        try: import msvcrt
        except ImportError:
            import tty
            import termios
            config.termios_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
        return self
    def __exit__(self, type, value, traceback):
        if config.termios_settings is not None:
            import termios
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, config.termios_settings)
            config.termios_settings = None
    def getch(self):
        ch = None
        try:
            import msvcrt
            if msvcrt.kbhit(): ch = msvcrt.getch()
            if isinstance(ch, bytes): ch = ch.decode('latin-1')
        except ImportError:
            import select
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                ch = sys.stdin.read(1)
        finally: return ch

def flushInput():
    try:
        import msvcrt
        while msvcrt.kbhit(): msvcrt.getch()
    except ImportError:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def inget(message, include_all = True):
    "Common string input system"
    if config.printEdit is None:
        data = None
        try:
            flushInput()
            if config.termios_settings is not None:
                import termios
                termios_settings = termios.tcgetattr(sys.stdin)
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, config.termios_settings)
            data = (raw_input if 'raw_input' in __builtins__ else input)(message).strip()
            if config.termios_settings is not None:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios_settings)
        except EOFError:
            if include_all: Print(" <<< EOFError caught, retry ... >>>")
            raise Error
        except KeyboardInterrupt:
            if include_all:
                if config.mayContinue: askToQuit(17, cleaner = config.cleaner)
                else: eXit(17, cleaner = config.cleaner)
            raise Error
        except RuntimeError:
            if include_all: raise Error
            else: return ''
        else: return data
    else:
        pass

def eXit(code, cleaner = None):
    "Exiting with a pause"
    if cleaner is not None: cleaner()
    if os.name is 'nt':
        isAShell = os.getenv('PROMPT')
        if isAShell is None: inget("\nPress ENTER to Exit")
    sys.exit(code)

def askToQuit(code, cleaner = None, nay = True):
    "Continue or Exit query"
    if code is None: return
    if config.mayContinue:
        if nay: message = 'y/N'
        else: message = 'Y/n'
        if code == 17: message = '\nKeyboard Interrupt, continue anyway [' + message + ']: '
        elif code > 0: message = 'Got an error, continue anyway [' + message + ']: '
        else: message = 'Do you want to build another archive [' + message + ']: '
        Print('')
        while True:
            try: toContinue = inget(message, False)
            except Error: pass
            else:
                if toContinue == '':
                    if nay: toContinue = 'n'
                    else: toContinue = 'y'
                if toContinue.lower() == 'n':
                    if cleaner is not None: cleaner()
                    sys.exit(code)
                elif toContinue.lower() == 'y': break
                else: Print(">>> Unrecognizable response, try again ...")
    else:
        if cleaner is not None: cleaner()
        if config.printEdit is None and os.name is 'nt':
            isAShell = os.getenv('PROMPT')
            if isAShell is None: inget("\nPress ENTER to Exit")
        sys.exit(code)

def handleSigINT(signum, frame):
    if config.mayContinue: askToQuit(17, cleaner = config.cleaner)
    else: eXit(17, cleaner = config.cleaner)

def deltree(path):
    "Recursive directories deletion, actually replaced by rmtree"
    for root, dirs, files in os.walk(path, topdown = False):
        for _file in files: os.remove(os.path.join(root, _file))
        for _dir in dirs: os.rmdir(os.path.join(root, _dir))

def errExc(funcName):
    strerr = funcName + " Fail ===> ("
    etype, value, _ = sys.exc_info()
    if isinstance(value, BaseException): strerr += etype.__name__
    else: strerr += etype
    strerr += ') ' + str(value)
    return strerr

def printExc(funcName):
    Print(errExc(funcName))

def execute(commandArgs, output = None):
    "call external program with arguments"
    if output is None:
        try:
            retValue = subprocess.call(commandArgs)
        except:
            error._lay(errExc('execute'))
            retValue = -1
    else:
        try:
            sp = subprocess.Popen(commandArgs, stdout = subprocess.PIPE)
            out = array.array('b', sp.communicate()[0]).tostring().strip()
            retValue = sp.wait()
            if not config.isPythonTwo:
                out = out.decode("latin1")
#           output.extend(out.replace('\r', '').split('\n'))
            output.extend([ x for x in out.replace('\r', '').split('\n') if x ])
#           for line in out.replace('\r', '').split('\n'):
#               line = line.strip()
#               if line: output.append(line)
        except:
            error._lay(errExc('pipe execute'))
            retValue = -2
    return retValue

def initFile(file, matter, overwrite = False):
    try:
        if os.path.exists(file):
            if overwrite:
                if not os.access(file, os.W_OK):
                    mode = S_IMODE(os.stat(file)[ST_MODE])
                    os.chmod(file, mode | S_IWRITE)
            else:
                error._lay('initFile Fail ===> File already exists: "' + file + '"!')
                raise Error
        confile = open(file, 'w')
        confile.write(matter + '\n')
        confile.close()
    except Error: raise
    except:
        error._lay(errExc('initFile'))
        raise Error

def onerror(text):
    raise

def init():
    from getpass import getuser
    config.user = getuser()
    config.cwd = os.getcwd() # Save current work directory
    signal.signal(signal.SIGINT, handleSigINT)

# if sys.version < '3':
#   def b(x): return x
# else:
#   import codecs
#   def b(x): return codecs.latin_1_encode(x)[0]

def hexdump(data, width, isAscii):
    if not data:
        return '<empty>'
    from io import StringIO
    io   = StringIO()
    io2  = StringIO()
    i    = 0
    import string
    for ch in data:
        if width > 0:
            if i and (i % width) == 0:
                if isAscii:
                    io.write('  ')
                    io.write(io2.getvalue())
                    io2.close()
                    io2 = StringIO()
                io.write('\n')
        io.write("{:02X}".format(ch))
        if isAscii:
            cch = chr(ch)
            if cch in string.printable and cch not in string.whitespace:
                io2.write(cch)
            else:
                io2.write('.')
        i += 1

    if width > 0 and isAscii:
        miss = width - (i % width)
        io.write(' ' * (miss * 2) + '   ')
        io.write(io2.getvalue())
    io2.close()
    hdump = io.getvalue()
    io.close()
    return hdump

if __name__ == '__main__':
    print(hexdump(b'This is a try for SPOT: \x07\x20\x37\x77\x9F', 7, True))
    with means.NonBlockGetChar() as nbgc:
        run = True
        while run:
            try:
                time.sleep(0.1)
                trapped_char = nbgc.getch()
                if trapped_char is not None:
                    means.flushInput()
                    print('Pressed the key:', trapped_char)
                    if trapped_char == 'q': run = False
            except Exception as ex:
                print('Protocol\'s Exception caught: ' + str(ex))
