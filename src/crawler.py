import logging
from databaseConnector import DatabaseConnector
from netatmoClient import NetatmoClient


class Crawler:
    """Class managing the fetch of the data from Netatmo and the push to the Database.

    Class fetches the measurement for d
    <ul>
       <li>time_utc</li>
       <li>co2</li>
       <li>noise</li>
       <li>temperature</li>
    </ul>
    from the currently connected station and stores it to the connected database.
    """

    def __init__(self, crawler_settings, netatmo_login, netatmo_client_setting, database_login):
        """
        Initialize the Crawler class.
        Creating instances for the netatmo-client and the database-connection
        :param crawler_settings: Crawler settings
        :param netatmo_login: Netatmo login-data
        :param netatmo_client_setting: Netatmo-Client settings
        :param database_login: Database login-data
        """
        self._crawler_setting = crawler_settings
        self._netatmo_login = netatmo_login

        try:
            self._netatmo_client = NetatmoClient(netatmo_login, netatmo_client_setting)
            self._database_connector = DatabaseConnector(database_login)
        except Exception as e:
            logging.critical("Error on initialling Crawler.")
            print("Exit on a critical Error on initializing Crawler.")
            raise e

    def crawl(self):
        """
        Crawl the current measurement and store to the database.
        """
        for station_mac in self._netatmo_login["station_macs"]:
            measurement = self._netatmo_client.get_measurement(station_mac)

            if measurement is not None:
                self._database_connector.push_measurement(measurement=measurement)
