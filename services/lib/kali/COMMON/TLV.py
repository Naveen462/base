#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy
from binascii import hexlify
import math


def pretty_hex(data, pad=0):
    return (" ".join('{:02x}'.format(x) for x in data) + " " * (pad - len(data))).upper()


def APDU2TLV(APDUstr, cmdLen):
    i = 0
    APDUstr = APDUstr[cmdLen:]  # First cmdLen bytes include APP ID and CMD
    apdu_len = len(APDUstr)
    tlv = []
    while i < apdu_len:
        lt = i + 1
        if APDUstr[i] & 0x1F == 0x1F:
            while APDUstr[lt] & 0x80 == 0x80:
                lt += 1
            lt += 1
        T = APDUstr[i:lt]
        i = lt
        if APDUstr[i] & 0x80 == 0x00:
            bit_length = math.ceil((APDUstr[i] & 0x7F).bit_length() / 8)
            L = (APDUstr[i] & 0x7F).to_bytes(bit_length, byteorder='big')
            i += 1
            rl = int.from_bytes(L, byteorder='big')
        else:
            lt = APDUstr[i] & 0x7F
            L = APDUstr[i:i + 1 + lt]
            i += 1 + lt
            rl = int.from_bytes(L[1:], byteorder='big')
        ll = int.from_bytes(L, byteorder='big')
        V = APDUstr[i:i+rl]
        tlv.append([T, L, V])
        i += ll
    return tlv


def TLV2APDU(tlvList):
    return b"".join(x[0] if x[0] else b"" + x[1] if x[1] else b"" + x[2] if x[1] else b"" for x in tlvList)


def createTLV(tag, length, value):
    return TLV(tag, value, length)


class TLVs(object):

    def __init__(self, TLVlist=None):
        self.__list = []
        if type(TLVlist) is list:
            for tlv in TLVlist:
                if type(tlv) is not TLV:
                    raise TypeError("Not all TLV passed are TLV object")
            self.__list = TLVlist

    def __iter__(self):
        return iter(self.__list)

    def __len__(self):
        return len(self.__list)

    def addTLV(self, tlv):
        if type(tlv) is not TLV:
            raise TypeError("try to add no TLV object")
        self.__list.append(tlv)

    def getTLVs(self):
        return self.__list

    def getLen(self):
        return len(self.__list)

    def print_TLVs(self):
        for tlv in self.__list:
            print(tlv.toStr_hex())

    def get_TLV(self, TAG):
        for tlv in self.__list:
            if tlv.getTag() == TAG:
                return tlv
        return None

    def TLVisPresent(self, TLVobj):
        for tlv in self.__list:
            if tlv.compare_tlv(TLVobj):
                return True
        return False

    def compare_tlvs(self, tlvs_compared, indentity=False):
        if type(tlvs_compared) is TLVs:
            for cmpTLV in tlvs_compared:
                if not self.TLVisPresent(cmpTLV):
                    return False
            if indentity:
                return tlvs_compared.compare_tlvs(self)
            return True
        else:
            raise TypeError("Object received is not a TLVs")

    def toStr(self):
        b = ""
        for tlv in self.__list:
            b += tlv.toStr()
        return b

    def hexdump(self):
        b = b""
        for tlv in self.__list:
            b += tlv.hexdump()
        return b

    def pretty_dump(self):
        dump = ""
        pad_t = max([len(x.getTag()) for x in self.__list])
        pad_v = max([len(x.getVal()) for x in self.__list])
        pad_l = max([len(x.getLen()) for x in self.__list])
        for tag in self.__list:
            # Dumping TLV received
            dump += "T: %s | L: %s | V: %s\n" % (pretty_hex(tag.getTag(), pad_t),
                                                 pretty_hex(tag.getLen(), pad_l),
                                                 pretty_hex(tag.getVal(), pad_v),
                                                 )
        return dump[:-1]


class TLV(object):
    def __init__(self, _tag=None, _val=None, _len=None):
        self.__Tag = b''
        self.__Len = b''
        self.__Val = b''

        self.complete = False
        self._tag_complete = False
        self._len_complete = False
        self._value_complete = False
        self._first_tag_byte = False
        self._first_len_byte = False
        self.length = None
        if None not in (_tag, _val):
            self.setTLV(_tag, _val, _len)

    def __str__(self):
        return hexlify(self.hexdump()).decode("latin 1").upper()

    def copy(self):
        return copy.deepcopy(self)
            
    def setTLV(self, tag, val, ln=None):
        self.__Tag = tag
        self.__Val = val
        if ln is not None:
            self.__Len = ln
        else:
            self.__Len = self.calc_len(self.__Val)

    def set_lengh_in_tlv(self, lenght_in_tlv):
        self.__Len = lenght_in_tlv

    def setTLVformAPDU2TLV(self, lst):
        self.setTLV(lst[0][0], lst[0][2], lst[0][1])

    def calculate_len(self):
        ln = len(self.__Val)
        bit_length = math.ceil(ln.bit_length() / 8)
        if ln < 128:
            self.__Len = ln.to_bytes(bit_length, byteorder='big')
        else:
            sz = ln.to_bytes(bit_length, byteorder='big')
            sz_len = math.ceil(0x80 | len(sz).bit_length() / 8)
            self.__Len = (0x80 | len(sz)).to_bytes(sz_len, byteorder='big')+sz

    def read(self, rawdata):
        rawdatalist = list(rawdata)
        return self.__readTag(rawdatalist) and self.__readLen(rawdatalist) and self.__readVal(rawdatalist)

    @staticmethod
    def calc_len(value):
        length = len(value)
        if length <= 127:
            # If length less than 127 bytes -> only one byte needed
            length = length.to_bytes(1, byteorder="big")
        else:
            nbytes = length.bit_length() // 8 + (1 if length.bit_length() % 8 > 0 else 0)
            if nbytes > 127:
                raise ValueError("Data too big to be set in TLV value")
            length = (0x80 | nbytes).to_bytes(1, byteorder="big") + length.to_bytes(nbytes, byteorder="big")
        return length

    def getTag(self):
        return self.__Tag

    def getLen(self):
        return self.__Len

    def getVal(self):
        return self.__Val

    def getTLV(self):
        return self.__Tag + self.__Len + self.__Val
    
    def getSize(self):
        return len(self.__Tag)+len(self.__Len)+len(self.__Val)

    def toStr(self):
        if self.__Tag is not None:
            _tag = hexlify(self.__Tag).decode("utf-8")
        else:
            _tag = ""
        if self.__Len is not None:
            _len = hexlify(self.__Len).decode("utf-8")
        else:
            _len = ""
        if self.__Val is not None:
            _val = hexlify(self.__Val).decode("utf-8")
        else:
            _val = ""
        v_string = "".join(_val[(i*2):(i*2)+2]+" " for i in range(0, len(_val)//2))
        string = "[ " + str(_tag) + " | " + str(_len) + " | " + str(v_string) + " ]"
        return string.upper()

    def hexdump(self):
        if None not in (self.__Tag, self.__Len, self.__Val):
            return self.__Tag + self.__Len + self.__Val
        else:
            return b""

    def compare_tlv(self, TLVcompared):
        if type(TLVcompared) is TLV:
            if TLVcompared.getTag() == self.getTag() and \
               TLVcompared.getLen() == self.getLen() and \
               TLVcompared.getVal() == self.getVal():
                return True
            else:
                return False
        else:
            raise TypeError("Object received is not a TLV")

    # Private stuffs

    def __readTag(self, rawdata):
        tg = []
        while len(rawdata):
            b = rawdata.pop(0)
            tg.append(b)
            if len(tg) == 1 and (ord(b) & 0x1f) == 0x1f:
                continue
            if len(tg) > 1 and (ord(b) & 0x80) == 0x80:
                continue
            self.__Tag = ''.join(c for c in tg)
            return True
        return False 

    def __readLen(self, rawdata):
        self.__Sz = 0
        ln = []
        cnt = 1
        while len(rawdata):
            b = rawdata.pop(0)
            ln.append(b)
            self.__Sz = self.__Sz*256 + ord(b) 
            cnt -= 1
            if len(ln) == 1 and (ord(b) & 0x80) == 0x80:
                self.__Sz = 0
                cnt = ord(b) & 0x7f
                continue
            if cnt == 0:
                self.__Len = ''.join(c for c in ln)
                return True
        return False

    def __readVal(self, rawdata):
        vl = []
        cnt = self.__Sz
        del self.__Sz
        if cnt == 0:
            self.__Val = ''
            return True
        while len(rawdata) and cnt:
            vl.append(rawdata.pop(0))
            cnt -= 1
            if cnt == 0:
                self.__Val = ''.join(c for c in vl)
                return True
        return False

    def populate(self, _byte):
        if self.complete:
            return
        if not self._tag_complete:
            self.__check_tag(_byte)
        elif not self._len_complete:
            self.__check_len(_byte)
            self.length = int.from_bytes(self.__Len, byteorder='big')
        elif not self._value_complete:
            self.__get_value(_byte)

        if self._tag_complete and self._len_complete and self._value_complete:
            self.complete = True

    def __check_tag(self, _byte):
        bt = int.from_bytes(_byte, byteorder='big')
        if (bt & 0x1F != 0x1F and not self._first_tag_byte) or (bt & 0x80 != 0x80 and self._first_tag_byte):
            self._tag_complete = True
        self.__Tag += _byte

    def __check_len(self, _byte):
        bt = int.from_bytes(_byte, byteorder='big')
        if bt & 0x80 == 0 and not self._first_len_byte:
            self._len_complete = True
            self._first_len_byte = True
            self.__Len = _byte
            self._len_bytes = 1
        elif not self._first_len_byte:
            self._len_bytes = _byte
            self._first_len_byte = True
        else:
            self.__Len += _byte
            self._len_bytes -= 1

        if self._len_bytes is not None and self._len_bytes == 0:
            self._len_complete = True

    def __get_value(self, _byte):
        if self.length > 0:
            self.__Val += _byte
            self.length -= 1
        if self.length == 0:
            self._value_complete = True
            self.length = int.from_bytes(self.__Len, byteorder='big')
