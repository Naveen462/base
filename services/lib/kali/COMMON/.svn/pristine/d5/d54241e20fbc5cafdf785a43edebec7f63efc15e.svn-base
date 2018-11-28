from .VerifyOutputRegex import VerifyOutputRegex
from .cfgUtils import convertValueToType


class EmptyBuff(bytes):
    def __init__(self):
        super(bytes, self).__init__()
        self.buff = b""
    
    def __len__(self):
        return len(self.buff)
    
    def __str__(self):
        return self.buff.decode('latin-1')
    
    def __bytes__(self):
        return self.buff
    
    def __instancecheck__(self, instance):
        return type(instance) == EmptyBuff()
    
    def __subclasscheck__(self, subclass):
        return type(subclass) == bytes 
    
    def __eq__(self, other):
        return isinstance(other, EmptyBuff)


class ComparisonObject(list):
    def __init__(self):
        super(ComparisonObject, self).__init__()
        self.prefix = None

    def load(self, new_list):
        if type(new_list) is not list:
            TypeError("Unexpected type for %s " % str(type(self)))
        self.clear()
        for element in new_list:
            self.append(element)
        return True

    def dump(self):
        dump = self.prefix or ""
        dump += ", ".join(str(element) for element in self.__iter__())
        return dump

    def __str__(self):
        return self.dump()


class OrObject(ComparisonObject):
    def __init__(self):
        super(OrObject, self).__init__()
        self.prefix = "One of these elements "

    def check(self, compare):
        # Return true at first positive match
        for element in self.__iter__():
            if isinstance(element, VerifyOutputRegex):
                if element.checkValue(compare, False):
                    return True
            elif type(element) in (DictObject, ListObject, OrObject, NotObject):
                if element.check(compare):
                    return True
            else:
                if not isinstance(compare, type(element)):
                    compare = convertValueToType(compare, type(element))
                if compare == element:
                    return True
        return False


class NotObject(ComparisonObject):
    def __init__(self):
        super(NotObject, self).__init__()
        self.prefix = "None of these elements "

    def check(self, compare):
        # Return false at first positive match
        for element in self.__iter__():
            if isinstance(element, VerifyOutputRegex):
                if element.checkValue(compare, False):
                    return False
            elif type(element) in (DictObject, ListObject, OrObject, NotObject):
                if element.check(compare):
                    return False
            else:
                if not isinstance(compare, type(element)):
                    compare = convertValueToType(compare, type(element))
                if compare == element:
                    return False
        return True


class ListObject(ComparisonObject):
    def __init__(self):
        super(ListObject, self).__init__()
        self.prefix = "All of this elements "

    def check(self, compare):
        # Return false at first negative match
        i = 0
        if len(self) > len(compare):
            return False
        for item in self.__iter__():
            if isinstance(item, VerifyOutputRegex):
                if not item.checkValue(compare[i], False):
                    return False
            elif type(item) in [ListObject, DictObject, OrObject, NotObject]:
                if not item.check(compare[i]):
                    return False
            else:
                item = convertValueToType(item, type(compare[i]))
                if item != compare[i]:
                    return False
            i += 1
        return True


class DictObject(dict):
    def __init__(self):
        super(DictObject, self).__init__()
        self.prefix = ""

    def check(self, compare):
        # return true if all element key:value present in self are also present into compare
        for key in self.keys():
            expected = self[key]
            try:
                returned = compare[key]
            except KeyError:
                # Element expected not returned
                return False
            if type(expected) is VerifyOutputRegex:
                if not expected.checkValue(returned):
                    return False
            elif type(expected) in [ListObject, DictObject, OrObject, NotObject]:
                if not expected.check(returned):
                    return False
            else:
                returned = convertValueToType(returned, type(expected))
                if returned != expected:
                    return False
        return True

    def dump(self):
        return ", ".join("%s: %s" % (str(k),str(self[k])) for k in self.keys())

    def load(self, new_dict):
        if type(new_dict) is not dict:
            TypeError("Unexpected type for DictObject")
        for k in new_dict.keys():
            self[k] = new_dict[k]
        return True

    def __str__(self):
        return self.dump()
