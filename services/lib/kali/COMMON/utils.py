from .config import Platforms, ConfigUpdate, PLATFORMS_CONFIG
import os


def bitmask(value, mask):
    """Returns a list
        - value can be an int or bin or hex
        - mask = {
            "val1": 0b00000001,
            "val2": 0b00000010,
            "val3": 0b00000100,
            ...
            }
    """
    result = []
    for name, binval in mask.items():
        if binval & value:
            result.append(name)
    return result


def set_env(platform, release_version):
    """
    :param platform: platform selected to set the version
    :param release_version: version to be set
    :return: True if execution has been properly performed
    :raises:
        - TypeError if platform is not a Platforms object;
        - TypeError if release_version is not a string;
    """
    # Checking proper type for platform
    if not isinstance(platform, Platforms):
        raise TypeError("Unexpected value for platform passed: %s" % type(platform).__name__)

    # Checking proper type for release_version
    if not isinstance(release_version, str):
        raise TypeError("Unexpected value for release_version passed: %s" % type(release_version).__name__)

    os.environ[platform.__str__()] = release_version
    return True


def check_env(platform, requested_config):
    """
    :param platform: (config.Platforms) selected plarform
    :param requested_config: (config.ConfigUpdate) requested configuration
    :return: True / False depending of configuration map
    :raises:
        - TypeError if platform is not a Platforms object;
        - TypeError if requested_config is not a string;
    """
    # Checking proper type
    if not isinstance(platform, Platforms):
        raise TypeError("Expecting Platforms not %s" % type(platform).__name__)

    # Checking proper type for requested_config
    if not isinstance(requested_config, ConfigUpdate):
        raise TypeError("Unexpected value for requested_config passed: %s" % type(requested_config).__name__)

    # Returning true as default if platform is not set
    if platform.__str__() not in os.environ.keys():
        return True

    # Extracting available configuration for selected platform
    config_map = PLATFORMS_CONFIG[platform]
    release = ''

    # Selecting all configuration matching with the requested one
    for k in config_map.keys():
        # Getting most matching configuration
        if os.environ[platform.__str__()].startswith(k) and \
                len(os.environ[platform.__str__()]) >= len(k) > len(release):
            release = k

    # No config found for requested release, returning False
    if len(release) == 0:
        return False

    return requested_config in config_map[release]
