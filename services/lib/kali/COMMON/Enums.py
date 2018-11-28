#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. module:: GVRlib.Pinpad.Enum3
   :platform: Unix, Windows
   :synopsis: Definitions of enumeration types (Python 3).
Contains definitions of some enumeration types for Pinpad package.
"""

from enum import Enum, unique


class GVRenum(Enum):
    def __int__(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def encode(self):
        return int(self.value).to_bytes(1, "big")


@unique
class Flags(GVRenum):
    """
    Multi-block operation parameter
        - 0x00 Intermediate data block (Not first, Not last)
        - 0x01 First data block
        - 0x02 Last data block
        - 0x03 First and Last data block
    """
    INTERMEDIATE_DATA_BLOCK = 0x00
    START_DATA_BLOCK = 0x01
    END_DATA_BLOCK = 0x02
    FIRSTANDLAST_DATA_BLOCK = 0x03


class Versus(GVRenum):
    """
    Operation required
        - 0x01 ECB encrypt
        - 0x02 ECB decrypt or RSA encrypt/decrypt
        - 0x03 CBC encrypt
        - 0x04 CBC decrypt
        - 0x05 ANSI X9.19 MAC calculation
        - 0x06 DUKPT 1992 MAC calculation
        - 0x07 OFB encrypt
        - 0x08 MAB calculation
        - 0x0A DUKPT MAC IN calculation half size (32bit) nordic
        - 0x0B DUKPT MAC OUT calculation half size (32bit) nordic
        - 0x0C DUKPT CBC encrypt nordic
        - 0x0D DUKPT CBC decrypt nordic
        - 0x0E DUKPT MAC IN calculation full size (64bit)
        - 0x0F MAC calculation ISO16609
        - 0x10 MAC calculation ISO9797-1
        - 0x11 MAC calculation ISO9797-2
        - 0x12 MAC calculation ISO9797-3
        - 0x13 MAC calculation ISO9797-4
        - 0x14 MAC calculation ISO9797-5
        - 0x15 CFB encrypt
        - 0x16 CFB decrypt
        - 0x17 CTR encrypt
        - 0x18 CTR decrypt
    """
    ECB_ENCRYPT = 0x01
    ECB_DECRYPT = 0x02
    RSA_ENCRYPT = 0x02
    RSA_DECRYPT = 0x02
    CBC_ENCRYPT = 0x03
    CBC_DECRYPT = 0x04
    X919_MAC = 0x05
    DUKPT1992_MAC = 0x06
    OFB_ENCRYPT = 0x07
    MAB = 0x08
    DUKPT_MAC_IN_NORDIC = 0x0A
    DUKPT_MAC_OUT_NORDIC = 0x0B
    DUKPT_CBC_ENCRYPT_NORDIC = 0x0C
    DUKPT_CBC_DECRYPT_NORDIC = 0x0D
    DUKPT_MAC_FULL = 0x0E
    MAC_ISO16609 = 0x0F
    MAC_ISO9797_1 = 0x10
    MAC_ISO9797_2 = 0x11
    MAC_ISO9797_3 = 0x12
    MAC_ISO9797_4 = 0x13
    MAC_ISO9797_5 = 0x14
    CFB_ENCRYPT = 0x15
    CFB_DECRYPT = 0x16
    CTR_ENCRYPT = 0x17
    CTR_DECRYPT = 0x18
    CMAC = 0x19
    DUKPT_MAC_IN = 0x1A
    DUKPT_MAC_OUT = 0x1B
    DUKPT_CBC_ENCRYPT = 0x1C
    DUKPT_CBC_DECRYPT = 0x1D
    DUKPT_MAC_MASK6 = 0x1E


class CVV(GVRenum):
    """
        - 0x01 CVV1
        - 0x02 CVV2
        - 0x04 CVVvolvo
    """
    CVV1 = 0x01
    CVV2 = 0x02
    CVVvovlo = 0x04


@unique
class WKMode(GVRenum):
    """
        - 0x00 No WorkingKey
        - 0x01 3DES EDE2 WorkingKey ECB encrypted
        - 0x02 3DES EDE2 WorkingKey CBC encrypted
        - 0x03 3DES EDE2 WorkingKey CFB encrypted
        - 0x04 3DES EDE2 WorkingKey OFB encrypted
        - 0x10 WorkingKey TR31 encoded
    """
    NO_WORKINGKEY = 0x00
    DES3_EDE2_ECB = 0x01
    DES3_EDE2_CBC = 0x02
    DES3_EDE2_CFB = 0x03
    DES3_EDE2_OFB = 0x04
    TR31 = 0x10
    CLEAR = 0xFF


@unique
class KeyUse(GVRenum):
    """
        - 0x01 PIN key
        - 0x02 Data key
        - 0x03 Transport key
        - 0x04 MAC key (implemented only in PINPAD version destined to Canadian market)
        - 0x05 OFFLINE PIN key
        - 0x06 TR-31 KBPK (SPOT M3c 2.1 only) Since version 03.02 these keys are no longer allowed to be downloaded
                                              with this command.
    """
    PIN_KEY = 0x01
    DATA_KEY = 0x02
    TRANSPORT_KEY = 0x03
    MAC_KEY = 0x04
    OFFLINE_PIN_KEY = 0x05
    TR31 = 0x06


@unique
class KeyType(GVRenum):
    """
        - 0x01 DES key
        - 0x02 DUKPT key
        - 0x03 RSA key
        - 0x04 TDES key
        - 0x05 DUKPT-2002 key
    """
    DES_KEY = 0x01
    DUKPT_KEY = 0x02
    RSA_KEY = 0x03
    TDES_KEY = 0x04
    DUKPT_2002_KEY = 0x05


class AutoNumber(GVRenum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj


class KeyKind(AutoNumber):
    """
        - 0x01 DES key
        - 0x02 TDES key
        - 0x03 AES key
        - 0x04 RSA key
        - 0x05 DUKPT key
        - 0x06 DUKPT2K2 key
        - 0x07 TR31 key
    """
    DES = ()
    TDES = ()
    AES = ()
    RSA = ()
    DUKPT = ()
    DUKPT2K2 = ()
    TR31 = ()


class TransportMethod(AutoNumber):
    """
        - 0x01 Legacy Mode
        - 0x02 TR31
        - 0x03 RKL
    """
    LegacyMode = ()
    TR31 = ()
    RKL = ()


class TR31BlockVersion(GVRenum):
    A = "A"
    B = "B"


class TR31Algo(GVRenum):
    AES = "A"
    DES = "D"
    RSA = "R"
    TDES = "T"
    RUNES = "0"


class TR31Mode(GVRenum):
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    G = "G"
    N = "N"
    S = "S"
    V = "V"
    X = "X"
    GVR0 = "0"


class TR31Use(GVRenum):
    B0 = "B0"
    B1 = "B1"
    C0 = "C0"
    D0 = "D0"
    E0 = "E0"
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"
    E5 = "E5"
    E6 = "E6"
    I0 = "I0"
    K0 = "K0"
    K1 = "K1"
    M0 = "M0"
    M1 = "M1"
    M2 = "M2"
    M3 = "M3"
    M4 = "M4"
    M5 = "M5"
    P0 = "P0"
    V0 = "V0"
    V1 = "V1"
    V2 = "V2"
    CMAC02 = "02"
    RUNES = "06"


class TR31Exportability(GVRenum):
    E = "E"
    N = "N"
    S = "S"


@unique
class Platforms(GVRenum):
    SPOT = "SPOT M3/M5/M7 Platform"
    OMNIA = "Omnia Platform"


class ConfigUpdate(GVRenum):
    EXTENDED_LOGIN = "Extra bytes passed for internal/external id (> DeltaK)"
    MAC3_TDES_EXTEND = "New method for MAC3 calculation using the whole triple des key"
