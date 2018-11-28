import paramiko
import os


class Detectus(object):
    def __init__(self):
        super(Detectus, self).__init__()
        self.ssh = None
        self.compare_archive = {}

    def __del__(self):
        if self.ssh:
            self.ssh.close()

    def ssh_open(self, ip, platform):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        usr = None
        pwd = None
        if platform.upper() == "VGD":
            usr = "root"
        else:
            # TODO: handle other platform (M5)
            pass
        if None not in (ip, usr):
            try:
                self.ssh.connect(ip, username=usr, password=pwd, look_for_keys=False)
            except paramiko.SSHException:
                self.ssh = None

    def ssh_command(self, command):
        if self.ssh:
            try:
                stdin_stdout_stderr = self.ssh.exec_command(command, mode=bytes)
                # Check if some errors have been triggered
                if len(stdin_stdout_stderr[2].readlines()):
                    return False
                return stdin_stdout_stderr
            except paramiko.SSHException:
                return None

    def save_compare(self, label, buf):
        self.compare_archive[label] = buf
        return True

    def save_compare_by_command(self, label, command):
        stdin_stdout_stderr = self.ssh_command(command)
        # Save standard output as compare check
        if stdin_stdout_stderr:
            self.save_compare(label, self.get_stdout(stdin_stdout_stderr))
        return False

    def save_compare_by_file(self, label, file_path):
        if self.ssh:
            if os.path.isfile(file_path):
                with open(file_path, "rb") as p:
                    f = self.save_compare(label, p.readall())
                p.close()
                return f
        return False

    def compare(self, label, compare_buf):
        try:
            return self.compare_archive[label] == compare_buf
        except KeyError:
            return False

    def compare_by_file(self, label, file_path):
        if os.path.isfile(file_path):
            with open(file_path, "rb") as p:
                f = self.compare(label, p.readall())
            p.close()
            return f
        return False

    def compare_by_command(self, label, command):
        stdin_std_out_stderr = self.ssh_command(command)
        if stdin_std_out_stderr:
            return self.compare(label, self.get_stdout(stdin_std_out_stderr))

    @staticmethod
    def get_stdout(std_tuple):
        return b"".join(x for x in std_tuple[1])

    # def save_compare_by_webcam(self):
        # TODO
