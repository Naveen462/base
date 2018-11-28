import os
import socket


def check_path(path):
    """
    Check if given path is a dir and if it contains at least one file

    Args:
        path(str): path to be checked

    Returns:
        True if path is valid
        False otherwise
    """
    return os.path.isdir(path) and len([f for f in os.listdir(path)]) >= 1


def check_ip(ip):
    """
    Check if given ip address is valid

    Args:
        ip(str): ip address to be checked

    Returns:
        True if ip address is valid
        False otherwise
    """
    try:
        socket.inet_aton(ip)
    except socket.error:
        return False
    return True
