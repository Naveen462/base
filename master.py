import getopt
import sys
import os
from services.defines import *
from services.lib.test_logger import MyLogger
# Loading modules
from services.loading.omnia_http_api_update import HttpApiUpdate
# Cleaning modules
from services.cleaning.omnia import OmniaCleaningModule


class CiCtMaster:
    def __init__(self):
        # Arguments initializing
        self.mode = None
        self.version = None
        self.build_path = None
        self.platform = None
        self.used_env = None
        # Private object
        self._logger = None
        # Main object
        self.__load_logger()
        self.__get_param()
        self.__run()

    @staticmethod
    def help():
        print("Required parameters")
        print("\t-h --help: show this help")
        print("\t-b --build: the build path")
        print("\t-v --version: the new version")
        print("\t-p --platform: the platform under testing")
        print("\t-m --mode: the required mode")

    def __load_logger(self):
        self._logger = MyLogger()
        # Remapping logging methods
        self.debug = self._logger.debug
        self.info = self._logger.info
        self.error = self._logger.error

    def __get_param(self):
        self.debug("Gathering parameters")
        try:
            opts = getopt.getopt(sys.argv[1:],
                                 "hb:m:v:p:",
                                 [
                                     "help",
                                     "build=",
                                     "mode=",
                                     "version=",
                                     "platform="
                                  ]
                                 )[0]
        except getopt.GetoptError:
            self.error("Error parsing received arguments")
            self.help()
            sys.exit(1)
        error = False
        for opt, arg in opts:
            error_line = None
            if opt in ("-h", "--help"):
                self.help()
                sys.exit(0)
            elif opt in ("-b", "--build"):
                if not os.path.isdir(arg):
                    error_line = "Build path passed is not a directory: %s" % arg
                    error = True
                self.build_path = os.path.abspath(arg)
            elif opt in ("-m", "--mode"):
                if arg not in MODE_LIST:
                    error_line = "Mode path passed is not a directory: %s" % arg
                    error = True
                self.mode = arg
            elif opt in ("-v", "--version"):
                self.version = arg
            elif opt in ("-p", "--platform"):
                if arg not in PLATFORM_LIST:
                    error_line = "Platrform passed is not allowed: %s" % arg
                    error = True
                self.platform = arg
            else:
                error_line = "Unexpected option/value (%s/%s)" % (opt, arg)
                error = True
            if error_line is not None:
                self.error(error_line)
        if error:
            self.help()
            sys.exit(1)

    def loading(self):
        # Sanity check
        if None in (self.version, self.build_path, self.platform):
            self.help()
            self._logger.error("One of these parameters are not been set: version, platform, build_path")
            sys.exit(1)
        if self.platform == OMNIA_PLATFORM:
            loading_module = HttpApiUpdate
            cfg_path = OMNIA_CONFIG_PATH
        else:
            self._logger.error("Unexpected platform type: %s" % self.platform)
            sys.exit(1)
        completed = False
        loading_object = loading_module(cfg_path, self._logger)
        if loading_object.update(self.build_path):
            self._logger.info("Update done successfully!")
            if loading_object.check(self.version):
                self._logger.info("New version correctly checked!")
                completed = True
            else:
                self._logger.error("Version check failed!")
        else:
            self._logger.error("Update failed!")
        self.used_env = loading_object.get_environment()
        return completed

    def cleaning(self):
        if self.platform == OMNIA_PLATFORM:
            cleaning_module = OmniaCleaningModule
            cfg_path = OMNIA_CONFIG_PATH
        else:
            self._logger.error("Unexpected platform type: %s" % self.platform)
            sys.exit(2)
        cleaning_object = cleaning_module(cfg_path, self._logger)
        return cleaning_object.clean(self.used_env)

    def __run(self):
        # Sanity check
        if self.mode is None:
            self.help()
            self._logger.error("Mode parameter not set, unable to move on!")
            sys.exit(1)
        # Loading phase
        if self.mode in (MASTER_MODE_FULL, ):
            if self.loading():
                self.info("Loading phase completed!")
            else:
                self.error("Loading phase failed!")
                sys.exit(90)
        else:
            self._logger.error("Unexpected value for mode parameter:  %s" % self.mode)
            sys.exit(1)
        # Cleaning phase
        if self.mode in (MASTER_MODE_FULL, ):
            if self.used_env is not None:
                if self.cleaning():
                    self.info("Cleaning phase completed!")
                else:
                    self.error("Cleaning phase failed!")
                    sys.exit(99)
        else:
            self._logger.error("Unexpected value for mode parameter:  %s" % self.mode)
            sys.exit(1)
        sys.exit(0)


if __name__ == '__main__':
    master = CiCtMaster()
