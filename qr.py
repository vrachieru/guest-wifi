from pyqrcode import create
from io import BytesIO
from base64 import b64encode

class QrCode:

    def __init__(self, ssid, authentication_method, password, **kwargs):
        self._qr = create('WIFI:S:{ssid};T:{authentication_method};P:{password};;'.format(
            ssid = self._mecard_escape(ssid),
            authentication_method = self._authentication_method(authentication_method),
            password = self._mecard_escape(password)
        ))

    def _authentication_method(self, authentication_method):
        if authentication_method.lower() in ['wep']:
            return 'WEP'
        if authentication_method.lower() in ['wpa', 'wpa2', 'wpawpa2', 'psk', 'psk2', 'pskpsk2']:
            return 'WPA'
        return 'nopass'
    
    def _mecard_escape(self, value):
        value = value.replace('\\', '\\\\')
        value = value.replace(';', '\\;')
        value = value.replace(':', '\\:')
        value = value.replace(',', '\\,')
        return value

    @property
    def base64svg(self):
        stream = BytesIO()
        self._qr.svg(stream, scale=4)
        return b64encode(stream.getvalue()).decode('utf-8')
