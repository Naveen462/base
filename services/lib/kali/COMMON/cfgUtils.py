"""
.. module:: GVRlib.Emv.cfgUtils
   :platform: Unix, Windows
   :synopsis: CSV and XML files management.
This module is in charge to manage CSV files and XML files used to create test cases
"""

import os
import sys
import binascii
from .Enums import Flags, Versus, WKMode, KeyKind, KeyType, KeyUse, CVV

from Crypto.Util.number import long_to_bytes, bytes_to_long


def get_data_path(path=""):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        data_path = os.path.join(sys._MEIPASS, 'sequencer/data/')
    except AttributeError:
        data_path = os.path.join(os.path.split(__file__)[0], 'sequencer/data')
    return os.path.join(data_path, path)


def convertValueToType(value, _type):
    conversionsTable = {
        int: [float, str, bytes, Flags, Versus, WKMode, KeyUse, KeyType, KeyKind, CVV, bool],
        float: [int, str],
        bytes: [int, str, Flags, Versus, WKMode, KeyUse, KeyType, KeyKind, CVV],
        str: [int, bytes],
        Flags: [int, bytes],
        Versus: [int, bytes],
        WKMode: [int, bytes],
        KeyUse: [int, bytes],
        KeyType: [int, bytes],
        KeyKind: [int, bytes],
        CVV: [int, bytes],
        list: [bytes],
        dict: [bytes]
    }
    tv = type(value)
    if tv is _type:
        return value
    elif value is None:
        return None
    if tv not in conversionsTable:
        raise TypeError('Type: ' + str(tv) + 'not found in conversions table!')
    else:
        if _type not in conversionsTable[tv]:
            raise TypeError('No conversion found for type ' +
                            str(_type) + ' to type ' + str(tv) + '!')
    if tv == int:
        if _type is float:
            value = float(value)
        elif _type is str:
            value = str(value)
        elif _type is bytes:
            value = long_to_bytes(value)
        elif _type is bool:
            if value > 0:
                value = True
            else:
                value = False
        elif _type in (Flags, Versus, WKMode, KeyUse, KeyType, KeyKind, CVV):
            value = _type(value)
    elif tv is float:
        if _type is int:
            value = int(value)
        elif _type is str:
            value = str(value)
    elif tv is bytes:
        if _type is int:
            value = bytes_to_long(value)
        elif _type is str:
            value = value.decode('latin-1')
        elif _type in (Flags, Versus, WKMode, KeyUse, KeyType, KeyKind, CVV):
            value = convertValueToType(convertValueToType(value, int), _type)
    elif tv is str:
        if _type is int:
            try:
                value = bytes_to_long(convertValueToType(value, bytes))
            except:
                raise Exception('Unable to convert from str to int')
        elif _type is bytes:
            value = value.encode()
    elif tv in (Flags, Versus, WKMode, KeyUse, KeyType, KeyKind, CVV):
        if _type == int:
            value = int(value)
        elif _type == bytes:
            value = value.encode()
    elif tv == list:
        if _type is bytes:
            buf = b''
            for i in value:
                buf += convertValueToType(i, bytes)
            value = buf
    elif tv == dict:
        if _type == bytes:
            buf = b''
            for k in sorted(value.keys()):
                buf += convertValueToType(value[k], bytes)
            value = buf
    return value


def evaluate(classtype, classmember):
    if classmember is None:
        return None
    classmember = classmember.replace('"', '\\"')
    value = None
    try:                             # ?str?, ?bool?, ?int? and ?float?
        value = eval(classtype + '("' + classmember + '")')
        if isinstance(value, bool):  # Valid values are: True, False, 0 and 1
            try:
                value = eval(classtype + '(' + classmember + ')')
            except NameError:
                pass   # Unknown value, return None
    except SyntaxError:
        pass         # This value produces a syntax error, return None
#   except NameError:                # raise an exception
#   except AttributeError:           # raise an exception
    except ValueError:
        try:                         # ?int?
            value = eval(classtype + '("' + classmember + '", 16)')
        except ValueError:
            pass      # Not able to convert this value as ?int?, return None
        except TypeError:
            try:                     # ?class member?
                value = eval(classtype + '.' + classmember)
#           except NameError:        # raise an exception
#           except AttributeError:   # raise an exception
            except SyntaxError:
                pass  # This value produces a syntax error, return None
            except ValueError:
                pass  # Not able to retrieve this class member, return None
    except TypeError:
        try:                         # ?bytes?
            pre_value = eval(classtype + '("' + classmember + '", "latin-1")')
            value = binascii.unhexlify(pre_value)
#       except NameError:            # raise an exception
        except binascii.Error:
            pass  # Not able to unhexlify this value, return None
        except TypeError:
            pass
    return value


def get_testlist(testlistfile, verbose=False):
    """
    Imports test case from text file formatted as following:
    ``FIELD1 FIELD2 FIELD3.....FIELDn
    TYPE1  TYPE2  TYPE3......TYPEn
    VALUE1 VALUE2 VALUE3.....VALUEn # for test case 1
    VALUE1 VALUE2 VALUE3.....VALUEn # for test case 2
    .................................................
    VALUE1 VALUE2 VALUE3.....VALUEn # for test case n``
    :Parameters:
        - *testlistfile* (string): The complete file path.
        - *verbose* (boolean): Print the number of test imported and the number of the test excluded.
    :Returns: A list of dictionaries. The keys of any single dictionary are the name of the fields put in the first line of the text files. 
    """
    if os.path.isfile(testlistfile):
        testlist = []
        with open(testlistfile, 'r') as tf:
            fields = tf.readline().split()
            types = tf.readline().split()
            if 'Title' not in fields:
                fields.append('Title')
                types.append('str')
                chk_title = True
            else:
                chk_title = False
            if len(fields) != len(types):
                raise Exception('Fields and types are not equally assigned!')
            imp = 0
            exc = 0
            for test in tf:
                test = test.strip()
                if len(test) > 0 and test[0] != '#':
                    try:
                        if chk_title:
                            data = test.split()[0:len(fields) - 1]
                        else:
                            data = test.split()[0:len(fields)]
                        if chk_title:
                            if test.rfind('#') > 0:
                                title = test[test.rfind('#') + 1:]
                                while title.find('  ') >= 0:
                                    title = title.replace('  ', ' ')
                            else:
                                title = None
                            data.append(title)
                        if len(data) == len(fields):
                            values = list(map(evaluate, types, data))
                            testlist.append(dict(zip(fields, values)))
                            imp += 1
                        else:
                            exc += 1
                    except:
                        raise
                else:
                    exc += 1
            if verbose:
                print("List imported: " + str(imp) +
                      " imported, " + str(exc) + " excluded.")
        return testlist
    raise Exception(testlistfile + ' NOT Found!')


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print(
            sys.argv[0] + ": It needs to be provided at least one argument (as file path).")
        sys.exit(1)
    for cfg in sys.argv[1:]:
        if not os.path.exists(cfg):
            print(cfg + ": This file NOT exists.")
            sys.exit(2)
        print('   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print('   >>>>>>>   ' + cfg + ' parameters loading ...   <<<<<<<')
        print('   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        for line in get_testlist(cfg, verbose=True):
            print(line)
