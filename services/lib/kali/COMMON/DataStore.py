"""
.. module:: GVRlib.DataStore3 
   :platform: Unix, Windows
   :synopsis: Utility classes for data store (Python 3).
This module contains some "utility classes" to managing the data store.
"""

import os
import sys
import re
import binascii
import configparser
from . import means


class _ExtendedConfigParser(configparser.RawConfigParser):
    """
    This class implements a *ConfigParser* with enhancements.
    """
    _DEFAULT_INTERPOLATION = configparser.ExtendedInterpolation()
    # Compiled regular expression for matching options with type information
    _OPTYRE = re.compile(r"^(?P<option>\S+?)@@(?P<type>[a-zA-Z0-9&_\.\-]+)$")

    def optionxform(self, optionstr):
        """
        Replacement of the base one to retrieve the type of option.
        :Parameters:
            - *optionstr* (string): Options. 
        """
        if self.reading: # Because when it reads it needs to know the type while it writes it must send as is.
            result = self._OPTYRE.match(optionstr)
            if result is not None:
                self.optionMap[result.group('option')] = result.group('type')
                return result.group('option')
        return optionstr

    def get(self, section, option, raw = False):
        """
        Get an option.
        :Parameters:
            - *section* (float|integer|boolean): TODO. 
            - *option* (string): Option name.
            - *raw* (boolean): Is raw?.
        :Returns: The value of option.
        """
        self.reading = False
        if section is None:
            section = self.default_section
        else:
            if isinstance(section, int) or isinstance(section, float) or isinstance(section, bool):
                section = str(section)
            elif isinstance(section, bytes):
                section = str(binascii.hexlify(section), "utf-8")
            self._validate_value_types(section = section)
            if not super().has_section(section):
                #print('Section not Found: ' + section)
                return None
        value = super().get(section, option, fallback = None)
        if value is not None and option in self.optionMap:
            value_type = self.optionMap[option]
            if value_type == 'float':
                return float(value)
            elif value_type == 'int':
                return int(value)
            elif value_type == 'bool':
                return self._convert_to_boolean(value)
            elif value_type == 'bytes':
                return binascii.unhexlify(bytes(value, "utf-8"))
            elif value_type == 'str':
                return str(binascii.unhexlify(value.encode("utf-8")), "latin-1")
            elif value_type == 'list':
                dataString = value.split('\t')
                dataList = []
                for data in dataString:
                    if data.startswith('float@'):
                        dataList.append(float(data[6:]))
                    elif data.startswith('int@'):
                        dataList.append(int(data[4:]))
                    elif data.startswith('bool@'):
                        dataList.append(self._convert_to_boolean(data[5:]))
                    elif data.startswith('bytes@'):
                        dataList.append(binascii.unhexlify(bytes(data[6:], "utf-8")))
                    elif data.startswith('str@'):
                        dataList.append(str(binascii.unhexlify(data[4:].encode("utf-8")), "latin-1"))
                    else:
                        dataList.append(data)
                return dataList
            else:
                result = re.match(r'^(?P<module>[a-zA-Z0-9_\.]+)&(?P<function>\w+)$', value_type)
                if result is not None:
                    module = result.group('module')
                    obj = __import__ (module, fromlist = [ module[module.rfind('.')+1:] ])
                    func = getattr(obj, result.group('function'), None)
                    if callable(func):
                        try:
                            return func(*value.split())
                        except:
                            means.error._lay('Failed to call the function [' + option + ']: ' + str(sys.exc_info()[1]))
                            return None
                means.error._lay('Failed to recognize the type: ' + option)
                return None
        return value

    def set(self, section, option, value = None):
        """
        Set an option.  Extends *RawConfigParser.set()* by validating type and interpolation syntax on the value.
        :Parameters:
            - *section* (float|integer|boolean): TODO. 
            - *option* (string): Option name.
            - *value* (string): Option raw.
        """
        if section is not None:
            section = self.add_section(section)
        else:
            self.reading = True
        self._validate_value_types(option = option, value = value)
        self.modified = True
        super().set(section, option, value)

    def add_section(self, section):
        """
        Creates a new section in the configuration. Extends *RawConfigParser.add\_section()* by validating if the section name is a string.
        :Parameters:
            - *section* (float|integer|boolean): TODO.
        :Returns: The section's name.
        """
        self.reading = True
        if isinstance(section, int) or isinstance(section, float) or isinstance(section, bool):
            section = str(section)
        elif isinstance(section, bytes):
            section = str(binascii.hexlify(section), "utf-8")
        self._validate_value_types(section = section)
        if not super().has_section(section):
            super().add_section(section)
        return section

    def read(self, fileINI):
        """
        Sets the *INI file* to read/write and read It.
        :Parameters:
            - *fileINI* (string): INI file name.
        """
        self.BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True, 'sure': True, 'accept': True, 'enabled': True,
                               '0': False, 'no': False, 'false': False, 'off': False, 'nope': False, 'reject': False, 'disabled': False}
        self.iniFile = fileINI
        self.reading = True
        self.modified = False
        self.optionMap = {}
        super().read(fileINI)
        self.setBuiltIn(True)

    def _write_section(self, fp, section_name, section_items, delimiter):
        """"
        Helper needed to rearrange option adding type on writing.
        :Parameters:
            - *fp* (string): file pointer.
            - *section\_name* (string): Section name.
            - *section\_items* (list): Items list.
            - *delimiter* (string): Delimiter between sections.
        """
        remanaged_items = [ (key if key not in self.optionMap else key + '@@' + self.optionMap[key], value) for key, value in section_items ]
        super()._write_section(fp, section_name, remanaged_items, delimiter)

    def write(self, end = True):
        """
        Writes changes to the *INI file*.
        :Parameters:
            - *end* (boolean): If ``True`` the *Built-in* flag is enabled.
        """
        if self.modified:
            self.reading = False
            tmpConfig = None if not os.path.exists(self.iniFile) else self.iniFile + '_' + str(os.getpid())
            try:
                if tmpConfig is not None:
                    os.rename(self.iniFile, tmpConfig)
            except:
                means.error._lay('Failed to rename [' + os.path.basename(self.iniFile) + ']: ' + str(sys.exc_info()[1]))
            else:
                restoreConfig = True
                try:
                    configfile = open(self.iniFile, 'w')
                except:
                    means.error._lay('Failed to open [' + os.path.basename(self.iniFile) + ']: ' + str(sys.exc_info()[1]))
                else:
                    try:
                        self.setBuiltIn(False)
                        super().write(configfile)
                        if not end:
                            self.setBuiltIn(True)
                        restoreConfig = False
                    except:
                        means.error._lay('Failed to write [' + os.path.basename(self.iniFile) + ']: ' + str(sys.exc_info()[1]))
                    finally:
                        configfile.close()
                    if tmpConfig is not None:
                        if restoreConfig:
                            try:
                                os.remove(self.iniFile)
                                os.rename(tmpConfig, self.iniFile)
                            except:
                                means.error._lay('Failed to restore [' + os.path.basename(self.iniFile) + ']: ' + str(sys.exc_info()[1]))
                        else:
                            try:
                                os.remove(tmpConfig)
                            except:
                                means.error._lay('Failed to remove [' + os.path.basename(tmpConfig) + ']: ' + str(sys.exc_info()[1]))

    def remove(self, section, option):
        """
        Remove an option and eventually the related section if empty.
        :Parameters:
            - *section* (string): Section name.
            - *option* (string): Option name.
        :Returns: ``True`` if option exist, ``False`` otherwise. 
        """
        self.reading = False
        existed = super().remove_option(section, option)
        if existed and section is not None and section != self.default_section:
            sectdict = self._sections[section]
            if len(sectdict) == 0:
                super().remove_section(section)
        return existed

    def setBuiltIn(self, inside):
        """
        Built\-in section for option set in the codes.
        :Parameters:
            - *inside* (boolean): Is a Built\-in section?
        """
        if inside:
            super().add_section('__BUILTIN__')
            super().set('__BUILTIN__', '__DIR__', os.path.dirname(self.iniFile))
        else:
            super().remove_section('__BUILTIN__')

def isPrintable(theString):
    """
    Checks if a string is printable.
        :Parameters:
            - *theString* (string): String to check.
    :Returns: ``True`` if the string is printable, ``False`` otherwise.
    """
    import string
    printset = set(string.printable)
    return set(theString).issubset(printset)

class DataStore(object):
    """
    This class handles a data store.
    """

    def __init__(self, *, path = None, dirname = 'data', configname = 'config.ini', default_section = 'common', throw = False, readonly = False):
        """
        Initializes a *DataStore* object.
         
        :Parameters:
            - *path* (string): Path to data store directory.
            - *dirname* (string): Data store directory. 
            - *configname* (string): INI file name.
            - *default\_section* (string): Default section name.
            - *throw* (boolean): Throws exceptions?.  
            - *readonly* (boolean): ``True`` if the data store is read\-only, ``False`` if it's writable.  
        """
        # self.dirname = os.path.dirname(__file__)
        self.datapath = os.path.join(os.curdir if path is None else path, dirname)
        if not os.path.exists(self.datapath):
            os.makedirs(self.datapath, mode = 0o777, exist_ok = True)
        self.throw = throw
        self.readonly = readonly
        self.inifile = _ExtendedConfigParser(default_section = default_section, strict = True, allow_no_value = True)
        self.inifile.read(os.path.join(self.datapath, configname))
        self.RSA_FORMAT = self.inifile.get(None, 'FormatOfRSA')
        if self.RSA_FORMAT is None:
            self.RSA_FORMAT = 'PEM'

    def __del__(self):
        if not self.readonly:
            self.inifile.write()

    def sync(self, forcewrite = False):
        """
        If the INI file isn't read-only, writes changes.
        :Parameters:
            - *forcewrite* (boolean): Force the write.
        """
        if forcewrite or not self.readonly:
            self.inifile.write(False)

    def put(self, name, data, section = None):
        """
        Puts a new item to the *Data store*.
        :Parameters:
            - *name* (string): Item name.
            - *data* (int|float|boolean): Item to put in the Data store.
            - *section* (string): Section name.
        """
        if isinstance(data, int) or isinstance(data, float) or isinstance(data, bool):
            self.inifile.set(section, name + '@@' + data.__class__.__name__, str(data))
        elif isinstance(data, bytes):
            self.inifile.set(section, name + '@@' + data.__class__.__name__, str(binascii.hexlify(data), "utf-8"))
        elif isinstance(data, list):
            dataString = None
            for d in data:
                s = None
                if isinstance(d, int) or isinstance(d, float) or isinstance(d, bool):
                    s = d.__class__.__name__ + '@' + str(d)
                elif isinstance(d, bytes):
                    s = d.__class__.__name__ + '@' + str(binascii.hexlify(d), "utf-8")
                elif isinstance(d, str):
                    if isPrintable(d): s = d
                    else: s = d.__class__.__name__ + '@' + str(binascii.hexlify(d.encode("latin-1")), "utf-8")
                if s is not None:
                    if dataString is None: dataString = s
                    else: dataString += '\t' + s
            self.inifile.set(section, name + '@@' + data.__class__.__name__, dataString)
        elif isinstance(data, str):
            if isPrintable(data):
                self.inifile.set(section, name, data)
            else:
                self.inifile.set(section, name + '@@' + data.__class__.__name__, str(binascii.hexlify(data.encode("latin-1")), "utf-8"))
        else:
            if section is None:
                file_ext = ''
            elif isinstance(section, str):
                file_ext = section
            elif isinstance(section, int) or isinstance(section, float) or isinstance(section, bool):
                file_ext = str(section)
            elif isinstance(section, bytes):
                file_ext = str(binascii.hexlify(section), "utf-8")
            else:
                means.error._lay('[ ' + name + ' ] Cannot convert its section: ' + data.__class__.__name__)
                if self.throw:
                    raise means.Error
                else:
                    return False
            try:
                className = data.__class__.__name__
                if className == "_RSAobj":
                    dataToStore = data.exportKey(format = self.RSA_FORMAT)
                    file_ext += '.cryRSA.' + self.RSA_FORMAT
                elif className == "PublicKey" or className == "PrivateKey":
                    dataToStore = data.save_pkcs1(format = self.RSA_FORMAT)
                    file_ext += '.pyRSA.' + self.RSA_FORMAT
                else:
                    means.error._lay('[ ' + name + ' ] Unknown class: ' + className)
                    if self.throw:
                        raise means.Error
                    else:
                        return False
                filepath = os.path.join(self.datapath, name + file_ext)
                with open(filepath, 'wb') as file:
                    file.write(dataToStore)
                file.close()
            except TypeError:
                means.error._lay('[ ' + name + ' ] Unknown type: ' + data.__class__)
                if self.throw:
                    raise means.Error
                else:
                    return False
            except means.Error:
                raise
            except:
                means.error._lay('Unexpected storing error: ' + sys.exc_info()[0])
                if self.throw:
                    raise means.Error
                else:
                    return False
            return True
        return True

    def get(self, name, section = None, remove = False):
        """
        Gets an item from the *Data store*.
        :Parameters:
            - *name* (string): Item name.
            - *section* (string): Section name.
            - *remove* (boolean): Remove the item from the *Data store*?
        """
        data = self.inifile.get(section, name)
        if data is None:
            # Search for stored data file
            if section is None: dataRE = re.compile('^' + name + "\.(?P<type>\w+)\.(?P<ext>\w+)$")
            else: dataRE = re.compile('^' + name + "\.(?P<sect>\w+?)\.(?P<type>\w+?)\.(?P<ext>\w+)$")
            for file in os.listdir(self.datapath):
                fileMatched = dataRE.match(file)
                if fileMatched is not None:
                    filepath = os.path.join(self.datapath, file)
                    dataType = fileMatched.group('type')
                    dataExt = fileMatched.group('ext')
                    if section is None or section == fileMatched.group('sect'):
                        break
            else:
                means.error._lay('NOT Found as stored: ' + name)
                if self.throw:
                    raise means.Error
                else:
                    return None
            with open(filepath, 'rb') as file:
                try:
                    dataRead = file.read()
                    if dataType == 'bytes':
                        data = dataRead
                    elif dataType == 'cryRSA':
                        from Crypto.PublicKey import RSA
                        data = RSA.importKey(dataRead)
                    elif dataType == 'pyRSA':
                        import rsa as RSA
                        try:
                            data = RSA.PrivateKey.load_pkcs1(dataRead, format = dataExt)
                        except:
                            data = RSA.PublicKey.load_pkcs1(dataRead, format = dataExt)
                    else:
                        means.error._lay('Unknown type of stored data: ' + dataType)
                        if self.throw:
                            raise means.Error
                        else:
                            return None
                    if remove:
                        try:
                            os.remove(filepath)
                        except:
                            means.error._lay('Failed to remove < ' + name + ' >: ' + str(sys.exc_info()[1]))
                            if self.throw:
                                raise means.Error
                    return data
                except means.Error:
                    raise
                except:
                    means.error._lay('Unexpected restoring error: ' + str(sys.exc_info()[1]))
                    if self.throw:
                        raise means.Error
                    else:
                        return None
            file.close()
        else:
            if remove:
                self.inifile.remove(section, name)
            return data

    def remove(self, name, section = None):
        """
        Removes an item from the *Data store*.
        :Parameters:
            - *name* (string): Item name.
            - *section* (string): Section name.
        """
        if not self.inifile.remove(section, name):
            # Search for stored data file
            if section is None: dataRE = re.compile('^' + name + "\.(?P<type>\w+)\.(?P<ext>\w+)$")
            else: dataRE = re.compile('^' + name + "\.(?P<sect>\w+?)\.(?P<type>\w+?)\.(?P<ext>\w+)$")
            for file in os.listdir(self.datapath):
                fileMatched = dataRE.match(file)
                if fileMatched is not None:
                    filepath = os.path.join(self.datapath, file)
                    try:
                        os.remove(filepath)
                    except:
                        means.error._lay('Failed to remove < ' + name + ' >: ' + str(sys.exc_info()[1]))
                        if self.throw:
                            raise means.Error
                        else:
                            return
                    break
            else:
                means.error._lay('NOT Found as stored: ' + name)
                if self.throw:
                    raise means.Error
