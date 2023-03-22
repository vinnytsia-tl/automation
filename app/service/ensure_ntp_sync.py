import logging
import subprocess
from time import sleep

import jc

logger = logging.getLogger(__name__)


def ensure_ntp_sync():
    while True:
        timedatectl = subprocess.run(['timedatectl'], stdout=subprocess.PIPE, check=True)
        timedatectl_output = jc.parse('timedatectl', timedatectl.stdout.decode())
        logger.debug('timedatectl output: %s', timedatectl_output)
        if timedatectl_output['system_clock_synchronized'] and timedatectl_output['ntp_service'] == 'active':
            logger.info('NTP time synchronized, continue.')
            break
        logger.warning('NTP time not synchronized, waiting...')
        sleep(1)
