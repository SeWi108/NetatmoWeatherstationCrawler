import configparser
import datetime
import logging
import threading
import sys
from crawler import Crawler

""" Managing the initialization and the threading.

Class initializes the crawler (including logging, configurations) and starts the crawling tasks. Therefore threading 
with a timer is used.

The crawling task will be started in a fixed time-period, defined in the config.ini.
"""

print("Start initializing Netatmo crawling.")

# initialize logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# parse config-file
config = configparser.ConfigParser()
config.read('config.ini')

_netatmo_login = {
    'user': config['NETATMO_LOGIN']['USER'],
    'password': config['NETATMO_LOGIN']['PASSWORD'],
    'station_mac': config['NETATMO_LOGIN']['STATION_MAC']
}
_netatmo_client_setting = {
    'client_id': config['NETATMO_CLIENT']['CLIENT_ID'],
    'client_secret': config['NETATMO_CLIENT']['CLIENT_SECRET'],
    'max_failed_registrations': int(config['NETATMO_CLIENT']['MAX_FAILED_REGISTRATIONS']),
    'delay_registrations': int(config['NETATMO_CLIENT']['DELAY_REREGISTER']),
    'timeout': int(config['NETATMO_CLIENT']['TIMEOUT'])
}
_database_login = {
    'dialect': config['DATABASE']['DIALECT'],
    'host': config['DATABASE']['HOST'],
    'name': config['DATABASE']['NAME'],
    'user': config['DATABASE']['USER'],
    'password': config['DATABASE']['PASSWORD'],
}
_crawler_setting = {
    'interval': int(config['CRAWLER']['INTERVAL']),
    'echo': bool(config['CRAWLER']['ECHO']),
}


def sync_thread():
    if _crawler_setting['echo']:
        print("Crawl-task @ " + str(datetime.datetime.now())[:19])

    threading.Timer(_crawler_setting['interval'], sync_thread).start()
    crawler.crawl()


crawler = Crawler(_crawler_setting, _netatmo_login, _netatmo_client_setting, _database_login)

print("Initialized! Start crawling.")
sync_thread()
