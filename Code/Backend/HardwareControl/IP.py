from subprocess import check_output
import time

class IP:
    def __init__(self):
        self.ip = self.return_ip()

    def return_ip(self):
        ips = str(check_output(['hostname', '--all-ip-addresses']))
        self.ip = ips.strip("b'").split(" ")
        return self.ip
