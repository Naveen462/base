#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. module:: COMMON.crypto
   :platform: Unix, Windows
   :synopsis: Encryption and decryption algorithms (Python 3).
This module collects various utility used for operation of encryption and decryption or similar
(pinblock, MAC generation, etc.)
"""

# System modules
import sys
import os
import binascii

# Local Modules
from . import means
from . import config
from .utils import check_env
from .config import Platforms, ConfigUpdate
from Crypto.PublicKey import RSA
import thirdparty.rsa as rsa
from Crypto.Cipher import AES
from Crypto.Cipher import DES
from Crypto.Cipher import DES3
from Crypto.Util.number import long_to_bytes, bytes_to_long
from Crypto.Util import Counter as CTR_Counter
from Crypto.Util.strxor import strxor

if __package__ is not None:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    try:
        import thirdparty
    except ImportError:
        raise Exception('Unable to load thirdparty module')

block_size = DES3.block_size
iv_size = AES.block_size


hexZero = b'\x00'
padding_algo = means.enum('NOPADDING', 'SKIPPING', 'ZERO', 'PKCS7', 'ISO10126', 'ANSI_X923', 'ISO_IEC7816_4')
TEST_MTK = b'0123456701234567'
RSA_TEST_KEY = b"""-----BEGIN RSA PRIVATE KEY-----
MIIEdwIBAAKB+QC89IKq48PVR4OO0t4YBHfaG+Bj9sBe/9WoIGviGnqrinNVl0BB
HR7XU/Fwznd3nWvVwp1pNOBGpnO5cx2m8f93uU475SY79kKQ9ni59HlHbvqZXpOU
loOalENhJkOsXZKfJ2TMiCEHeiglKdk4h1y2VKphA67ekb/BdBX7v2YRxldInC1Q
uKuvSnoj8rnDxUO4soiO9wxbP+bOgazpz7MPv7n0D/seHiHRRLwH7dnDbOYcVdM5
NFEY3EVbyK8JoDiRSJM1meVypHb2AVl5QnBFeG1nHwXtQVlcWjYlXm6ebNmjWJbe
cCr77t6ZjAYV5azf7sHZhQtbPQIBAwKB+H34VxyX1+OFAl83PrqtpTwSlZf51ZSq
jnAVnUFm/HJcTOO6KtYTaeTioPXe+k++R+PXE5t4lYRu99D3aRn2qk/Q3tKYxCf5
gbX5pdFNpi+fUbuUYmMPAmcNgkDELR2TtxTE7d2wFgT8GsNxO3sE6HmNxutXyem2
f9ZNY/wERjogUpErUA8q4n3wQTrZA39ECCREMztHoA2w68vIu/l6ZxE/jTp0MxMx
gx8kD/l3amnkHsxyIshGbQWbcVxND+g274TlArns0kgk4052FpbMCOObUcwPtWCS
xdiHiio4UKE5PJOU2mi043NOuWinBTyUlsTyoOCZzXhrAn0A7CTC07FiJLSKf8ha
oRYz5NfwbaFmW+72CsGw4CYakb6StcvjFHFLF85NG9eftFffl5zOS1bFwo45LoYk
2rtjvCh2UbUdGPyD5fS8U4S9IykcPkNOpBAY4dl3aEh2CC+yc2QU1INwd1OSAgMB
NEq+QEAWnRkRjgu9ceTmlQJ9AMzX98IqDLaAr3iPl8ECF8hclHGWG/BMwADaldZf
AkLUYOJMksv00UngNDgFgtpMMiMdVkthI+gQ05wna5hf7ZjutvwcLNgSmtC1Shmd
Qy0OetIfoWtinCWcZPzoIYa3M5aRl8J7VYH7r17SzcR9vlE+JGmxpvTEyyxyQAkC
fQCdbdc3y5bDIwb/2ucWDs1DOqBJFkQ9SflcgSCVbrxhKbcj3UINoNy6iYi9Omp4
OpUPvd7c5IPXCXt0WW3nJ5fSxaQ2eL4QqFfuoyg3rdNsxhLULN8YCrtBO6TwME6w
H8xM7WM4V6BPjQwBV1Yi3H7VgA8TZgu0B9OhQ0RjAn0AiI/6gXFdzwB0+wplK1a6
hZMNoQ69St3VVecOjuoBgeLrQYhh3U3g2+rNeq5XPDLMF2jkMkDCmrXiaBpHuuqe
ZfR5/Wgd5WG8iyOGu74syLRR4WprnOxoGRLt/fAWWc93ubZlLFI5AVJ06eHegv5+
4NQYRnZvTdiHcvbVWwJ8V42dYpXJmbW710UHdahK+t8JgoO53ajO4sXg0Yds85z9
/4eWwstEOa0/fYWT1V3IaSbfajB9IHGQqhRNgYbU5VxRJsdj6Cqe5ww9KWQ1xoQq
8B7UfuwxY8yexZ1xh2NF2gYpeywScAEnXobi3gos9HDIQhvxLfNRQ4jrew==
-----END RSA PRIVATE KEY-----
"""


def XOR(data1, data2):
    """
    data1 = first operator
    data2 = second operator
    XOR between two strings or two bytes array
    """
    return strxor(data1, data2)


'''
MAC ALGORITHMS
Upper case function name => Generic function
'''


def mac_x919(data, key, size=4):  # Based on MAC 3 algorithm
    """
    Perform a *MAC X919* on a specific data with a specific key (based on *MAC 3 algorithm*).
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.    
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    while len(data) % 8 != 0:
        data += value0

    des_key1 = DES.new(key[:8], DES.MODE_CBC, IV=block_size * value0)
    des_key2 = DES.new(key[:8], DES.MODE_ECB)

    buf = des_key1.encrypt(data)
    buf = buf[-8:]
    buf = des_key2.decrypt(buf)

    des3_key = DES3.new(key, DES3.MODE_ECB)

    buf = des3_key.encrypt(buf)
    return buf[0:size]


def mac_x919_des(data, key, size=4):
    """
    Perform a *MAC X919* on a specific data with a specific key (based on *DES algorithm*).
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    while len(data) % 8 != 0: data += value0

    des_key = DES.new(key, DES.MODE_CBC, IV=block_size * value0)

    buf = des_key.encrypt(data)
    return buf[-8:size-8 if size < 8 else None]


def MAB(data, key, size=8):
    """
    Perform a *MAB algorithm*, based on *MAC1*.
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    oddment = len(data) % block_size
    if oddment != 0:
        oddment = block_size - oddment
        data += value0 * oddment
    if len(key) in (16, 24):

        encryptor = DES3.new(key, DES3.MODE_CBC, value0 * block_size)

    else:

        encryptor = DES.new(key, DES.MODE_CBC, value0 * block_size)

    mab = encryptor.encrypt(data)[-block_size:]
    return mab[:min(size, block_size)]


def mac1(data, tdes_key, size=4):
    """
    *MAC method 1* with Padding method 1 (AS 2805.4.1-2001). If TDES key is used \-\> MAC ISO 16609.
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *tdes\_key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.   
    .. note::
    TODO: move this function to specific AS2805/Utilit.py lib?
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    oddment = len(data) % block_size
    if oddment != 0:
        oddment = block_size - oddment
        data += value0 * oddment

    encryptor = DES3.new(tdes_key, DES3.MODE_CBC, value0 * block_size)

    mab = encryptor.encrypt(data)[-block_size:]
    return mab[:min(size, block_size)]


def mac2(data, tdes_key, size=4):
    """
    *MAC method 2* with Padding method 1 (AS 2805.4.1-2001).
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *tdes\_key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.   
    .. note::
    TODO: move this function to specific AS2805/Utility.py lib?
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    oddment = len(data) % block_size
    if oddment != 0:
        oddment = block_size - oddment
        data += value0 * oddment
    lkey = tdes_key[:block_size]
    rkey = tdes_key[-block_size:]

    encryptor = DES.new(lkey, DES.MODE_CBC, value0 * block_size)
    r_decryptor = DES.new(rkey)
    l_encryptor = DES.new(lkey)

    encrypted_data = encryptor.encrypt(data)
    pre_mab = r_decryptor.decrypt(encrypted_data[-block_size:])
    mab = l_encryptor.encrypt(pre_mab)
    return mab[:min(size, block_size)]


def MAC16609(data, key, size=4):
    # MAC ISO16609 Implements MAC Algorithm1 Padding1 and works only if a TDES key is referred.
    if len(key) not in [16, 24]:
        raise Exception('Only 3DES keys are allowed for MAC16609')
    return MAC1(data, key, size)


def MAC1(data, key, size=4):
    """
    Generic MAC1 algorithm (padding method 1, final iteration 1, output transformation 1).
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.   
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    oddment = len(data) % block_size
    if oddment != 0:
        oddment = block_size - oddment
        data += value0 * oddment
    if len(key) == 8:

        encryptor = DES.new(key, DES.MODE_CBC, value0 * block_size)

    elif len(key) in (16, 24):

        encryptor = DES3.new(key, DES3.MODE_CBC, value0 * block_size)

    else:
        raise Exception('Bad length for MAC1 key: ' + str(len(key)))
    mac = encryptor.encrypt(data)[-block_size:]
    return mac[:min(size, block_size)]


def MAC2(data, key, size=4):
    """
    Generic MAC2 algorithm (padding method 1, final iteration 1, output transformation 2).
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    value_f0 = '\xF0' if isinstance(data, str) else b'\xF0'
    oddment = len(data) % block_size
    if oddment != 0:
        oddment = block_size - oddment
        data += value0 * oddment

    encryptor = DES.new(key[:block_size], DES.MODE_CBC, value0 * block_size)
    enc_data = encryptor.encrypt(data)
    if len(key) == 8:

        encryptor = DES.new(XOR(key, value_f0 * block_size), DES.MODE_CBC, value0 * block_size)

    elif len(key) in (16,24):

        encryptor = DES.new(key[block_size:DES.block_size*2], DES.MODE_CBC, value0 * block_size)

    else:
        raise Exception('Bad length for MAC2 key: ' + str(len(key)))
    mac = encryptor.encrypt(enc_data[-block_size:])
    return mac[:min(size, block_size)]


def MAC3(data, key, size=4):
    """
        Perform a *MAC3* on a specific data with a specific key.
        :Parameters:
            - *data* (bytes array): Data to be MACed.
            - *key* (bytes array): Key value.
            - *size* (integer): MAC length.
        :Returns: The encrypted data.
        """
    if len(key) not in (block_size * 2, block_size * 3):
        raise ValueError("Wrong key lengt (%d) received for MAC3 calculation" % len(key))
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    while len(data) % 8 != 0:
        data += value0

    des_key1 = DES.new(key[:block_size], DES.MODE_CBC, IV=block_size * value0)
    des_key2 = DES.new(key[block_size: block_size * 2], DES.MODE_ECB)
    # des_key3 creation
    if len(key) == block_size * 2 or (not check_env(Platforms.SPOT, ConfigUpdate.MAC3_TDES_EXTEND)):
        des_key3 = DES.new(key[:block_size], DES3.MODE_ECB)
    elif len(key) == block_size * 3 and check_env(Platforms.SPOT, ConfigUpdate.MAC3_TDES_EXTEND):
        des_key3 = DES.new(key[block_size * 2:], DES3.MODE_ECB)
    else:
        raise ValueError("Unable to calculate derived keys with key lengt (%d)" % len(key))

    buf = des_key1.encrypt(data)
    buf = buf[-block_size:]
    buf = des_key2.decrypt(buf)
    buf = des_key3.encrypt(buf)
    return buf[:size]


def MAC4(data, key, size = 4):
    """
    MAC4 algorithm (padding method 1, final iteration 1, output transformation 2).
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.

    """
    if len(data) < 8:
        raise Exception('Bad length for MAC4 data: ' + str(len(data)))
    
    if (len(key) < 16) or (len(key) % 8 != 0) :
        raise Exception('Bad length for MAC4 key: ' + str(len(key)))

    # PADDING
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    oddment = len(data) % block_size
    if oddment != 0:
        oddment = block_size - oddment
        data += value0 * oddment
    
    # KEY DERIVATION 
    k = key[:block_size]
    k1 = key[block_size:block_size*2]
    # Derivation for K2 following SPOT protocol implementation (suggested by ISO16609:2012 - 5.4.2 
    # Approved authentication mechanisms based on ISO/IEC 9797).
    if len(key) == 16: 
        k2 = k1                   # If key length is 16 bytes key the UPM calculate the MAC using K'' = K' 
    else:
        # If key length is 24 bytes key, it's splitted into 3 key blocks K K' and K''
        k2 = key[block_size*2:block_size*3]
    
    # ENCRYPTION(D1,K)
    d1KEncryptor = DES.new(k, DES.MODE_CBC, value0 * block_size)

    h1 = d1KEncryptor.encrypt(data[:block_size])
    
    # ENCRYPTION(H1,K2) 

    h1K2Encryptor = DES.new(k2,  DES.MODE_CBC, value0 * block_size)

    h1 = h1K2Encryptor.encrypt(h1) 
    
    # ENCRYPTION(D2:Dq,K) 
    if len(data) > 8:

        dqKEncryptor = DES.new(k, DES.MODE_CBC, h1)

        hq = dqKEncryptor.encrypt(data[block_size:])
    else:
        hq = h1
    #
       
    # OUTPUT TRANSFORMATION

    hqK1Encryptor = DES.new(k1, DES.MODE_ECB)

    g = hqK1Encryptor.encrypt(hq[-block_size:])    
    
    return g[:min(size, block_size)]   # TRUNCATION
    

def MAC5(data, key, size = 4):
    """
    Generic MAC5 algorithm (padding method 1, final iteration 3, output transformation 1).
    This algorithm is derived from the ISO 9797:1:2011 standard.
    
    :Parameters:
        - *data* (bytes array): Data to be MACed.
        - *key* (bytes array): Key value.
        - *size* (integer): MAC length.
    :Returns: The encrypted data.
    """
    value0 = '\x00' if isinstance(data, str) else b'\x00'
    oddment = len(data) % block_size
    if oddment != 0:
        oddment = block_size - oddment
        data += value0 * oddment
    lkey = key[:block_size]
    rkey = key[block_size:DES.block_size*2]
    macA = MAC1(data, lkey, size)
    macB = MAC1(data, rkey, size)
    return XOR(macA,macB)[:min(size, block_size)]


def CMAC(Key, Message, algo):
    # subkeys
    def Subkeys(Key, algo):
        if algo in ['des3','des']:
            # version for DES
            if algo == 'des3':
                cipher = DES3.new(Key, DES3.MODE_ECB)
            else:
                cipher = DES.new(Key, DES.MODE_ECB)
            Rb = 0x000000000000001B
        elif algo == 'aes':
            cipher = AES.new(Key, AES.MODE_ECB)
            Rb = 0x00000000000000000000000000000087
        else:
            raise ValueError("Unexpected algorithm type received: %d" % str(algo))
        Mask1b = 0x8000000000000000
        Mask2b = 0xFFFFFFFFFFFFFFFF
        CIPHk0 = b'\x00'*CIPH
        # Step 1. Let L = CIPHk(0)
        L = cipher.encrypt(CIPHk0)
        # Step 2. If MSB1(L) = 0, then K1 = L<<1
        #        Else K1 = (L<<1) + Rb
        iL = bytes_to_long(L) 
        if iL & Mask1b == 0:
            iK1 = (iL << 1) & Mask2b
        else:
            iK1 = ((iL << 1) & Mask2b) ^ Rb
        K1 = long_to_bytes(iK1,0)
        # Step 3. If MSB1(K1) = 0, then K2 = K1<<1
        #        Else K2 = (K1<<1) + Rb
        if iK1 & Mask1b == 0:
            iK2 = (iK1 << 1) & Mask2b
        else:
            iK2 = ((iK1 << 1) & Mask2b) ^ Rb
        K2 = long_to_bytes(iK2,0)
        return K1, K2
    if algo in ['des3', 'des']:
        CIPH = 8
    elif algo == 'aes':
        CIPH = 16
    else:
        raise Exception('Undefined algo for CMAC Subkeys derivation: ' + str (algo))
    # Key = Keys[0]+Keys[1]+Keys[2]
    # 1. Generate sub keys
    K1, K2 = Subkeys(Key, algo)
    # 2. Apply padding 10..0 to last block Mn
    padding = b'\x80\x00\x00\x00\x00\x00\x00\x00'
    Mlen = len(Message)
    if Mlen == 0:
        Message = padding
    pM = Message+padding[:(CIPH-Mlen%CIPH)%CIPH]
    # 3. Transform last block Mn
    # if Mn is a not padded block Mn = Mn + K1
    # if Mn is a padded block Mn = Mn + K2
    if Mlen > 0 and Mlen % CIPH == 0:
        K = bytes_to_long(K1)
    else:
        K = bytes_to_long(K2)
    iM = long_to_bytes(K ^ bytes_to_long(pM),8)
    # 4. CBC encryption
    if algo == 'des3':
        cipher = DES3.new(Key, DES3.MODE_CBC, b'\x00'*CIPH)
    elif algo == 'des':
        cipher = DES.new(Key, DES.MODE_CBC, b'\x00'*CIPH)
    else:
        cipher = AES.new(Key, AES.MODE_CBC, b'\x00'*CIPH)
    eM = cipher.encrypt(iM)
    return eM[-CIPH:]


# NORDIC STUFF
def CVV1(key, data):
    if len(data) != 23:
        raise ValueError("CVV1/2 must be calcated on 23 bytes length array")
    if len(key) != 16:
        raise ValueError("CVV1/2 need 16 bytes length array")
    # STEP 1 Construct a string of bits by concatenating (left to right)
    # the right-most four bits of each character of the data elements:
    hex_data = b""
    # Increasing data to make it even (starting also 0 padding)
    data += b"0"
    i = 0
    while i < len(data):
        hex_data += ((int(data[i]) & 0x0F) << 4 | (int(data[i+1]) & 0x0F)).to_bytes(1, "big")
        i += 2
    hex_data = pad(hex_data, length=16,side="RIGHT",value=b"\x00")
    keyA = key[:8]
    keyB = key[8:]
    block1 = hex_data[:8]
    block2 = hex_data[8:]
    # Step 1 Encrypt Block 1 using Key A.
    enc_data = encrypt("DES_ECB", block1, keyA)
    # Step 2 XOR the result of Step 1 with Block 2. Encrypt this value with Key A.
    enc_data = XOR(enc_data, block2)
    enc_data = encrypt("DES_ECB", enc_data, keyA)
    # Step 3 Decrypt the result of Step 2 using Key B.
    dec_data = decrypt("DES_ECB", enc_data, keyB)
    # Step 4 Encrypt the result of Step 3 using Key A
    enc_data = encrypt("DES_ECB", dec_data, keyA)
    # From the result of Step 4, going from left to right, extract all numeric characters of nine or less.
    # Left-justify these digits in a 64 bit field.
    DECnumber = b""
    NotDECnumber = b""
    for c in enc_data:
        ln = (c & 0x0F)       # Low nibble
        hn = (c & 0xF0) >> 4  # High nibble
        for nibble in [hn, ln]:
            if nibble < 0x0A:
                DECnumber += str(nibble).encode()
            else:
                NotDECnumber += str(nibble - 10). encode()
    return (DECnumber + NotDECnumber)[:3]


def CVV2(key, data):
    return CVV1(key, data)


def CVVvolvo(key, data):
    field_3 = data[8:15]
    field_6 = data[19:23]
    field_9 = data[27:28]
    field_10 = data[28:31]
    field_12 = data[32:33]
    ScrambledData16 = field_3 + field_6 + field_9 + field_10 + field_12
    ScrambledData8 = binascii.unhexlify(ScrambledData16.replace(b"=", b"3D"))
    EncData = encrypt("DES_ECB", ScrambledData8, key)
    CVV = b""
    SpareData = b""
    for c in EncData:
        # High nibble and low nibble
        hn = (c & 0xF0) >> 4
        ln = (c & 0x0F)
        for nibble in (hn, ln):
            if nibble < 0x0A:
                CVV += str(nibble).encode()
            else:
                SpareData += str(nibble - 10).encode()
            if len(CVV) == 4:
                break
        if len(CVV) == 4:
            break
    l = len(CVV)
    if l < 4:
        CVV += SpareData[:4-l]
    return CVV


def rsa2img(dump):
    priv_key = RSA.load_key_string(RSA_TEST_KEY)
    buf = dump[:-248]
    cert = dump[-248:]
    decrypted = priv_key.public_decrypt(cert, RSA.no_padding)
    byDecrypted = decrypted[0:243]
    if not isinstance(dump, str) and isinstance(byDecrypted, str):
        byDecrypted = byDecrypted.encode("latin-1")
    if isinstance(dump, str) and not isinstance(byDecrypted, str):
        byDecrypted = byDecrypted.decode("latin-1")
    valueZero = '\x00' if isinstance(dump, str) else b'\x00'
    test_mtk = TEST_MTK if isinstance(dump, str) else TEST_MTK.decode("latin-1")
    buf += byDecrypted
    mac = mac_x919(byDecrypted, test_mtk)
    buf += mac + valueZero
    return buf


def dump_bytestream(data):
    res = '' if isinstance(data, str) else b''
    if type(data) == str:
        for i in data:
            try:
                res += i.encode('latin-1')
            except:
                res += '{:02x}'.format(ord(i))
    else:
        for i in data:
            try:
                res += i.decode('latin-1')
            except:
                try:
                    res += '{:02x}'.format(i).encode('latin-1')
                except:
                    res += i
    return res


def pad(data, *, length = block_size, side = 'RIGHT', value = hexZero):
    """
    Padding data function.
    :Parameters:
        - *data* (bytes array): Data which to apply the padding.
        - *length* (integer): Data lenght.
        - *side* (string): Side which to apply the padding.
        - *value* (byte): Padding content.
    """
    pad_add = length - len(data) % length
    if pad_add == length and len(data) > 0: return data
    if isinstance(data, str) and not isinstance(value, str):
        value = value.decode('latin-1')
    if not isinstance(data, str) and isinstance(value, str):
        value = value.encode('latin-1')
    if side is 'RIGHT':
        return data + pad_add * value
    if side is 'LEFT':
        return pad_add * value + data
    return None


def padding_append(data, *, block_length=block_size, algo=padding_algo.NOPADDING):
    if algo == padding_algo.NOPADDING:
        return data
    elif algo == padding_algo.ZERO:
        return pad(data, length=block_length)
    elif algo == padding_algo.PKCS7:
        numpads = block_length - (len(data) % block_length)
        if isinstance(data, str):
            return data + numpads * chr(numpads)
        else:
            return data + (numpads * chr(numpads)).encode("latin-1")
    elif algo == padding_algo.ISO10126:
        numpads = block_length - (len(data) % block_length)
        padded_part = os.urandom(numpads - 1) + (chr(numpads) if isinstance(data, str) else bytes((numpads,)))
        return data + (padded_part if isinstance(data, bytes) else padded_part.decode("latin-1"))
    elif algo == padding_algo.ANSI_X923:
        numpads = block_length - (len(data) % block_length)
        padded_part = (numpads - 1) * chr(0x00) + chr(numpads)
        return data + (padded_part if isinstance(data, bytes) else padded_part.decode("latin-1"))
    elif algo == padding_algo.ISO_IEC7816_4:
        numpads = block_length - (len(data) % block_length) - 1
        padded_part = chr(0x80) + numpads * chr(0x00)
        return data + (padded_part if isinstance(data, bytes) else padded_part.decode("latin-1"))
    else:
        raise ValueError("Unknown padding algorithm: %s" % algo)


def padding_strip(data, *, block_length=block_size, expected_length=None, algo=padding_algo.NOPADDING):
    len_data = len(data)
    if algo == padding_algo.NOPADDING:
        return data
    elif algo == padding_algo.SKIPPING:
        if not data or len_data % block_length:
            raise ValueError("Byte array of length %d can't be %s-padded" % (len_data, padding_algo.list[algo]))
        if expected_length is None:
            raise ValueError("No expected length found, failed to provides %s" % padding_algo.list[algo])
        return data[:expected_length]
    elif algo == padding_algo.ZERO:
        if not data or len_data % block_length:
            raise ValueError("Byte array of length %d can't be %s-padded" % (len_data, padding_algo.list[algo]))
        for c in data[expected_length:]:
            i = ord(c) if isinstance(data, str) else int(c)
            if i != 0x00:
                raise ValueError("Padding has a wrong byte 0x%02X so can't be %s-padded" % (i, padding_algo.list[algo]))
        return data[:expected_length]
    elif algo == padding_algo.PKCS7 or algo == padding_algo.ISO10126 or algo == padding_algo.ANSI_X923:
        if not data or len_data < block_length or len_data % block_length:
            raise ValueError("Byte array of length %d can't be %s-padded" % (len_data, padding_algo.list[algo]))
        try:
            numpads = ord(data[-1])
        except:
            numpads = data[-1]
        if 0 < numpads <= block_length:
            return data[:-numpads]
        raise ValueError("Byte array ending with 0x%02X can't be %s-padded" % (numpads, padding_algo.list[algo]))
    elif algo == padding_algo.ISO_IEC7816_4:
        if not data or len_data < block_length or len_data % block_length:
            raise ValueError("Byte array of length %d can't be ISO/IEC7816-4-padded" % len_data)
        idx = len_data - 1
        if isinstance(data, str):
            while idx > 0 and ord(data[idx]) == 0x00:
                idx -= 1
            if ord(data[idx]) != 0x80:
                len_data = -1
        else:
            while idx > 0 and int(data[idx]) == 0x00:
                idx -= 1
            if int(data[idx]) != 0x80:
                len_data = -1
        if len_data < 0:
            raise ValueError("Byte array padded with %r can't be ISO/IEC7816-4-padded" % data[idx:])
        return data[:idx]
    else:
        raise ValueError("Unknown padding algorithm: %s" % padding_algo.list[algo])


def generate_key(key_type, key_length=None):
    """
    Generates a specific key.
    :Parameters:
        - *key\_type* (byte): Key type:
            - RSA,
            - DES,
            - DES3.
        - *key_length* (bytes array): Key value.
    :Returns: The generated key.
    """
    key = None
    if key_type == "DES":
        key = os.urandom(block_size)
    elif key_type == "DES3":
        if key_length is None:
            key = os.urandom(2 * block_size)
        else:
            key = os.urandom(key_length)
    elif key_type == "AES":
        if key_length not in (16, 24, 32):
            raise ValueError('Invalid keysize, %s. Should be one of (16, 24, 32).' % key_length)
        key = os.urandom(key_length)
    elif key_type == "RSA":
        if key_length < 1024 or (key_length & 0xff) != 0:
            def genRSApair(length):
                    """
                    Generate RSA private and public key
                    length : RSA key size
                    """
                    (pk, sk) = rsa.newkeys(length)
                    pkObj = RSA.construct((int(pk.n), int(pk.e)))
                    skObj = RSA.construct((int(sk.n), int(sk.e), int(sk.d), int(sk.q), int(sk.p)))
                    return pkObj, skObj
            key = genRSApair(key_length)
        else:
            key = RSA.generate(key_length)
    return key


def decrypt(algo, encrypted_text, key, *,
            iv=None, expected_length=None, pad_algo=padding_algo.NOPADDING, counter=None):
    """
    Utility  function to decrypt encrypted data.
    :Parameters:
        - *algo* (string):
            - DES3\_CBC,
            - DES3\_ECB,
            - DES3\_OFB,
            - AES\_CBC.
        - *encrypted\_text* (bytes array): Text to be decrypted.
        - *key* (bytes array): Key value.
        - *iv* (bytes array): initial vector.
    :Returns: The plain text.
    """
    if iv is None and not algo.endswith('_ECB') and not algo.endswith('_CTR'):
        value0 = '\x00' if isinstance(encrypted_text, str) else b'\x00'
        iv = (iv_size if algo.startswith('AES') else block_size) * value0
    elif callable(iv):
        iv = iv(iv_size if algo.startswith('AES') else block_size)
    if algo == "DES_ECB":
        encryptor = DES.new(key, DES.MODE_ECB)
        plain_text = encryptor.decrypt(encrypted_text)
    elif algo == "DES_CBC":
        encryptor = DES.new(key, DES.MODE_CBC, iv)
        plain_text = encryptor.decrypt(encrypted_text)
    elif algo == "DES_OFB":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        encryptor = DES.new(key, DES.MODE_OFB, iv)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "DES_CFB":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        encryptor = DES.new(key, DES.MODE_CFB, iv, segment_size=8 * block_size)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "DES_CTR":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        if counter is None:
            counter = CTR_Counter.new(block_size * 8, initial_value=0 if iv is None else bytes_to_long(iv))
        encryptor = DES.new(key, DES.MODE_CTR, counter=counter)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "DES3_ECB":
        encryptor = DES3.new(key, DES3.MODE_ECB)
        plain_text = encryptor.decrypt(encrypted_text)
    elif algo == "DES3_CBC":
        encryptor = DES3.new(key, DES3.MODE_CBC, iv)
        plain_text = encryptor.decrypt(encrypted_text)
    elif algo == "DES3_OFB":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        encryptor = DES3.new(key, DES3.MODE_OFB, iv)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "DES3_CFB":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        encryptor = DES3.new(key, DES3.MODE_CFB, iv, segment_size=8 * block_size)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "DES3_CTR":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        if counter is None:
            counter = CTR_Counter.new(block_size * 8, initial_value=0 if iv is None else bytes_to_long(iv))
        encryptor = DES3.new(key, DES3.MODE_CTR, counter = counter)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "AES_ECB":
        encryptor = AES.new(key, AES.MODE_ECB)
        plain_text = encryptor.decrypt(encrypted_text)
    elif algo == "AES_CBC":
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        plain_text = encryptor.decrypt(encrypted_text)
    elif algo == "AES_OFB":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        encryptor = AES.new(key, AES.MODE_OFB, iv)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "AES_CFB":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        encryptor = AES.new(key, AES.MODE_CFB, iv, segment_size=8 * iv_size)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    elif algo == "AES_CTR":
        # Pad the encrypted_text
        length = len(encrypted_text)
        encrypted_text = pad(encrypted_text)
        if counter is None:
            counter = CTR_Counter.new(iv_size * 8, initial_value=0 if iv is None else bytes_to_long(iv))
        encryptor = AES.new(key, AES.MODE_CTR, counter=counter)
        plain_text = encryptor.decrypt(encrypted_text)
        if expected_length is None:
            expected_length = length
        pad_algo = padding_algo.SKIPPING
    else:
        raise Exception("Algo unknown %s" % algo)
    # UnPad the plain_text
    plain_text = padding_strip(plain_text, block_length=iv_size if algo.startswith('AES') else block_size,
                               expected_length=expected_length, algo=pad_algo)
    return plain_text


def encrypt(algo, plain_text, key, *, iv=None, pad_algo=padding_algo.NOPADDING, counter=None):
    """
    Utility function to encrypt a plain text.
    :Parameters:
        - *algo* (string): 
            - DES3\_CBC,
            - DES3\_ECB,
            - DES3\_OFB,
            - AES\_CBC.
        - *plain\_text* (bytes array): Text to be encrypted.
        - *key* (bytes array): Key value.
        - *iv* (bytes array): initial vector.
    :Returns: The encrypted data.
    """
    length = len(plain_text)
    if iv is None and not algo.endswith('_ECB') and not algo.endswith('_CTR'):
        value0 = '\x00' if isinstance(plain_text, str) else b'\x00'
        iv = (iv_size if algo.startswith('AES') else block_size) * value0
    elif callable(iv):
        iv = iv(iv_size if algo.startswith('AES') else block_size)
    # Pad the plain_text
    plain_text = padding_append(plain_text, block_length=iv_size
                                if algo.startswith('AES')
                                else block_size, algo=pad_algo
                                if algo.endswith('_CBC') or algo.endswith('_ECB')
                                else padding_algo.ZERO)
    if algo == "DES_ECB":
        encryptor = DES.new(key, DES.MODE_ECB)
        encrypted_text = encryptor.encrypt(plain_text)
    elif algo == "DES_CBC":
        encryptor = DES.new(key, DES.MODE_CBC, iv)
        encrypted_text = encryptor.encrypt(plain_text)
    elif algo == "DES_OFB":
        encryptor = DES.new(key, DES.MODE_OFB, iv)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "DES_CFB":
        encryptor = DES.new(key, DES.MODE_CFB, iv, segment_size=8 * block_size)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "DES_CTR":
        if counter is None:
            counter = CTR_Counter.new(block_size * 8, initial_value=0 if iv is None else bytes_to_long(iv))
        encryptor = DES.new(key, DES.MODE_CTR, counter=counter)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "DES3_ECB":
        encryptor = DES3.new(key, DES3.MODE_ECB)
        encrypted_text = encryptor.encrypt(plain_text)
    elif algo == "DES3_CBC":
        encryptor = DES3.new(key, DES3.MODE_CBC, iv)
        encrypted_text = encryptor.encrypt(plain_text)
    elif algo == "DES3_OFB":
        encryptor = DES3.new(key, DES3.MODE_OFB, iv)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "DES3_CFB":
        encryptor = DES3.new(key, DES3.MODE_CFB, iv, segment_size=8 * block_size)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "DES3_CTR":
        if counter is None:
            counter = CTR_Counter.new(block_size * 8, initial_value=0 if iv is None else bytes_to_long(iv))
        encryptor = DES3.new(key, DES3.MODE_CTR, counter = counter)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "AES_ECB":
        encryptor = AES.new(key, AES.MODE_ECB)
        encrypted_text = encryptor.encrypt(plain_text)
    elif algo == "AES_CBC":
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypted_text = encryptor.encrypt(plain_text)
    elif algo == "AES_OFB":
        encryptor = AES.new(key, AES.MODE_OFB, iv)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "AES_CFB":
        encryptor = AES.new(key, AES.MODE_CFB, iv, segment_size=8 * iv_size)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    elif algo == "AES_CTR":
        if counter is None:
            counter = CTR_Counter.new(iv_size * 8, initial_value=0 if iv is None else bytes_to_long(iv))
        encryptor = AES.new(key, AES.MODE_CTR, counter=counter)
        encrypted_text = encryptor.encrypt(plain_text)
        if len(encrypted_text) > length:
            encrypted_text = encrypted_text[:length]
    else:
        raise Exception("Algo unknown %s" % algo)
    return encrypted_text


def rsa_decrypt(encrypted_text, key_rsa):
    """
    Utility function to decrypt an encrypted text with the *RSA algorithm*.
    :Parameters:
        - *encrypted\_text* (bytes array): Text to decrypt.
        - *rsa\_key* (bytes array): Key value.
    :Returns: The decrypted text.
    """
    if isinstance(key_rsa, tuple):
        _, key_rsa = key_rsa
    try:
        decrypted_text = rsa.decrypt(encrypted_text, key_rsa, padding=False)
    except:
        try:
            decrypted_text = key_rsa.decrypt(encrypted_text)
        except:
            raise Exception("The key isn't a RSA Private key")
    return decrypted_text


def rsa_encrypt(plain_text, key_rsa):
    """
    Utility function to encrypt a plain text with the *RSA algorithm*.
    :Parameters:
        - *plain\_text* (bytes array): Text to encrypt.
        - *rsa_key* (bytes array): Key value.
    :Returns: The encrypted text.
    """     
    if isinstance(key_rsa, tuple):
        key_rsa, _ = key_rsa
    try:
        encrypted_text = rsa.encrypt(plain_text, key_rsa, padding=False)
    except:
        try:
            encrypted_text = key_rsa.encrypt(plain_text, 0)
        except:
            raise Exception("The key isn't a RSA Public key")
    return encrypted_text


def getPKMAN(*, dirPath=None, fileName='SBPKMAN.DAT'):
    """
    Get *PKMAN* from a *.dat* file.
    :Parameters:
        - *dirPath* (string): File complete path.
        - *name* (string): File name.
    :Returns: *PKMAN*.
    """
    filepath = os.path.join(config.dirdata if dirPath is None else dirPath, fileName)
    if os.path.exists(filepath) and os.path.getsize(filepath) == 521:  # 521 : PKN=7 + MID=2 + MOD=256 + EXP=256
        with open(filepath, 'rb') as file:
            try:
                dataRead = file.read()
#               pkn = int(dataRead[:7], 16)
#               mid = int(dataRead[7:9], 16)
                mod = int(dataRead[9:265], 16)
                exp = int(dataRead[-6:], 16)
#               print('pkMAN info: PKN={:d}, MID={:x}, MOD={:x}, EXP={:x}'.format(pkn, mid, mod, exp))
                data = RSA.construct((mod, exp))
                return data
            except:
                means.error._lay('Unexpected restoring error: ' + str(sys.exc_info()[1]))
                print(means.error)
                return None
    else:
        means.error._lay('Not Found the file: ' + filepath)
        print(means.error)
        return None


def import_RSAkey(path, asFile=True):
    """
    Imports value for RSA key from a text file or a string.
    :Parameters:
        - *path* (string): File path.
        - *asFile* (boolean).
    :Returns: The RSA key.  
    """
    if asFile:
        with open(path, 'r') as f:
            keyfile = f.read()
    else:
        keyfile = path
    if keyfile is None:
        return None
    return RSA.importKey(keyfile)


def ofb_helper(data, key, Stan=None):
    """
    Utility for GenerateMac&Encrypt process (for AS2805 project)
    TODO: move this function to specific AS2805/Utilit.py lib?
    """
    constant = b'\x01\x23\x45\x67\x89\xab\xcd\xef'

    if Stan is None:
            SV = constant
    else:   # Set Starting Value (SV) as the STAN right-justified, zero-filled and XORed with a constant
            SV = XOR(constant, pad(Stan, length=len(constant), side='LEFT'))

    # Padding the plain_text
    pad_num = 0 if len(data) % DES3.block_size == 0 else DES3.block_size - len(data) % DES3.block_size
    buffer = (len(data) + pad_num) * b'\x00'
    result = encrypt("DES3_CBC", buffer, key, iv = SV)
    if pad_num != 0:
        result = result[:-pad_num]

    return XOR(data, result)
