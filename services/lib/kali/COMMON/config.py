"""
.. module:: GVRlib.Emv.config
   :platform: Unix, Windows
   :synopsis: Variables definitions and configuration set.

This module contains some variables definitions and configuration set.

"""
from .Enums import Platforms, ConfigUpdate


"""
PLATFORMS_CONFIG rules:
- 1st level indexed by Platforms.* values;
- 2nd level indexed by version labels:
- comparison is done with incremental check, i.e.:
    - PLATFORMS_CONFIG[Platform.example].keys() -> '12.34', '12.56', '12.34.56';
    - if release version set is '12.34.56' ->  selected config = 12.34.56';
    - else if release version set is '12.56' ->  selected config = '12.56';
    - else if release version set is '12.34' ->  selected config = '12.34';
    - else if release version set is '12.34.56.78' ->  selected config = '12.34.56';
"""

PLATFORMS_CONFIG = {
    Platforms.SPOT:
        {
            # All Delta K builds
            "42.11.": [ConfigUpdate.EXTENDED_LOGIN, ConfigUpdate.MAC3_TDES_EXTEND],
            # Latest Delta J builds
            "42.10.12": [ConfigUpdate.MAC3_TDES_EXTEND],
            "42.10.13": [ConfigUpdate.MAC3_TDES_EXTEND],
            "42.10.14": [ConfigUpdate.MAC3_TDES_EXTEND],
            # All PCI5 builds
            "52.11.": [ConfigUpdate.EXTENDED_LOGIN],
            # Latest PCI5 builds aligned with Delta K
            "52.11.03": [ConfigUpdate.MAC3_TDES_EXTEND],
            "52.11.07": [ConfigUpdate.MAC3_TDES_EXTEND]
        },
    Platforms.OMNIA:
        {

        }
}

cleaner = None
mayContinue = False
printEdit = None
endTextEdit = None
dispatchHolder = None
user = None
cwd = None
dirdata = '.'
termios_settings = None
certpath = 'certificates'
