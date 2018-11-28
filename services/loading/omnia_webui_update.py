# from argparse import ArgumentParser
import os

from .abstract import LoadingModule, SEPARATE_CHAR
from ..lib.kali.kali import Kali
from ..lib.helpers import check_ip, check_path


class OmniaWebUiLoading(LoadingModule):
    def __init__(self, config_ini, logger):
        LoadingModule.__init__(self)
        self.ip = None
        self.port = None
        self.kali = None
        self.env = None
        self.logger = logger
        self.cfg = config_ini
        self.__load_kali()

    def __load_kali(self):
        self.env = self._find_1st_free(self.cfg)
        if self.env is None:
            # No free evironment available, returning False
            return False
        try:
            self.ip, self.port = self.env.split(SEPARATE_CHAR)
            self.port = int(self.port)
        except ValueError:
            raise ValueError("Unexpected value for OMNIA address: %s" % self.env)
        self.kali = Kali()
        self.kali.set_logger(self.logger)
        return True

    def _update(self):
        if self.ip is None:
            self.logger.debug("No free environment for this platform")
            return False
        self.kali.add_omnia_webui_addon('webui', ip=self.ip)
        if not (check_ip(self.ip) and
                check_path(self.build_path) and
                isinstance(self.port, int)):
            raise TypeError("Unexpected input parameters received:\nIP:PORT =  %s:%d\nPATH = %s\n" %
                            (self.ip, self.port, self.build_path)
                            )
        self.kali.do_addon_method('webui', 'macro_login')
        self.kali.info('Login successfully')
        self.kali.do_addon_method('webui', 'click_button', label='Tools')
        self.kali.do_addon_method('webui', 'click_button', label='Software Update')
        self.kali.info('Uploading files...')
        for filename in os.listdir(self.build_path):
            self.kali.do_addon_method('webui', 
                                      'upload_file', 
                                      file_path=os.path.join(self.build_path, filename),
                                      hidden=True)
        self.kali.do_addon_method('webui', 'click_button', label='Upload all')
        self.kali.info('Updating... Please wait for about 5 minutes')
        self.countdown(300)
        self.kali.do_addon_method('webui', 'click_button', label='Reboot now')
        self.kali.info('Update completed successfully')
        self.kali.info('Rebooting board...')
        self.countdown(60)
        self.kali.remove_addon("webui")
        return True

    def _check_loaded_version(self, new_version_string):
        self.kali.add_omnia_webui_addon('webui', ip=self.ip)
        self.kali.do_addon_method('webui', 'macro_login')
        self.kali.info('Login successfully')
        self.kali.do_addon_method("webui", "get_value", label="Core-FWR[Build]")
        self.kali.set_check("webui", new_version_string)
        return self.kali.get_result("webui", "equal")

    def _get_envirnoment_in_use(self):
        return self.env
