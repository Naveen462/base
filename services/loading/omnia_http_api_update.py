from .abstract import LoadingModule, SEPARATE_CHAR
from ..lib.kali.kali import Kali
from ..lib.helpers import check_ip, check_path
import configparser
import sys
import subprocess
import os
import time


class HttpApiUpdate(LoadingModule):
    def __init__(self, config_ini, logger):
        LoadingModule.__init__(self, config_ini, logger)
        self.ip = None
        self.port = None
        self.kali = None
        self.ppn = None
        self.env = None
        self.__load_kali()
        self.__load_cfg()

    def __load_cfg(self):
        cfg = configparser.ConfigParser()
        cfg.read(self.cfg)
        try:
            self.ppn = cfg['INFO']['ppn']
        except KeyError:
            return False
        return True

    def __load_kali(self):
        self.env = self._find_1st_free(self.cfg)
        if self.env in (None, False):
            # No free evironment available or error parsing the config file, returning False
            return False
        try:
            self.ip, self.port = self.env.split(SEPARATE_CHAR)
            self.port = int(self.port)
        except ValueError:
            raise ValueError("Unexpected value for OMNIA address: %s" % self.env)
        self.kali = Kali()
        self.kali.set_logger(self.logger)
        return True

    def __login(self):
        subprocess.call("curl -H 'Content-Type: application/json' -X POST -d '{\"username\": \"admin\","
                        " \"password\": \"" + str(self.ppn[-6:]) + "\"}' http://" + str(self.ip) +
                        ":" + str(self.port) + "/index --insecure -o /dev/null", shell=True)

    def _update(self):
        if self.ip is None:
            self.logger.error("No free environment for this platform")
            return False
        if not (check_ip(self.ip) and
                check_path(self.build_path) and
                self.ppn is not None and
                len(self.ppn) >= 6):
            raise TypeError("Unexpected input parameters received:\nIP:PORT =  %s:%d\nPATH = %s\n" %
                            (self.ip, self.port, self.build_path)
                            )
        self.__login()
        self.logger.info("Updating Omnia platform... This may take a while")
        for filename in os.listdir(self.build_path):
            abs_path = os.path.join(self.build_path, filename)
            proc = subprocess.Popen("curl -F \"file=@" + str(abs_path) + "\" http://" + str(self.ip) + ":" + str(self.port) +
                                    "/updateSoftware --insecure -i", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = str(proc.communicate()[0])
            if '"success":true' not in out:
                self.logger.error("Update failed")
                return False
        self.logger.info("Update complete! Rebooting board...")
        subprocess.call("curl http://" + str(self.ip) + ":" + str(self.port) + "/reboot --insecure", shell=True)
        time.sleep(80)
        return True

    def _check_loaded_version(self, new_version):
        if self.ip is None:
            self.logger.debug("No free environment for this platform")
            return False
        if not (check_ip(self.ip) and
                self.ppn is not None and
                len(self.ppn) >= 6):
            raise TypeError("Unexpected input parameters received:\nIP:PORT =  %s:%d\nPATH = %s\n" %
                            (self.ip, self.port, self.build_path)
                            )
        self.__login()
        proc = subprocess.Popen("curl http://" + str(self.ip) + ":" + str(self.port) + "/getInfo --insecure",
                                shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.communicate()[0].decode('utf-8')
        start_index = out.find('Core-FWR[Build]:') + len('Core-FWR[Build]:')
        cur_version = out[start_index:out.find(",", start_index + 1)]
        return cur_version == new_version
