import urllib.request as urllib


class powerCycle(object):
    def __init__(self):
        self.POWER_SWITCH_IP      = "192.168.68.20"
        self.POWER_SWITCH_USER    = "admin"
        self.POWER_SWITCH_PASS    = "gilbarco"
        self.POWER_SWITCH_CMD_ON  = "1"
        self.POWER_SWITCH_CMD_OFF = "0"
        self.POWER_SWITCH_LBL_ON  = "ON"
        self.POWER_SWITCH_LBL_OFF = "OFF"

    def power(self, val, port):
        if val == self.POWER_SWITCH_LBL_ON: val = self.POWER_SWITCH_CMD_ON
        elif val == self.POWER_SWITCH_LBL_OFF: val = self.POWER_SWITCH_CMD_OFF
        url = 'http://'+self.POWER_SWITCH_IP+'/Set.cmd?user='+self.POWER_SWITCH_USER+'+pass='+self.POWER_SWITCH_PASS+'+CMD=SetPower+'+port+'='+val
        f = urllib.urlopen(url)
        if f.getcode() == 200:
            return True
        return False

    def powerOn(self, port):
        return self.power(self.POWER_SWITCH_LBL_ON, self.portTranslate(port))

    def powerOff(self, port):
        return self.power(self.POWER_SWITCH_LBL_OFF, self.portTranslate(port))

    def portTranslate(self, port):
        if type(port) is not int:
            raise TypeError('Bad value passed for port number, int required')
        if port == 1:
            return 'P60'
        elif port == 2:
            return 'P61'
        elif port == 3:
            return 'P62'
        elif port == 4:
            return 'P63'
        raise ValueError('Wrong value passed for port number, value expected: [1,2,3,4]')
