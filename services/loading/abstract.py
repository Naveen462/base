import os
import configparser
import time


ADDRESS_SECTION = "ADDRESS"
STATUS_SECTION = "STATUS"
FREE_VALUE = "free"
BUSY_VALUE = "busy"
SEPARATE_CHAR = ","


class LoadingModule(object):
    def __init__(self, config_ini, logger):
        self.build_path = None
        self.used_env = None
        self.logger = logger
        self.cfg = config_ini

    def __set_params(self, build_path):
        if not os.path.isdir(build_path):
            self.logger.error("Build path not found: %s" % build_path)
            return False
        self.build_path = build_path
        return True

    def _update(self):
        raise NotImplementedError("The extended class doesn't override the update method")

    def _check_loaded_version(self, new_version):
        raise NotImplementedError("The extended class doesn't override the check_loaded_version method")

    def _get_environment_in_use(self):
        return self.used_env

    '''
    def __check_and_save_params(self, expected, **kwargs):
        if not isinstance(expected, dict):
            raise TypeError("Expected parameters are not placed in a dictionary")
        for key in expected.keys():
            if key not in kwargs or not isinstance(kwargs[key], expected[key]):
                raise TypeError("Missing parameters %s" % key)
        for key in expected.keys():
            setattr(self, key, kwargs[key])
    '''

    @staticmethod
    def countdown(secs):
        """
        Display a countdown on the console

        Args:
            secs(int): countdown seconds
        """
        while secs > 0:
            print(str(secs) + ' seconds remaining ', end="\r", flush=True)
            secs -= 1
            time.sleep(1)

    def _find_1st_free(self, config_path):
        if not os.path.isfile(config_path):
            self.logger.error('Unable to load config file: %s' % config_path)
            return False
        cfg = configparser.ConfigParser()
        cfg.read(config_path)
        try:
            envs = cfg.options(ADDRESS_SECTION)
        except configparser.NoSectionError:
            self.logger.error("Unable to find section %s into config file %s" %
                              (ADDRESS_SECTION, config_path)
                             )
            return False
        free_env = None
        free_env_values = None
        for env in envs:
            try:
                if cfg.get(STATUS_SECTION, env) == FREE_VALUE:
                    free_env = env
                    free_env_values = cfg.get(ADDRESS_SECTION, env)
                    break
            except (configparser.NoOptionError, configparser.NoSectionError):
                self.logger.error("Status section is not present or option %s is not set" % env)
        # Returning the first free environment (or None if no env are free)
        # Reserving the environment
        if free_env is None:
            return None
        cfg.set(STATUS_SECTION, free_env, BUSY_VALUE)
        with open(config_path, "w") as fp:
            cfg.write(fp)
        fp.close()
        self.used_env = free_env
        return free_env_values

    def update(self, build_path):
        if self.__set_params(build_path):
            return self._update()
        return False

    def check(self, new_version):
        return self._check_loaded_version(new_version)
    
    def get_environment(self):
        return self._get_environment_in_use()




