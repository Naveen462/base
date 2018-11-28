"""
Created on Jan 20, 2016

@author: D. Verna
"""

import string


class VerifyOutputRegex(object):
    """
    This class handles the case
    of VerifyOutput tag with type regex.
    
    An example tag value could be B2/!;|n2/A9|b8/01010101|B4/_|n4/C**3|n4/C_3|b8/11_
    
    The '|' is the separator of each block in regex.
    
    Each regex block is formatted as <format><length>/<value>.
    The '/' character is a separator and indicates that <value> follows.
    
    <format> of each block must be expressed as one of the following characters 
    and indicated the format <value> is expressed:
        B:    byte
        n:    nibble
        b:    binary
        
    <length> indicates the length in term of number of digits of <value>
    
    <value> is any sequence of the indicated <format> and <length> digits.
        If any digit has no the right format according to the following rules,
        or the number of digits is different from <length> an exception is raised:
        
            If <format> is:
                B:    any alphanumeric character except '|' and '/' using as separators
                n:    any hex digit
                b:    1 or 0 digits
        
        '*' and '_' are special characters that can be used for any kind of <format>.
        '*' indicates any single character of the given <format>.
        '_' indicates any sequence of character of the given <format>.
        
            examples:
            
                'B4/_' matches any alphanumeric sequence of 4 characters
                
                 'n4/C**3' matches any hex sequence of 4 digits starting with 0xC and ending with 0x3
                 
                 'n4/C_3' is equivalent to 'n4C**3'
                 
                 'b8/11_ matches any binary sequence of 8 starting with 11
                 
            Limitations: only a single '_' must be used in each block     
    """


    def __init__(self, regex):
        if type(regex) != bytes:
            raise ValueError('regex param must have bytes type') 
                
        self._byte_format = b'B'
        self._nibble_format = b'n'
        self._binary_format = b'b'
        self._unrolled_regex = b''
        self._unrolled_regex_len = 0
        self._sequence_skip_char = b'_'
        self._char_skip_char = b'*'
        
        block_separator = b'|'
        value_separator = b'/'
        
        allowed_format = self._byte_format + self._nibble_format + self._binary_format
        special_chars = self._sequence_skip_char + self._char_skip_char

        bytes_allowed = bytes(string.ascii_letters, 'ascii') + bytes(string.digits, 'ascii') + bytes(string.punctuation, 'ascii')
        nibbles_allowed = bytes(string.hexdigits, 'ascii') + special_chars
        binaries_allowed = b'01' + special_chars
        
        regex_blocks = regex.split(block_separator)
        
        self._regex = regex
        
        regex_table = []
        
        for block in regex_blocks:
            
            if len(block) == 0:
                raise ValueError('Invalid regex in VerifyOutput: empty block')
            
            block_format = bytes([block[0]])    #block[0] is an int so we have to turn it back to bytes
            
            if block_format not in allowed_format:
                raise ValueError('Format does not match value in VerifyOutput regex block: ' + block.decode())
            
            regex_table.append(block.split(value_separator))
            
            block_len = regex_table[-1][0].lstrip(allowed_format)
            
            try:
                block_int_len = int(block_len)
            except:
                raise ValueError('Invalid length in VerifyOutput regex block: ' + block.decode())   
            
            if block_format == self._nibble_format:    
                if block_int_len % 2 != 0:
                        raise ValueError('Len must be multiple of 2 for VerifyOutput regex nibble block: ' + block.decode())
            
            if block_format == self._binary_format:
                if block_int_len % 8 != 0:
                    raise ValueError('Len must be multiple of 8 for VerifyOutput regex binary block: ' + block.decode())
            
            block_value = regex_table[-1][1]
            
            if len( block_value.split(self._sequence_skip_char) ) > 2:
                raise ValueError('Only a single _ must be present in a VerifyOutput regex block: ' + block.decode())
                    
            if len(block_value) > block_int_len:
                raise ValueError('Len does not match value in VerifyOutput regex block:' + block.decode())
            
            for char in block_value:
                
                char = bytes([char])    #char is an int so we have to turn it back to bytes
                
                if char == self._char_skip_char:
                    self._unrolled_regex += self._skip_sequence(block_format)
                    continue
                
                if char == self._sequence_skip_char:
                    self._unrolled_regex += self._skip_sequence(block_format, ( block_int_len, block_value  ) )
                    continue

                if block_format == self._byte_format:  
                    if char not in bytes_allowed:  
                        raise ValueError('Invalid value in VerifyOutput regex block: ' + block.decode() )
                    
                    self._unrolled_regex += format( ord(char),'08b' ).encode() #convert to bytes sequence of binary digits and append
                
                if block_format == self._nibble_format:
                    if char not in nibbles_allowed:
                        raise ValueError('Invalid value in VerifyOutput regex block: ' + block.decode() )
                    
                    self._unrolled_regex += format( int( char, 16 ) ,'04b' ).encode()
            
                if block_format == self._binary_format:
                    if char not in binaries_allowed:
                        raise ValueError('Invalid value in VerifyOutput regex block: ' + block.decode() )
                    
                    self._unrolled_regex += char

    def __str__(self):
        return self._regex.decode()

    def __bytes__(self):
        return self._regex

    def checkValue(self, value, len_check = True):
        if type(value) != bytes:
            raise ValueError('value param must have bytes type')
        
        _value = b''
        
        for b in value:
            _value += format( b, '08b' ).encode()
        
        if len_check and len(self._unrolled_regex) != len(_value):
            return False
        
        for bin_index in range( min( len(self._unrolled_regex), len(_value) ) ):
            if self._unrolled_regex[bin_index] == ord(self._char_skip_char):
                continue    #skip '*'
            
            if _value[bin_index] != self._unrolled_regex[bin_index]:
                return False    #byte mismatch
            
        
        return True        
                
    def _skip_sequence(self, block_format, block_len_and_val = ( 0, b'' )):
        
        block_len = block_len_and_val[0]
        block_value = block_len_and_val[1]
        
        block_parts = block_value.split(self._sequence_skip_char)

        sequence_len = sum( len(part) for part in block_parts )
        sequence_len = block_len - sequence_len
        
        len_to_skip = 0
        
        if block_format == self._byte_format:
            len_to_skip = ( 8 if sequence_len == 0 else 8 * sequence_len  )
              
        if block_format == self._nibble_format:
            len_to_skip = ( 4 if sequence_len == 0 else 4 * sequence_len  )
            
        if block_format == self._binary_format:
            len_to_skip = ( 1 if sequence_len == 0 else sequence_len  )

        return len_to_skip * self._char_skip_char
