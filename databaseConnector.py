import logging
from models import Measurement, Base
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker


class DatabaseConnector:
    """Handling all database transactions.

    This class handles all interactions with the database. The insert and get statements for measurements will be
    handled exclusively with this class.
    For SQL-Connection the Framework `SQLALCHEMY' is used (see https://www.sqlalchemy.org).

    The access-data for the database must be handed on initializing (see __init__ method below)
    """

    def __init__(self, database_login):
        """Initialize the DatabaseConnector.
        :param database_login: Database login-data
        """
        logging.info("Setup Database-Engine.")

        self._engine = create_engine(database_login['dialect'] + '://' + database_login['user'] + ':'
                                     + database_login['password'] + '@' + database_login['host'] + '/'
                                     + database_login['name'])

        Base.metadata.create_all(self._engine)

        self._session = sessionmaker(bind=self._engine)

    def push_measurement(self, measurement):
        """
        Pushes the measurement-data to the database if this measurement is not already stored.
        (Combined PrimaryKey with station_mac and time_utc)
        :param measurement: the measurement-data
        """
        logging.info("Save measurements from " + str(measurement.time_utc) + " of the station " + measurement.station_mac + " to the database.")

        last_sync = self._get_last_sync_station(measurement.station_mac)

        if last_sync != measurement.time_utc:
            session = self._session()
            try:
                session.add(measurement)
                # session.add_all(measurement)
                session.commit()
            except Exception:
                print(Exception)
                logging.warning("ROLLBACK: storing measurement cause an exception raised.")
                session.rollback()
            finally:
                session.close()

    def _get_last_sync_station(self, station_mac):
        """
        Returns the UTC-Time of the last stored data of a specific station
        :param station_mac: the mac-address of the station for which the data should be returned
        :return: the UTC-Time of the last stored sync-dat
        """
        logging.info("Get last sync-time for station '" + station_mac + "'.")

        session = self._session()
        last_sync = None
        try:
            last_sync = session.query(func.max(Measurement.time_utc)).filter_by(station_mac=station_mac).scalar()
        except:
            logging.warning("An exception raised during executing SQL-query.")
            # default to last_sync = None
        finally:
            session.close()

        logging.info("Last-Sync for station '" + station_mac + "' :" + str(last_sync))
        return last_sync
