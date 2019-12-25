from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
import logging
import requests
import time
import urllib.parse
from models import Measurement

# API-URI (Netatmo)
# @see https://dev.netatmo.com

_BASE_URL = "https://api.netatmo.com/"
_TOKEN_URL = _BASE_URL + "oauth2/token"
_STATION_DATA_URL = _BASE_URL + "api/getstationsdata"


class NetatmoClient:
    """Handling the collection of the data from the Netatmo API.

    This class handles all data requests from the Netatmo API. All measurements will be exclusively collected from
    Netatmo and handed for further processing through this class.

    API documentation: @see https://dev.netatmo.com

    The access-data for the Netatmo API must be handed on initializing (see __init__ method below)
    """

    _failed_registration_counter = 0  # counter for failed registration attempts (oAuth)
    _lock_reinit_oAuth = False  # lock reinitialize oAuth-Session for a single task

    def __init__(self, netatmo_login, netatmo_client_settings):
        """Initialize the Netatmo Client and get the authTokens
        :param netatmo_login: Netatmo login-data
        :param netatmo_client_settings: Netatmo-Client settings
        """
        logging.info("Initialize Netatmo Client")

        self._netatmo_login = netatmo_login
        self._netatmo_client_settings = netatmo_client_settings

        self._netatmo_oauth = None
        self._init_oauth_session()

    def _init_oauth_session(self, reinit_task=False):
        logging.info("Init oAuth-Session @ NetatmoClient._init_oauth_session()")

        # check if initialization is not locked
        if self._lock_reinit_oAuth and not reinit_task:
            logging.warning("Initialization task can not be performed. - init locked")
        else:
            try:
                self._netatmo_oauth = OAuth2Session(
                    client=LegacyApplicationClient(client_id=self._netatmo_client_settings['client_id']))
                self._netatmo_oauth.fetch_token(token_url=_TOKEN_URL, username=self._netatmo_login['user'],
                                                password=self._netatmo_login['password'],
                                                client_id=self._netatmo_client_settings['client_id'],
                                                client_secret=self._netatmo_client_settings['client_secret'])
            except Exception as e:
                logging.warning("Error on init Netatmo oAuth-Session")
                self._failed_registration_counter += 1

                if self._failed_registration_counter <= self._netatmo_client_settings['max_failed_registrations']:
                    logging.debug("Lock reinitialize Netatmo oauth-Session.")
                    self._lock_reinit_oAuth = True  # only one task allowed to reinit oAuth
                    time.sleep(self._netatmo_client_settings['delay_registrations'])
                    self._init_oauth_session(True)
                else:
                    logging.critical("(Re-)Initialize Netatmo oAuth-Session failed. ("
                                     + str(self._failed_registration_counter) + " retries)")
                    exit()

    def _reinit_oauth_session(self):
        logging.info("Reinit oAuth-Session @ NetatmoClient._reinit_oauth_session()")

        if self._netatmo_oauth is None:
            self._init_oauth_session(reinit_task=True)
        else:
            try:
                self._netatmo_oauth.refresh_token(token_url=_TOKEN_URL,
                                                  refresh_token=self._netatmo_oauth.token["refresh_token"],
                                                  username=self._netatmo_login['user'],
                                                  password=self._netatmo_login['password'],
                                                  client_id=self._netatmo_client_settings['client_id'],
                                                  client_secret=self._netatmo_client_settings['client_secret'])
            except Exception as e:
                logging.warning("Error on reinit Netatmo oAuth-Session")
                self._failed_registration_counter += 1

                if self._failed_registration_counter <= self._netatmo_client_settings['max_failed_registrations']:
                    logging.debug("Lock reinitialize Netatmo oauth-Session.")
                    self._lock_reinit_oAuth = True  # only one task allowed to reinit oAuth
                    time.sleep(self._netatmo_client_settings['delay_registrations'])
                    self._init_oauth_session(True)
                else:
                    logging.critical("(Re-)Initialize Netatmo oAuth-Session failed. ("
                                     + str(self._failed_registration_counter) + " retries)")
                    exit()

    def _handle_statuscode(self, status_code):
        if status_code == 401:
            # HTTP 401
            logging.info("Handling HTTP 401 status-code with reinitializing the Netatmo-oAuth-Session.")
            self._init_oauth_session()
        elif status_code == 403:
            # HTTP 403
            logging.info("Handling HTTP 403 status-code with reinitializing the Netatmo-oAuth-Session.")
            self._reinit_oauth_session()
        else:
            # unexpected
            logging.error("Handling unexpected HTTP status-code with reinitializing the Netatmo-oAuth-Session.")
            self._reinit_oauth_session()

    def _handle_timeout(self):
        logging.info("Handling timeout with reinitializing the Netatmo-oAuth-Session.")
        self._reinit_oauth_session()

    def _handle_connection_error(self):
        logging.info("Handling ConnectionError with reinitializing the Netatmo-oAuth-Session.")
        self._reinit_oauth_session()

    def get_measurement(self):
        logging.info("Get the measurements of the handed station. (MAC: " + self._netatmo_login['station_mac'] + ")")

        if self._lock_reinit_oAuth:
            logging.info("Execution locked (During reinitializing the oAuth Session).")
            return []  # exit

        try:
            # get measurements form the api
            measurement_response = self._netatmo_oauth.get(
                _STATION_DATA_URL + "?device_id=" + urllib.parse.quote(
                    self._netatmo_login['station_mac']) + "&get_favorites=false",
                timeout=self._netatmo_client_settings['timeout'])

            if measurement_response.status_code != 200:
                logging.warning('HTTP status code @ get_measurement(' + self._netatmo_login['station_mac'] + '). Code: '
                                + str(measurement_response.status_code))
                self._handle_statuscode(measurement_response.status_code)
                return []  # exit
            else:
                # extract measurement
                measurement_response_json = []
                try:
                    measurement_response_json = measurement_response.json()
                except ValueError:
                    logging.error("JSON Decode Error @ get_measurement", measurement_response)
                    # default to measurement_response_json = []
                finally:
                    if measurement_response_json:
                        return Measurement(
                            time_utc=measurement_response_json["body"]["devices"][0]["dashboard_data"]["time_utc"],
                            station_mac=self._netatmo_login["station_mac"],
                            co2=measurement_response_json["body"]["devices"][0]["dashboard_data"]["CO2"],
                            noise=measurement_response_json["body"]["devices"][0]["dashboard_data"]["Noise"],
                            temperature=measurement_response_json["body"]["devices"][0]["dashboard_data"]["Temperature"]
                        )
                    else:
                        return None

        except requests.exceptions.ConnectionError:  #
            logging.warning("Connection Error @ get_measurement()")
            self._handle_connection_error()
            return []  # exit
        except requests.exceptions.Timeout:
            logging.warning("Timeout @ get_measurement()")
            self._handle_timeout()
            return []  # exit
