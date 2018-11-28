from .COMMON.TLV import TLV, APDU2TLV
import math

valid_tags = [b'\xe0', b'\xdf\x01', b'\xdf\x02']


def format_to_bytes(_format):
    """ Return a byte code based on format
    Args:
        _format (str): data format

    Returns:
        byte: code for specified format
    """
    _format = _format.lower()
    if _format == 'json':
        return b'\x00'


def bytes_to_format(code):
    """Return a format string base on byte code
    Args:
        code (byte): format code
    Returns:
        str: format string
    """
    if code == 'b\x00':
        return 'json'


def create_header(length, _format):
    """ Return a tlv header.

    Args:
        length (int): data length to be sent
        _format (str): data format

    Returns:
        byte: hexdump of tlv object
    """
    bit_length = math.ceil(length.bit_length() / 8)
    len_tlv = TLV(b'\xdf\x01',  length.to_bytes(bit_length, byteorder='big'))
    format_tlv = TLV(b'\xdf\x02', format_to_bytes(_format))
    tlv = TLV(b'\xe0', len_tlv.hexdump() + format_tlv.hexdump())
    return tlv.hexdump()


def parse_header(header):
    """ Parse a tlv header
    Args:
        header (byte): header to be parsed
    Returns:
        length (int): data length
        format (str): data format
    """
    #parsing the header
    tlv_fields = APDU2TLV(header, 0)[0]
    val_tlv = TLV(tlv_fields[0], tlv_fields[2], tlv_fields[1])
    #parsing length
    hex_len = APDU2TLV(val_tlv.getVal(), 0)[0]
    len_tlv = TLV(hex_len[0], hex_len[2], hex_len[1])
    #parsing format
    hex_format = APDU2TLV(val_tlv.getVal(), 0)[1]
    format_tlv = TLV(hex_format[0], hex_format[2], hex_format[1])
    return int.from_bytes(len_tlv.getVal(), byteorder='big'), bytes_to_format(format_tlv.getVal())


def check_header(tlv):
    """Check header values
    Args:
        tlv (TLV): TLV object
    Returns:
        bool: correctness value"""
    tag = tlv.getTag()
    val = tlv.getVal()
    result = tag in valid_tags
    if tag == b'\xdf\x02':
        result = val == b'\x00'
    return result
