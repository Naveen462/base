#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. module:: GVRlib.dukpt3 
   :platform: Unix, Windows
   :synopsis: DUKPT management (Python 3).
This module contains the **DUKPT** (*Derived Unique Key Per Transaction*) class. 
"""
# System modules
from binascii import unhexlify

# Local Modules
from .crypto import XOR, encrypt as enCrypt, decrypt as deCrypt, mac_x919, mac_x919_des


'''
# Class defined values (private use)
_DUKPT_Keyself.KEYSLEN_DES = 8     # DES key lenght
_DUKPT_Keyself.KEYSLEN_3DES = 16   # 3DES key lenght
_DUKPT_Keyself.DATALEN = 8         # DES/3DES data lenght in bytes
_DUKPT_Keyself.MACLEN = 4          # MAC lenght in bytes
_DUKPT_Keyself.FKR_NUM = 21        # Number of slots in future keys register
_DUKPT_Keyself.SMIDR_LEN = 10      # SMIDR lenght in bytes
_DUKPT_Keyself.SMIDR_OFF = 2       # SMIDR offset in bytes (skipped padding bytes, 0xFF padded)
_DUKPT_Keyself.CNT_OFF = 7         # Counter offset in bytes (locate CNT in SMIDR from SMIDR head)
_DUKPT_Keyself.VAR_PIN_OFF = 7     # Offset for key variant for PIN
_DUKPT_Keyself.VAR_MAC_OFF = 6     # Offset for key variant for MAC
_DUKPT_Keyself.VAR_MAC_OUT_OFF = 5 # Offset for key variant for MAC OUT
'''

class DUKPT_Key:
    """
    This class implements a *DUKPT* key and all related operations.
    In cryptography, *Derived Unique Key Per Transaction* (*DUKPT*) is a key management scheme in which for every transaction, a unique key is used which is derived from a fixed key. Therefore, if a derived key is compromised, future and past transaction data are still protected since the next or prior keys cannot be determined easily. DUKPT is specified in ANSI X9.24 part 1.DUKPT allows the processing of the encryption to be moved away from the devices that hold the shared secret. The encryption is done with a derived key, which is not re-used after the transaction. DUKPT is used to encrypt electronic commerce transactions. While it can be used to protect information between two companies or banks, it is typically used to encrypt PIN information acquired by Point-Of-Sale (POS) devices.
    DUKPT is not itself an encryption standard; rather it is a key management technique. 
    The features of the DUKPT scheme are:
        - enable both originating and receiving parties to be in agreement as to the key being used for a given transaction,
        - each transaction will have a distinct key from all other transactions, except by coincidence,
        - if a present key is compromised, past and future keys (and thus the transactional data encrypted under them) remain uncompromised,
        - each device generates a different key sequence, 
        - originators and receivers of encrypted messages do not have to perform an interactive key-agreement protocol beforehand.
    """
    def __init__(self, keylen):
        """
        Initializes a *DUKPT\_Key* object.
        :Parameters:
            - *keylen* (integer): key length.
        """
        # Class defined values (private use)
        self.KEYSLEN_DES        = 8    # DES key lenght
        self.KEYSLEN_3DES       = 16   # 3DES key lenght
        self.DATALEN            = 8    # DES/3DES data lenght in bytes
        self.MACLEN             = 4    # MAC lenght in bytes
        self.FKR_NUM            = 21   # Number of slots in future keys register
        self.SMIDR_LEN          = 10   # SMIDR lenght in bytes
        self.SMIDR_OFF          = 2    # SMIDR offset in bytes (skipped padding bytes, 0xFF padded)
        self.CNT_OFF            = 7    # Counter offset in bytes (locate CNT in SMIDR from SMIDR head)
        self.VAR_PIN_OFF        = 7    # Offset for key variant for PIN
        self.VAR_MAC_OFF        = 6    # Offset for key variant for MAC IN
        self.VAR_MAC_OUT_OFF    = 4    # Offset for key variant for MAC OUT
        self.VAR_ENC_REQ        = 5    # Offset for key variant for Data Encryption request or both way
        self.VAR_ENC_RES        = 3    # Offset for key variant for Data Encryption response
        self.VAR_MAC_MASK6      = 2    # Offset for key variant for DUKPT MAC mask 6
        self.SMIDR_MASK         = 0xFFFFFFFFFFFFFFE00000
        self._derivation_needed = True
        
        if keylen not in [self.KEYSLEN_DES, self.KEYSLEN_3DES]:
            raise Exception('DUKPT init: Unexpected keylen value')
        self.keyslen = keylen              # key length
        self.shiftr = 1 << (self.FKR_NUM - 1) # shift register
        self.tctr = 0                      # initialize transaction counter to 0
        self.smidr = b'\xff' * self.SMIDR_LEN # SMIDR
        self.insert_counter()              # update smidr with current tctr value
        self.key_ptr = 0                   # Pointer to current key in FKR
        self._fkr = [ b'\x00' * keylen for _ in range(0, self.FKR_NUM)] # Future keys register initialization
        self.ipek = bytes()                # !!! WARNING: unsave storage of IPEK (secret) for reversing Host Key generation !!!

    # PUBLIC
    def initializeKeys(self, init_key_serial_num, init_pin_enc_key):
        """
        TODO.
        :Parameters:
            - *init_key_serial_num* (bytes array): TODO.
            - *init_pin_enc_key* (bytes array): TODO.
        """
        if init_key_serial_num is None or init_pin_enc_key is None:
            raise Exception('DUKPT initializeKeys: At least a parameter is not set')
        if len(init_key_serial_num) < self.SMIDR_LEN or len(init_pin_enc_key) < self.keyslen:
            raise Exception('DUKPT initializeKeys: Unexpected parameters length')
        self.tctr = 0                                   # Reset transaction counter
        self.smidr = init_key_serial_num[:self.SMIDR_LEN]  # set new SMIDR value
        self.insert_counter()                           # Update smidr with current tctr value
        self.key_ptr = self.FKR_NUM - 1                    # Set Key Pointer to FKR initial slot (e.g. 20)
        self.shiftr = 1 << self.key_ptr                 # Reset Shifter Register to initial value (e.g. in bin 100000000000000000000, in hex 0x1000)
        self._fkr[self.key_ptr] = init_pin_enc_key[:self.keyslen]

        # Fill Future Keys Register (FKR) as required in ANSI+X9.24-1-2009
        while self.new_key3() and self.new_key1(): pass # loop over all available FKR slots and store a new generated key in each one

        #self.tctr += 1                                  # increment the transaction counter, invalidating the currently pointed FKR slot
        #self.insert_counter()                           # Update smidr with current tctr value
        self.ipek = init_pin_enc_key[:self.keyslen]     # !!! WARNING: unsave storage of IPEK (secret) for reversing Host Key generation !!!
        # Update SMIDR to align to passed one
        cur_counter = int.from_bytes(init_key_serial_num, byteorder = 'big') & (~self.SMIDR_MASK)
        if cur_counter == 0:
            return
        while True:
            cur_counter_smidr = int.from_bytes(self.smidr, byteorder = 'big') & (~self.SMIDR_MASK)
            if cur_counter == cur_counter_smidr:
                break
            elif cur_counter < cur_counter_smidr:
                raise ValueError("Unable to set current counter")
            else:
                self.derivate_key()
        if cur_counter > 0:
            self.generateHostKeys(init_key_serial_num, init_pin_enc_key)
            
    # PUBLIC
    def generateHostKeys(self, init_key_serial_num, init_pin_enc_key):
        """
        TODO.
        :Parameters:
            - *init_key_serial_num* (bytes array): TODO.
            - *init_pin_enc_key* (bytes array): TODO.
        :Returns: TODO. 
        """
        if init_key_serial_num is None or init_pin_enc_key is None:
            raise Exception('DUKPT generateHostKeys: At least a parameter is not set')
        if len(init_key_serial_num) < self.SMIDR_LEN or len(init_pin_enc_key) < self.keyslen:
            raise Exception('DUKPT generateHostKeys: Unexpected parameters lenght')
        self.smidr = init_key_serial_num[:self.SMIDR_LEN] # set new SMIDR value
        self.extract_counter()                         # extract 'm_ulTCTR' from 'm_uchaSMIDR'
        if self.count_bits(self.tctr) > 10 or self.tctr == 0 or self.tctr >= 0x00200000:
            return False                               # 21 bit overflow = valid key not existing
        self.key_ptr = self.search_bit(self.tctr, self.FKR_NUM, False)
        self.shiftr = 1 << (self.FKR_NUM - 1)             # Reset Shifter Register to initial value (e.g. in bin 100000000000000000000, in hex 0x1000)
        self._fkr[self.key_ptr] = init_pin_enc_key[:self.keyslen]
        while True:
            self.tag1()
            if self.new_key1() == False:
                break
        return True

    # PUBLIC
    def encrypt(self, pin_block):
        """
        Encrypt given pinblock with current pin key.
        :Parameters:
            - *pin\_block* (bytes array): Pinblock to encrypt.
        :Returns: The encrypted pin.    
        """
        if pin_block is None:
            raise Exception('DUKPT encrypt: The pinblock is not initialized')
        if len(pin_block) < self.DATALEN:
            raise Exception('DUKPT encrypt: Lenght of submitted pinblock is less than expected {0} bytes'.format(str(self.DATALEN)))
        if not self.request_pin_entry1():
            return None
        cur_pin_key = self.calculate_variants(self.VAR_PIN_OFF)               # Calculate Current Pin Key (from Current Key in FKR)
        if self.keyslen == self.KEYSLEN_3DES:
            encrypted_pin = self.tdes(pin_block, cur_pin_key, True)        # Encrypt pinblock with current pin key (for TDES)
        else:
            encrypted_pin = self.des_special(pin_block, cur_pin_key, True) # Encrypt pinblock with current pin key (for DES)
        return encrypted_pin

    # PUBLIC
    def decrypt(self, encrypted_pin):
        """
        Decrypt given encrypted pinblock with current pin key.
        :Parameters:
            - *encrypted\_pin* (bytes array): Pin to decrypt.
        :Returns: The decrypted pinblock.   
        """
        if encrypted_pin is None:
            raise Exception('DUKPT decrypt: The encrypted pinblock is not initialized')
        if len(encrypted_pin) < self.DATALEN:
            raise Exception('DUKPT decrypt: Lenght of submitted encrypted pin is less than expected {0} bytes'.format(str(self.DATALEN)))
        if not self.request_pin_entry1():
            return None
        cur_pin_key = self.calculate_variants(self.VAR_PIN_OFF)                # Calculate Current Pin Key (from Current Key in FKR)
        if self.keyslen == self.KEYSLEN_3DES:
            pin_block = self.tdes(encrypted_pin, cur_pin_key, False)        # Decrypt encrypted pinblock with current pin key (for TDES)
        else:
            pin_block = self.des_special(encrypted_pin, cur_pin_key, False) # Decrypt encrypted pinblock with current pin key (for DES)
        self._derivation_needed = True
        return pin_block

    # PUBLIC
    def mac_dukpt(self, input_bytes):
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
        :Returns: TODO.
        """
        
        def hex_to_bin(_in):
            if _in in range(0x30,0x3A):
                return _in & 0x0F
            if _in in range(0x41, 0x47):
                return _in - 0x37
            return 255
        
        def myunhex(_in):
            _out = b''
            i = 0
            while i < len(_in):
                curr = [hex_to_bin(_in[i]),hex_to_bin(_in[i+1])]
                _out += ((curr[0] << 4) | curr[1]).to_bytes(2, 'big')[1].to_bytes(1, 'big')
                i += 2
            return _out 
                   
        if self.keyslen != self.KEYSLEN_DES: #or not self.request_pin_entry1():
            return None
        cur_mac_key = self.calculate_variants(self.VAR_MAC_OFF)                        # Calculate Current MAC Key (from Current Key in FKR)
        if len(input_bytes) <= self.DATALEN*2:                                       # Depending on input bytes len...
            data_tmp = input_bytes.ljust((self.DATALEN*2), b'\xFF')[:self.DATALEN * 2]     # ... FF right pad till 16 bytes
        else:
            data_tmp = input_bytes.ljust((self.DATALEN * 4), b'\xFF')[:self.DATALEN * 4]     # ... FF right pad till 32 bytes
        crypted_tmp = self.des_special(myunhex(data_tmp[:self.DATALEN * 2]), cur_mac_key, True) # encrypt (first part of) padded input bytes
        if len(data_tmp) > (self.DATALEN * 2):                                         # if input_bytes are more than self.DATALEN * 2 ...
            crypted_tmp = self.des_special(XOR(crypted_tmp[:self.DATALEN], myunhex(data_tmp[self.DATALEN * 2:self.DATALEN * 4])), cur_mac_key, True) # ... XOR second part of padded input bytes with crypted data and encrypt it again under current mac key
            
        mac1 = crypted_tmp[0:self.MACLEN]                                              # Extract MAC1
        crypted_tmp = self.des_special(crypted_tmp, cur_mac_key, True)              # Encrypt a last time crypted data under current MAC key
        mac2 = crypted_tmp[0:self.MACLEN]                                              # Extract MAC2
        mac3 = crypted_tmp[self.MACLEN: 2 * self.MACLEN]                                     # Extract MAC3
        return mac1 + mac2 + mac3

    # PRIVATE
    def _mac_x919(self, input_bytes, mask, size=None):
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
            - *size* (integer): ``input_bytes`` size.
        :Returns: TODO.
        """
        if size is None:
            size = self.MACLEN
        if self.keyslen != self.KEYSLEN_3DES or not self.request_pin_entry1():  # not initialised no key produced
            return None
        # PIN and MAC key generation as variant of current key
        cur_mac_key = self.calculate_variants(mask)  # Calculate Current MAC Key (from Current Key in FKR)
        return mac_x919(input_bytes, cur_mac_key, size)

    # PUBLIC
    def mac_x919(self, input_bytes, size = None):
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
            - *size* (integer): ``input_bytes`` size.
        :Returns: TODO.
        """
        return self._mac_x919(input_bytes, self.VAR_MAC_OFF, size)

    def mac_x919_mask6(self, input_bytes, size = None):
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
            - *size* (integer): ``input_bytes`` size.
        :Returns: TODO.
        """
        return self._mac_x919(input_bytes, self.VAR_MAC_MASK6, size)

    # PUBLIC
    def mac_x919_nordic(self, input_bytes, inout): #inout => True = in, false => out
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
            - *inout* (boolean): ``True`` = in, ``False`` = out.
        :Returns: TODO.
        """
        if self.keyslen != self.KEYSLEN_3DES or not self.request_pin_entry1(): # not initialised no key produced
            return None
        # PIN and MAC key generation as variant of current key
        if inout:
            if self.keyslen == self.KEYSLEN_DES: 
                cur_mac_key = XOR(self._fkr[self.key_ptr], b'\x00\x00\x00\x00\x00\xFF\x00\xFF')
                cur_mac_key += cur_mac_key
            else:
                cur_mac_key = XOR(self._fkr[self.key_ptr], b'\x00\x00\x00\x00\x00\x00\xFF\x00\x00\x00\x00\x00\x00\x00\xFF\x00')
        else:
            if self.keyslen == self.KEYSLEN_DES:
                cur_mac_key = XOR(self._fkr[self.key_ptr], b'\x00\x00\x00\x00\x00\xFF\x00\xFF')
                cur_mac_key += cur_mac_key
            else:                                            
                cur_mac_key = XOR(self._fkr[self.key_ptr], b'\x00\x00\x00\x00\x00\xFF\x00\xFF\x00\x00\x00\x00\x00\x00\x00\x00')
        return mac_x919(input_bytes, cur_mac_key)

    # PUBLIC
    def mac_x919_in(self, input_bytes):
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
        :Returns: TODO.
        """
        if self.keyslen not in [self.KEYSLEN_DES, self.KEYSLEN_3DES] or not self.request_pin_entry1(): # not initialised no key produced
            return None
        # PIN and MAC key generation as variant of current key
        #cur_mac_key = self.calculate_variants_Nordic(self.VAR_MAC_OFF, 'IN')                        # Calculate Current MAC Key (from Current Key in FKR)
        cur_mac_key = self.calculate_variants(self.VAR_MAC_OFF)
        if self.keyslen == self.KEYSLEN_DES:
            mac = mac_x919_des(input_bytes, cur_mac_key, self.MACLEN)
        else:
            mac = mac_x919(input_bytes, cur_mac_key, self.MACLEN)
        return mac

    # PUBLIC
    def mac_x919_out(self, input_bytes):
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
        :Returns: TODO.
        """
        if self.keyslen not in [self.KEYSLEN_DES, self.KEYSLEN_3DES]: #or not self.request_pin_entry1(): # not initialised no key produced
            return None
        # PIN and MAC key generation as variant of current key
        cur_mac_key = self.calculate_variants(self.VAR_MAC_OUT_OFF)
        if self.keyslen == self.KEYSLEN_DES:
            mac = mac_x919_des(input_bytes, cur_mac_key, self.MACLEN)
        else:
            mac = mac_x919(input_bytes, cur_mac_key, self.MACLEN)
        return mac

    # PUBLIC
    def mac_x919_full(self, input_bytes):
        """
        TODO.
        :Parameters:
            - *input\_bytes* (bytes array): TODO.
        :Returns: TODO.
        """
        if self.keyslen not in [self.KEYSLEN_DES, self.KEYSLEN_3DES] or not self.request_pin_entry1(): # not initialised no key produced
            return None
        # PIN and MAC key generation as variant of current key
        cur_mac_key = self.calculate_variants_Nordic(self.VAR_MAC_OFF, 'IN')                        # Calculate Current MAC Key (from Current Key in FKR)
        if self.keyslen == self.KEYSLEN_DES:
            mac = mac_x919_des(input_bytes, cur_mac_key, 8)
        else:
            mac = mac_x919(input_bytes, cur_mac_key, 8)
        return mac

    # PUBLIC
    def get_key_serial_nr(self):
        """
        Gets the key serial number.
        :Returns: The key serial number.
        """         

        return self.smidr

    # PUBLIC
    def derivate_key(self):
        """
        TODO.
        :Returns: TODO.
        """         
        if not self.request_pin_entry1() and self.tctr > 0:
            return None
        n_bits = self.count_bits(self.tctr) # Counts the number of '1' bits in TCTR:
                                            # If this is not < 10 '1', it also sums SHIFTR value to TCTR
                                            # for skipping counter values that would have more than 10 '1' bits
        if n_bits >= 10:
            self.tctr += 1 << (self.FKR_NUM - 1 - self.search_bit(self.shiftr, self.FKR_NUM, True))
        else:
            while self.new_key1():          # it selects next FKR position (if any)
                self.new_key3()             # it generates a new key and insert it in FKR
            self.tctr += 1
        #self._fkr[self.key_ptr] = None      # Invalidates current key on FKR
        if self.tctr >= 0x00200000 :        # 21 bit overflow
            self.tctr = 0                   # reset TCTR after 1 milion derivation overflow
                                            # so next time a LOAD will be required 
        self.insert_counter()               # Update smidr with current tctr value
        self._derivation_needed = False
        self.generateHostKeys(self.smidr, self.ipek)
        return self.tctr != 0

    # PRIVATE
    def des_special(self, data, key, action):
        """
        Encrypt or decrypt a data buffer using the *special DES* algorithm.
        :Parameters:
            - *data* (bytes array): Data to encrypt/decrypt.
            - *key* (bytes array): Key.
            - *action* (boolean): ``True`` = encryption, ``False`` = decryption.
        :Returns:  The encrypted/decrypted data buffer.
        """ 
        if self.keyslen == self.KEYSLEN_3DES: # for 3DES keys action is supposed True (ecryption)
            key_variant = b'\xc0\xc0\xc0\xc0\x00\x00\x00\x00\xc0\xc0\xc0\xc0\x00\x00\x00\x00'
            tmp2 = XOR(data[:self.DATALEN], key[self.KEYSLEN_DES:self.KEYSLEN_DES+self.DATALEN])               # 1 - XOR data's byte with key's right byte, put in tmp2
            tmp2 = enCrypt("DES_ECB", tmp2, key[:self.KEYSLEN_DES])                                   # 2 - DEA Encrypt XORed data in tmp2 using key's left byte as DES key, put in tmp2
            tmp2 = XOR(tmp2, key[self.KEYSLEN_DES:self.KEYSLEN_DES+self.DATALEN])                           # 3 - XOR encrypted data in tmp2 with key's right byte, put in tmp2
            key_after_variant = XOR(key[0:self.KEYSLEN_3DES] , key_variant)                           # 4 - XOR key with key_variant array, save as new key
            tmp1 = XOR(data[:self.DATALEN], key_after_variant[self.KEYSLEN_DES:self.KEYSLEN_DES+self.DATALEN]) # 5 - XOR data's byte with right byte of variated key, put in tmp1
            tmp1 = enCrypt("DES_ECB", tmp1, key_after_variant[:self.KEYSLEN_DES])                     # 6 - DEA Encrypt XORed data in tmp1 using key's left byte, put in tmp1
            tmp1 = XOR(tmp1, key_after_variant[self.KEYSLEN_DES:self.KEYSLEN_DES+self.DATALEN])             # 7 - XOR encrypted data in tmp1 with right byte of variated key
            return tmp1 + tmp2
        else: # self.keyslen == self.KEYSLEN_DES
            tmp1 = XOR(data[:self.DATALEN], key[: self.DATALEN])                  # XOR data's byte with key byte, but in tmp
            if action: tmp1 = enCrypt("DES_ECB", tmp1, key[:self.KEYSLEN_DES]) # DEA Encrypt XORed data in tmp using key's byte, put in tmp
            else: tmp1 = deCrypt("DES_ECB", tmp1, key[:self.KEYSLEN_DES])      # DEA Decrypt XORed data in tmp using key's byte, put in tmp
            tmp1 = XOR(tmp1, key[0: self.DATALEN])                             # XOR Encrypted byte in tmp with key byte, but in tmp
            return tmp1

    # PRIVATE
    def tdes(self, pin_block, cur_pin_key, action):  # action = True means encryption, False means decryption
        """
        Encrypt or decrypt a pinblock using the *triple DES ECB* algorithm.
        :Parameters:
            - *pin_block* (bytes array): Data to encrypt/decrypt.
            - *cur_pin_key* (bytes array): Current pin key.
            - *action* (boolean): ``True`` = encryption, ``False`` = decryption.    
        :Returns: The encrypted/decrypted pinblock.
        """ 
        if action: return enCrypt("DES3_ECB", pin_block, cur_pin_key[:self.KEYSLEN_3DES])
        else: return deCrypt("DES3_ECB", pin_block, cur_pin_key[:self.KEYSLEN_3DES])

    # PUBLIC
    def tdes_cbc(self, data, action):  # action = True means encryption, False means decryption
        """
        Encrypt or decrypt a pinblock using the *triple DES CBC* algorithm.
        :Parameters:
            - *data* (bytes array): Data to encrypt/decrypt.
            - *action* (boolean): ``True`` = encryption, ``False`` = decryption.    
        :Returns: The encrypted/decrypted pinblock.
        """         
        if action: 
            return enCrypt("DES3_CBC", data, XOR(self._fkr[self.key_ptr], b'\x00\x00\x00\x00\x00\xFF\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00'), iv = b'\x00' * self.DATALEN)
        else:
            return deCrypt("DES3_CBC", data, XOR(self._fkr[self.key_ptr], b'\x00\x00\x00\x00\xFF\x00\x00\x00\x00\x00\x00\x00\xFF\x00\x00\x00'), iv = b'\x00' * self.DATALEN)
    
    def tdes_cbc_req(self, data):
        cur_key = self.calculate_variants_data_enc(self.VAR_ENC_REQ)
        return enCrypt("DES3_CBC", data, cur_key, iv = b'\x00' * self.DATALEN)
    
    def tdes_cbc_res(self, data):
        cur_key = self.calculate_variants_data_enc(self.VAR_ENC_RES)
        return deCrypt("DES3_CBC", data, cur_key, iv = b'\x00' * self.DATALEN)

    # PROTECTED
    def request_pin_entry1(self):
        """
        TODO.
        :Returns: TODO.
        """ 
        if self.tctr == 0 or self.tctr >= 0x00200000 :
            return False # 21 bit overflow = valid key not existing
        self.key_ptr = self.search_bit(self.tctr, self.FKR_NUM, False)
        self.shiftr = 1 << (self.FKR_NUM - self.key_ptr - 1)
        return True

    # PRIVATE
    def search_bit(self, counter, nbits, versus):
        """
        TODO.
        :Parameters:
            - *counter* (bytes array): TODO.
            - *n_bits* (integer): TODO.
            - *versus* (integer): TODO.
        :Returns: TODO.
        """ 
        if versus: # Scan head -> tail
            pivot = 1 << nbits - 1
            i = 0
            while i < nbits and (counter & pivot) == 0:
                pivot >>= 1
                i += 1
            if i == nbits: i = -1
        else:       # Scan tail -> head
            pivot = 1
            i = nbits - 1
            while i > 0 and (counter & pivot) == 0:
                pivot <<= 1
                i -= 1
        return i

    # PRIVATE
    def insert_counter(self):
        """
        TODO.
        """
        smidr_long = int.from_bytes(self.smidr, byteorder = 'big')
        smidr_long = (smidr_long & self.SMIDR_MASK) | (self.tctr & 0x1FFFFF)
        self.smidr = smidr_long.to_bytes(self.SMIDR_LEN, byteorder = 'big')
    # PRIVATE
    def extract_counter(self):
        """
        TODO.
        """                 
        self.tctr = ((self.smidr[self.CNT_OFF] & 0x1F) << 16) | (self.smidr[self.CNT_OFF + 1] << 8) | self.smidr[self.CNT_OFF + 2]

    # PRIVATE
    def new_key1(self):
        """
        TODO.
        :Returns: TODO
        """ 
        self.shiftr >>= 1 # 1 bit right shift of shift register
        if self.shiftr == 0: return False
        return True

    # PRIVATE
    def new_key3(self):
        """
        TODO.
        :Returns: TODO
        """ 
        smidr_long = int.from_bytes(self.smidr[self.SMIDR_OFF:], byteorder = 'big') # STRIP first 2 bytes from SMIDR value
        smidr_long |= self.shiftr & 0x1FFFFF                                     # binary OR between shift register and SMIDR's right 8 bytes
        tmp1 = smidr_long.to_bytes(self.DATALEN, byteorder = 'big')
        tmp2 = self.des_special(tmp1, self._fkr[self.key_ptr], True)             # over ORed data is performed the OWF Key generation with currently pointed key on FKR
        bit_pos = self.search_bit(self.shiftr, self.FKR_NUM, True)                  # Search bit position on shift register
        self._fkr[bit_pos] = tmp2[:self.keyslen]                                 # Update key in FKR in selected slot (by shift register)
        return True

    # PRIVATE
    def tag1(self):
        """
        TODO.
        :Returns: TODO
        """ 
        if self.shiftr & self.tctr == 0: return                                  # if AND check fails, return
        smidr_long = int.from_bytes(self.smidr[self.SMIDR_OFF:], byteorder = 'big') # STRIP first 2 bytes from SMIDR value
        bitXorMask = ((self.shiftr - 1) & self.tctr) & 0x1FFFFF                  # Define BitXorMask
        smidr_long ^= bitXorMask                                                 # binary XOR between bitXorMask and SMIDR's right 8 bytes
        tmp1 = smidr_long.to_bytes(self.DATALEN, byteorder = 'big')
        tmp2 = self.des_special(tmp1, self._fkr[self.key_ptr], True)             # over XORed data perform OWF Key generation with currently pointed key on FKR
        self._fkr[self.key_ptr] = tmp2[:self.keyslen]                            # Update key in FKR for current key slot
        return True

    # PROTECTED
    def calculate_variants(self, var_num):
        """
        TODO.
        :Parameters:
            - *var\_num* (): TODO
        :Returns: TODO
        """ 
        # The following two lines are necessary if it is called before other requests (i.e.:  after deriveKey) [MAYBE MUST BE A PRIVATE METHOD]
#       if not self.request_pin_entry1():
#           return None
        mask = 0xff << ((self.KEYSLEN_DES - var_num - 1) << 3)
        if self.keyslen == self.KEYSLEN_3DES: mask = (mask << (self.KEYSLEN_DES << 3)) | 0xff << ((self.KEYSLEN_DES - var_num - 1) << 3)
        elif var_num == self.VAR_MAC_OFF: mask |= 0xff # for DUKPT1992 MAC mask is set to 00 00 00 00 00 00 FF FF
        # Variant is calculated as XOR between current key and the PIN/MAC bitmask
        key_variant = int.from_bytes(self._fkr[self.key_ptr], byteorder = 'big')
        key_variant ^= mask
        return key_variant.to_bytes(self.keyslen, byteorder = 'big')[-self.keyslen:]
    
    # PROTECTED
    def calculate_variants_data_enc(self, var_num):
        key = self.calculate_variants(var_num)
        kel = key[:self.KEYSLEN_DES]
        ker = key[self.KEYSLEN_DES:]
        vrl = enCrypt("DES3_CBC", kel, kel + ker, iv = b'\x00' * self.KEYSLEN_DES)
        vrr = enCrypt("DES3_CBC", ker, kel + ker, iv = b'\x00' * self.KEYSLEN_DES)
        return vrl + vrr

    # PROTECTED
    def calculate_variants_Nordic(self, var_num, _type = 'IN'):
        """
        TODO.
        :Parameters:
            - *var\_num* (): TODO
            - *type* (string): TODO
        :Returns: TODO
        """ 
        mask = 0xff << ((self.KEYSLEN_DES - var_num - 1) << 3)
        if _type == 'OUT':
            mask |= 0xff
            if self.keyslen == self.KEYSLEN_3DES: mask <<= self.KEYSLEN_DES << 3
        if _type == 'IN':
            if self.keyslen == self.KEYSLEN_DES: mask |= 0xff
            else: mask = (mask << (self.KEYSLEN_DES << 3)) | 0xff << ((self.KEYSLEN_DES - var_num - 1) << 3)
        # Variant is calculated as XOR between current key and the PIN/MAC bitmask
        key_variant = int.from_bytes(self._fkr[self.key_ptr], byteorder = 'big')
        key_variant ^= mask
        return key_variant.to_bytes(self.keyslen, byteorder = 'big')[-self.keyslen:]
    # PUBLIC
    def calculate_variants_for_3DESwithDUKPT(self, var_num):
        """
        TODO.
        :Parameters:
            - *var\_num* (): TODO
        :Returns: TODO
        """ 
        # This function does not set the last byte in the mask
        # It is useful for 3DES-CBC encryption with DUKPT with mask 3 and 4
        mask = 0xff << ((self.KEYSLEN_DES - var_num - 1) << 3)
        if self.keyslen == self.KEYSLEN_3DES: mask = (mask << (self.KEYSLEN_DES << 3)) | 0xff << ((self.KEYSLEN_DES - var_num - 1) << 3)
        # Variant is calculated as XOR between current key and the PIN/MAC bitmask
        key_variant = int.from_bytes(self._fkr[self.key_ptr], byteorder = 'big')
        key_variant ^= mask
        return key_variant.to_bytes(self.keyslen, byteorder = 'big')[-self.keyslen:]

    def derivation_needed(self):
        return self._derivation_needed
    # PRIVATE
    def count_bits(self, counter):
        """
        TODO.
        :Parameters:
            - *counter* (bytes array): TODO
        :Returns: TODO
        """ 

        nbits = 0
        while counter > 0:
            nbits += counter & 1
            counter >>= 1
        return nbits

if __name__ == '__main__':
    from binascii import hexlify
    from time import time

    init_smidr = unhexlify(b"FFFF9876543210E00000")
    init_pin_key = unhexlify(b"6AC292FAA1315B4D858AB3A3D7D5933A")
    pinblock = unhexlify(b"041274EDCBA9876F")
    mac_data = b"1234567890123456789012345678901234567890"
    pin = b"1234"
    pan = b"4012345678909"

    # verify table for DUKPT2000 (SMIDR, PIN_KEY, MAC_KEY, EPB, MAC)
    dukpt2000_verify_table = [
        [ b"FFFF9876543210E00001", b"042666B49184CF5C68DE9628D0397B36", b"042666B4918430A368DE9628D03984C9", b"1B9C1845EB993A7A", b"BF3DF9F4" ],
        [ b"FFFF9876543210E00002", b"C46551CEF9FD244FAA9AD834130D3B38", b"C46551CEF9FDDBB0AA9AD834130DC4C7", b"10A01C8D02C69107", b"1F05D23A" ],
        [ b"FFFF9876543210E00003", b"0DF3D9422ACA561A47676D07AD6BAD05", b"0DF3D9422ACAA9E547676D07AD6B52FA", b"18DC07B94797B466", b"70D151A4" ],
        [ b"FFFF9876543210E00004", b"279C0F6AEED0BE9A2B2C733E1383AE6E", b"279C0F6AEED041652B2C733E13835191", b"0BC79509D5645DF7", b"00B50910" ],
        [ b"FFFF9876543210E00005", b"5F8DC6D2C845C1DA508DDC048093B8C0", b"5F8DC6D2C8453E25508DDC048093473F", b"5BC0AF22AD87B327", b"581ED2C6" ],
        [ b"FFFF9876543210E00006", b"5E415CB0BAF9F0C3D0C14B63FB62FFBC", b"5E415CB0BAF90F3CD0C14B63FB620043", b"A16DF70AE36158D8", b"39B5EE87" ],
        [ b"FFFF9876543210E00007", b"0C8F780B7C8B492FAE84A9EB2A6CE69F", b"0C8F780B7C8BB6D0AE84A9EB2A6C1960", b"27711C16CB257F8E", b"226C141F" ],
        [ b"FFFF9876543210E00008", b"27F66D5244FF621EAA6F6120EDEB427F", b"27F66D5244FF9DE1AA6F6120EDEBBD80", b"50E55547A5027551", b"40412159" ],
        [ b"FFFF9876543210E00009", b"27E31064FDC565968900E2057F658E81", b"27E31064FDC59A698900E2057F65717E", b"536CF7F678ACFC8D", b"621F9B4F" ],
        [ b"FFFF9876543210E0000A", b"6CF2500A22507C83C776CEADC1E330EB", b"6CF2500A2250837CC776CEADC1E3CF14", b"EDABBA23221833FE", b"7B79E6A3" ],
        [ b"FFFF9876543210E0000B", b"3E8260BA04B2D6DFC01482B3819A1848", b"3E8260BA04B22920C01482B3819AE7B7", b"2328981C57B4BDBA", b"CC92E456" ],
        [ b"FFFF9876543210E0000C", b"B716E1E11CF53D7F726CAEE75C3A62B0", b"B716E1E11CF5C280726CAEE75C3A9D4F", b"038D03CC926CF286", b"1BA8BCA1" ],
        [ b"FFFF9876543210E0000D", b"E072EDF9534053A0B6C581C58FBF25CC", b"E072EDF95340AC5FB6C581C58FBFDA33", b"6C8AA97088B62C68", b"A733F330" ],
        [ b"FFFF9876543210E0000E", b"A80046087F5B8FDB5AAD95E1842908B0", b"A80046087F5B70245AAD95E18429F74F", b"F17C9E1D72CD4950", b"8844EEAA" ],
        [ b"FFFF9876543210E0000F", b"93DD5B956C4878B82E453AAEFD32A555", b"93DD5B956C4887472E453AAEFD325AAA", b"B170F6E7F7F2F64A", b"1B1A40E7" ],
        [ b"FFFF9876543210E00010", b"59598DCBD9BD943F94165CE453585FA8", b"59598DCBD9BD6BC094165CE45358A057", b"D5D9638559EF53D6", b"DB05312F" ],
        [ b"FFFF9876543210E00011", b"2B5F01F4F0CC0515639D523231BF1B5D", b"2B5F01F4F0CCFAEA639D523231BFE4A2", b"D544F8CDD292C863", b"9C4253EB" ],
        [ b"FFFF9876543210E00012", b"9CF640F279C2AE1915F725EEEAC2CB50", b"9CF640F279C251E615F725EEEAC234AF", b"7A21BD10F36DC41D", b"9237DD4E" ],
        [ b"FFFF9876543210E00013", b"C3DF489FDF11534BF03DE97C27DC4CD0", b"C3DF489FDF11ACB4F03DE97C27DCB32F", b"78649BD17D0DFA60", b"5402D529" ],
        [ b"FFFF9876543210E00014", b"658488507721B30E4737FA93F923CB2D", b"6584885077214CF14737FA93F92334D2", b"7E7E16EA0C31AD56", b"99DC2A04" ],
        [ b"FFFF9876543210E00015", b"E161D1956A61F62DF37AFD7F9CC36965", b"E161D1956A6109D2F37AFD7F9CC3969A", b"72105C22EBC791E6", b"2B42A5B7" ],
        [ b"FFFF9876543210E10000", b"2F9A0C0B46ECCBA1F8287A7A071AF54B", b"2F9A0C0B46EC345EF8287A7A071A0AB4", b"19776D96D73AF1E2", b"D9DFF7D6" ],
        [ b"FFFF9876543210E20000", b"DEFDE0EA1043B58D2FA013DE6C4B8F04", b"DEFDE0EA10434A722FA013DE6C4B70FB", b"83F14581B8946B2D", b"AB8E57A9" ],
        [ b"FFFF9876543210E40000", b"9F59E8536BDB056513C856FCCF9A0981", b"9F59E8536BDBFA9A13C856FCCF9AF67E", b"96B3ADCBF9F5219C", b"B72B23BF" ],
        [ b"FFFF9876543210E80000", b"87B9983D9D23047A8D199F5CA0C3DEEC", b"87B9983D9D23FB858D199F5CA0C32113", b"1E0F453FD55FCE45", b"B27DF964" ],
        [ b"FFFF9876543210EFF800", b"F9CDFEBF4F5B1D61B3EC12454527E189", b"F9CDFEBF4F5BE29EB3EC124545271E76", b"33365F5CC6F23C35", b"3F7A0CE1" ],
        [ b"FFFF9876543210EFF801", b"5BEE92627E9782A3911BF619DF72CAC4", b"5BEE92627E977D5C911BF619DF72353B", b"3A86BF003F835C9D", b"72653326" ],
        [ b"FFFF9876543210EFF802", b"64CA2F8AB93F614F1620B00BF77C73FE", b"64CA2F8AB93F9EB01620B00BF77C8C01", b"3DB977D05C36DF3F", b"FB38BE77" ],
        [ b"FFFF9876543210EFF804", b"35A168695B3BA8CC07E871C42021DDC8", b"35A168695B3B573307E871C420212237", b"BA83243305712099", b"22BFAA61" ],
        [ b"FFFF9876543210EFF808", b"12C380FCB72ED33D6FC6079AF63F4778", b"12C380FCB72E2CC26FC6079AF63FB887", b"B0DA04AC90A36D85", b"08602C13" ],
        [ b"FFFF9876543210EFF810", b"D8007C833A1E3CB6C6889B97A68C5400", b"D8007C833A1EC349C6889B97A68CABFF", b"2CF02BD9C309EEDA", b"2E033EBC" ],
        [ b"FFFF9876543210EFF820", b"A9C9FF9B735FDDB6591F296B0BF0FD8F", b"A9C9FF9B735F2249591F296B0BF00270", b"9D1E2F77AEEE81C6", b"A821E7C7" ],
        [ b"FFFF9876543210EFF840", b"0E3E221062CB5EFCA384602783A00405", b"0E3E221062CBA103A384602783A0FBFA", b"40870B0F8BA2011C", b"F765BD9E" ],
        [ b"FFFF9876543210EFF880", b"CA8225C587124D04B87F279C0BE297D8", b"CA8225C58712B2FBB87F279C0BE26827", b"22E340D6ABB40981", b"393982DC" ],
        [ b"FFFF9876543210EFF900", b"906AAC1751D497E5144D52C76C6E1F68", b"906AAC1751D4681A144D52C76C6EE097", b"1A4C10AFBA03A430", b"8A7D5738" ],
        [ b"FFFF9876543210EFFA00", b"2B9E2CE7C27503C8E10B54D2989EA650", b"2B9E2CE7C275FC37E10B54D2989E59AF", b"849763B43E5F9CFF", b"2A15EFF9" ],
        [ b"FFFF9876543210EFFC00", b"F9430DF97508246EC77BE4EF4FDB9111", b"F9430DF97508DB91C77BE4EF4FDB6EEE", b"DEFC6F09F8927B71", b"2EBFA205" ],
        [ b"FFFF9876543210F00000", b"AA4D58DB653EC7B548C75F2F047DD24A", b"AA4D58DB653E384A48C75F2F047D2DB5", b"73EC88AD0AC5830E", b"E771B48A" ]
    ]

    # verify table for DUKPT (SMIDR, PIN_KEY, MAC_KEY, EPB, MAC)
    dukpt_verify_table  = [
        [ b"FFFF9876543210E00001", b"35FDB4BBAEE6A293", b"35FDB4BBAEE65D93", b"6B1431D0D9B23093", b"1238716E08B239B3E5DE7138" ],
        [ b"FFFF9876543210E00002", b"1A3CD4AB030F02BB", b"1A3CD4AB030FFDBB", b"B76997F83C1479DB", b"0B3EE955D576F08E934A6981" ],
        [ b"FFFF9876543210E00003", b"1998AA279AA21032", b"1998AA279AA2EF32", b"925BC2A39652CF75", b"FF4D991CE3B1948B0488C0FC" ],
        [ b"FFFF9876543210E00004", b"4D2ED4E7D411C27D", b"4D2ED4E7D4113D7D", b"8E180C51E598ED9C", b"5C3BFCAE24D78E7A23903810" ],
        [ b"FFFF9876543210E00005", b"28EBB08D6CF7D682", b"28EBB08D6CF72982", b"C799F1C4E638BAD4", b"431F8B2346D28D3AD3B12299" ],
        [ b"FFFF9876543210E00006", b"81DDC59C51F89EC5", b"81DDC59C51F861C5", b"1E0961DA7A131C31", b"1170113E51AD82916369262A" ],
        [ b"FFFF9876543210E00007", b"21813BBA85CF416A", b"21813BBA85CFBE6A", b"1C4C5CDFED8E8777", b"E32D47CE0E4B1056D36F1717" ],
        [ b"FFFF9876543210E00008", b"34E5014B8E997DE8", b"34E5014B8E9982E8", b"8772B46D98DC8444", b"DAECBABBDB95D10618412735" ],
        [ b"FFFF9876543210E00009", b"1BC9DD89F13DAD70", b"1BC9DD89F13D5270", b"8DC939C56D0FD13C", b"024CBA298A88580CC629AD3C" ],
        [ b"FFFF9876543210E0000A", b"C5730F52B823E30B", b"C5730F52B8231C0B", b"CFB9B25BA6875971", b"C608754DA167412F672D1752" ],
        [ b"FFFF9876543210E0000B", b"B5990289A9CDB5FB", b"B5990289A9CD4AFB", b"23CB8282DF457BFC", b"C7525F252DE7EA8057F9651A" ],
        [ b"FFFF9876543210E0000C", b"FA000A709DF2808E", b"FA000A709DF27F8E", b"6977948EAEEE59D1", b"45AD360198F94915A4B3B2D9" ],
        [ b"FFFF9876543210E0000D", b"02D6250E1C06009D", b"02D6250E1C06FF9D", b"F4D14F00470C69FD", b"6767C241240CA20E9E1F55BA" ],
        [ b"FFFF9876543210E0000E", b"840020C3990C8CDB", b"840020C3990C73DB", b"15717318C288776D", b"BFB8D1FBC0631C135E1C6316" ],
        [ b"FFFF9876543210E0000F", b"E57F414FE873E0E6", b"E57F414FE8731FE6", b"C578B541B9A58A5B", b"AA4774C7924EB60B0CBE8A2E" ],
        [ b"FFFF9876543210E00010", b"2F7EEF21B68B8BBC", b"2F7EEF21B68B74BC", b"6268FFC127118969", b"023A267471471E0DEB205224" ],
        [ b"FFFF9876543210E00011", b"F393B7D63A5A761B", b"F393B7D63A5A891B", b"A43B7FE9E3426E4E", b"9E235E5E399A70AE524E4E65" ],
        [ b"FFFF9876543210E00012", b"72076E53243EC5AA", b"72076E53243E3AAA", b"0664AB26B1D3BC95", b"BC359085EF4584D308D4E62A" ],
        [ b"FFFF9876543210E00013", b"932DA0370FDEACA8", b"932DA0370FDE53A8", b"20013153EC69EB5D", b"A405E3AED6F1C2A9E24E379A" ],
        [ b"FFFF9876543210E00014", b"86D247E0E1567868", b"86D247E0E1568768", b"8C003174CFC5F0AF", b"85177F99804DBDB7987E223F" ],
        [ b"FFFF9876543210E00015", b"D6395F8E660EE72D", b"D6395F8E660E182D", b"934A85AC28AFE4AC", b"1F7111BBBCDE4D18756B39F4" ],
        [ b"FFFF9876543210E10000", b"D515CFBB8257EF9C", b"D515CFBB8257109C", b"4E2F0DF28C37698A", b"7808154E384CE3696D395312" ],
        [ b"FFFF9876543210E20000", b"7BCBCFE0335C2BD3", b"7BCBCFE0335CD4D3", b"FFF38FDCBE5ACBD7", b"483A9E6225DB52E81F0523D4" ],
        [ b"FFFF9876543210E40000", b"B2B27F021F67A100", b"B2B27F021F675E00", b"58ECCB3DA8296EC8", b"D6A4ED1EB6FCB1886A526A97" ],
        [ b"FFFF9876543210E80000", b"D75A2E8DA84526AF", b"D75A2E8DA845D9AF", b"1A556E94C8AE1C0B", b"7A6A7847DB97C20BFFAA07D9" ],
        [ b"FFFF9876543210EFF800", b"653E5B68A791E24E", b"653E5B68A7911D4E", b"A6552D24B01E71A0", b"08E1A9FA3E6FF81F68ECD518" ],
        [ b"FFFF9876543210EFF801", b"B2752D548F8E2D3E", b"B2752D548F8ED23E", b"F415E7192C3571F7", b"932A5F7DA41DF53FBE85E1A1" ],
        [ b"FFFF9876543210EFF802", b"0C5B794CEEBC88B2", b"0C5B794CEEBC77B2", b"53AD3705F09170FD", b"37819B0A5518F433D4D9DB48" ],
        [ b"FFFF9876543210EFF804", b"65108DBAB6DB4B28", b"65108DBAB6DBB428", b"8590E369C55697F7", b"7D866E70259C11793CDAB02F" ],
        [ b"FFFF9876543210EFF808", b"4E380860A00C70EE", b"4E380860A00C8FEE", b"D8ABBC5DD0CE64C6", b"DD25D0CA4F68430A26F66DD9" ],
        [ b"FFFF9876543210EFF810", b"D3B0827129F45E46", b"D3B0827129F4A146", b"B436A434F9944196", b"2B2989CCB9B6B5F987C4ABB6" ],
        [ b"FFFF9876543210EFF820", b"7EDCEFCD9401D938", b"7EDCEFCD94012638", b"AD69A6C398EBCC85", b"51097EE9334007CFA6B81F38" ],
        [ b"FFFF9876543210EFF840", b"17AC1DD1543D0ACF", b"17AC1DD1543DF5CF", b"4F12869C522A50D4", b"DBA71EF9787A9838EB759190" ],
        [ b"FFFF9876543210EFF880", b"0067318AA16525C0", b"0067318AA165DAC0", b"F08F3B16E335EC9A", b"558EB0042DF1361154B6601F" ],
        [ b"FFFF9876543210EFF900", b"3E1720D0FAE374F4", b"3E1720D0FAE38BF4", b"F5813F26E84C48BB", b"1922619299FA0D3137E6EBD7" ],
        [ b"FFFF9876543210EFFA00", b"536644BC7150BAF9", b"536644BC715045F9", b"D166C62FDB58AACB", b"EA112FD80B33DB206752F8AE" ],
        [ b"FFFF9876543210EFFC00", b"3B4926EA7DFB7CD7", b"3B4926EA7DFB83D7", b"6DEF7FD593810AC7", b"5D68BD69F94A316C91839434" ],
        [ b"FFFF9876543210F00000", b"A101F43AFE98FEB7", b"A101F43AFE9801B7", b"3FAC6F8763C0B60C", b"3AA3AFAB9C46C993CF81A7A3" ]
    ]

    for keyType in ( 8, 16 ):
        Key = DUKPT_Key(keyType)
        print(">>> Starting test in " + ( "DUKPT2000" if keyType == 16 else "DUKPT" ) + " mode <<<")
        Key.initializeKeys(init_smidr, init_pin_key)
        condition = True
        iNumUnv = 0
        iNumOk = 0
        iNumErr = 0
        iNumLoops = 0
        startTimeMsec = time()
        while condition:
            iNumLoops += 1
            smidr = Key.get_key_serial_nr()
            epb = Key.encrypt(pinblock)
            pin_var = Key.calculate_variants(7)
            mac_var = Key.calculate_variants(6)
            mac = Key.mac_x919(mac_data) if keyType == 16 else Key.mac_dukpt(mac_data)
            SMIDR = hexlify(smidr).upper()
            PINVAR = hexlify(pin_var).upper()
            MACVAR = hexlify(mac_var).upper()
            EPB = hexlify(epb).upper()
            MAC = hexlify(mac).upper()
            verify_table = dukpt2000_verify_table if keyType == 16 else dukpt_verify_table
            for verify_item in verify_table:
                if SMIDR == verify_item[0]:
                    Key4Pin = DUKPT_Key(keyType)
                    Key4Pin.generateHostKeys(smidr, init_pin_key)
                    DecData = Key4Pin.decrypt(epb)
                    if DecData != pinblock:
                        bOk = False
                    print("SMIDR=", SMIDR, " PINVAR=", PINVAR, sep = "", end = "")
                    bOk = True
                    if PINVAR != verify_item[1]:
                        print("(expected=", verify_item[1], ")", sep = "", end = "")
                        bOk = False
                    print(" MACVAR=", MACVAR, sep = "", end = "")
                    if MACVAR != verify_item[2]:
                        print("(expected=", verify_item[2], ")", sep = "", end = "")
                        bOk = False
                    print(" EPB=", EPB, sep = "", end = "")
                    if EPB != verify_item[3]:
                        print("(expected=", verify_item[3], ")", sep = "", end = "")
                        bOk = False
                    print(" MAC=", MAC, sep = "", end = "")
                    if MAC != verify_item[4]:
                        print("(expected=", verify_item[4], ")", sep = "", end = "")
                        bOk = False
                    if bOk:
                        print("(OK)")
                        iNumOk += 1
                    else:
                        print("(FAIL)")
                        iNumErr += 1
                    break;
            else:
                iNumUnv += 1
#                   print("Failed to find SMIDR: " + SMIDR + " (EPB=" + EPB + " MAC=" + MAC + " unverified)!")
            condition = Key.derivate_key()
        elapsedMsec = time() - startTimeMsec
        print('Done on {:.2f} seconds for {:d} computations (ok={:d}, fail={:d}, unverified={:d})'.format(elapsedMsec, iNumLoops, iNumOk, iNumErr, iNumUnv))
