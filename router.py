from abc import ABC, abstractmethod
from pexpect import pxssh, exceptions

_AUTHENTICATION_METHOD = {
    'open': 'Open System',
    'shared': 'Shared Key',
    'wep': 'WEP',
    'psk': 'WPA-Personal',
    'psk2': 'WPA2-Personal',
    'pskpsk2': 'WPA-Auto-Personal',
    'wpa': 'WPA-Enterprise',
    'wpa2': 'WPA2-Enterprise',
    'wpawpa2': 'WPA-Auto-Enterprise'
}

class Router(ABC):
    
    def __init__(self):
        self._connected = False

    @property
    def connected(self):
        return self._connected

    @property
    @abstractmethod
    def connection_details(self):
        return None

    @abstractmethod
    def reset_password(self):
        return None

    def generate_password(self):
        from random import choice
        from string import letters, digits, punctuation, whitespace

        return ''.join([choice(letters + digits + punctuation) for x in range(int(os.environ.get('PASSWORD_COMPLEXITY', 16)))])

class AsusWRT(Router):

    def __init__(self, host, port, username, password, ssh_key, wifi_interface):
        super().__init__()

        self._ssh = None
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._ssh_key = ssh_key
        self._wifi_interface = wifi_interface

    @property
    def connection_details(self):
        authentication_method = self.run_command('nvram get %s_auth_mode_x' % self._wifi_interface)
        return {
            'authentication_method': authentication_method,
            'authentication_method_name': _AUTHENTICATION_METHOD.get(authentication_method.lower(), authentication_method),
            'ssid': self.run_command('nvram get %s_ssid' % self._wifi_interface),
            'password': self.run_command('nvram get %s_wpa_psk' % self._wifi_interface)
        }

    def reset_password(self):
        self.run_command('nvram set %s_wpa_psk="%s"' % (self._wifi_interface, self.generate_password()))
        self.run_command('nvram commit')
        self.run_command('reboot')

    def run_command(self, command):
        try:
            if not self.connected:
                self.connect()
            self._ssh.sendline(command)
            self._ssh.prompt()
            return b'\n'.join(self._ssh.before.split(b'\r\n')[1:-1]).decode('utf-8')
        except Exception as ex:
            self.disconnect()
            raise ex

    def connect(self):
        self._ssh = pxssh.pxssh()
        if self._ssh_key:
            self._ssh.login(self._host, self._username, quiet=False, ssh_key=self._ssh_key, port=self._port)
        else:
            self._ssh.login(self._host, self._username, quiet=False, password=self._password, port=self._port)

        self._connected = True

    def disconnect(self):
        try:
            self._ssh.logout()
        except Exception:
            pass
        finally:
            self._ssh = None

        self._connected = False
