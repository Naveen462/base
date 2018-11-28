import os
from configparser import ConfigParser
from ..defines import SECTION_STATUS, FREE_STATE


class CleaningModule(object):
    def __init__(self, config_ini, logger):
        self.used_env = None
        self.cfg_path = config_ini
        self.logger = logger

    def __set_params(self, used_env):
        self.used_env = used_env
        return True

    def __clean_config_file(self):
        cfg = ConfigParser()
        cfg.read(self.cfg_path)
        cfg.set(SECTION_STATUS, self.used_env, FREE_STATE)
        with open(self.cfg_path, "w") as p:
            cfg.write(p)
            p.close()
        return True

    def clean(self, used_env):
        self.__set_params(used_env)
        return self.__clean_config_file()
