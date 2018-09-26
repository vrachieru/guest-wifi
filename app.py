from os import environ

from flask import Flask, render_template

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from router import AsusWRT
from qr import QrCode

app = Flask(__name__)

scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

router = AsusWRT(
    environ.get('ROUTER_IP', '192.168.1.1'), 
    int(environ.get('ROUTER_SSH_PORT', 22)),
    environ.get('ROUTER_USERNAME', 'admin'), 
    environ.get('ROUTER_PASSWORD', 'admin'),
    environ.get('ROUTER_SSH_KEY'),
    environ.get('ROUTER_WIFI_INTERFACE', 'wl0.1')
)

@app.route('/')
def home():
    connection_details = router.connection_details
    valid_until = scheduler.get_job('reset_password').next_run_time
    qr_code = QrCode(**connection_details)

    return render_template('index.html', **connection_details, valid_until=valid_until, qr=qr_code.base64svg)

@scheduler.scheduled_job(id='reset_password', trigger=CronTrigger.from_crontab(environ.get('PASSWORD_RESET_CRON', '0 12 * * MON')))
def reset_password():
    router.reset_password()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
