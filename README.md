# Netatmo Weather-Station Crawler


A simple crawler to fetch the measurements of **one** connected Netatmo Weather Station and store the values for

- time_utc
- temperature
- CO2
- noise

to a SQL-Database.

This crawler uses the official Netatmo API (see https://dev.netatmo.com) and for storing the Data to the Database the Framework `SQLALCHEMY' is used (see https://www.sqlalchemy.org)

##
**THIS CODE SHOULD ONLY BE USED FOR PERSONAL USE AND TESTING PURPOSE**\
This code stores plain access data of a user in the `config.ini` file!
For Security reasons you should **NEVER** store some plain userdata.
\
If you want to use the crawler for live- or professional purposes rewrite the OAuth2 Authentication! (see https://dev.netatmo.com/apidocumentation/oauth)



## Setup
Add your personal account-data at the `config.ini` file and start the crawler by running
```
pip main.py 
```
You may have first creat your personal app credentials at the Netatmo Website at https://dev.netatmo.com/apps/createanapp#form

## Notes
Per default the data will be fetched every 10minutes as it is the maximum resolution for the Netatmo API.
\
The data will be stored in a SQL-Database in the format
```
time_utc = Column(BigInteger, primary_key=True)
station_mac = Column(String(17), primary_key=True)
co2 = Column(Integer)
noise = Column(Integer)
temperature = Column(Integer)
```
