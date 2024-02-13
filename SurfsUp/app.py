# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################

# create engine to sqlite file hawaii

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station



# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#list out all of the flask routes

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"

    )

# precipitation route that:
# Returns json with the date as the key and the value as the precipitation 
# Only returns the jsonified precipitation data for the last year in the database 

@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    one_year= dt.date(2017, 8, 23)-dt.timedelta(days=365)
    previous_last_date = dt.date(one_year.year, one_year.month, one_year.day)

    result= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_last_date).order_by(Measurement.date.desc()).all()


    precipitation_dict = dict(result)

    print(f"Results for Precipitation - {precipitation_dict}")
    print("Out of Precipitation section.")
    return jsonify(precipitation_dict) 


# A stations route that:
# Returns jsonified data of all of the stations in the database

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    result = session.query(*sel).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in result:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)

# A tobs route that:
# Returns jsonified data for the most active station (USC00519281) 
# Only returns the jsonified data for the last year of data 

@app.route("/api/v1.0/tobs")
def tobs():
     session = Session(engine)


     result = session.query( Measurement.date, Measurement.tobs).filter(Measurement.station=='USC00519281')\
     .filter(Measurement.date>='2016-08-23').all()


     tob_obs = []
     for date, tobs in result:
         tobs_dict = {}
         tobs_dict["Date"] = date
         tobs_dict["Tobs"] = tobs
         tob_obs.append(tobs_dict)

     return jsonify(tob_obs)


# A start route that:
# Accepts the start date as a parameter from the URL 
# Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset 


@app.route("/api/v1.0/<start>")

def get_temps_start(start):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in result:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps_dict['Average Temperature'] = avg_temp
        
        temps.append(temps_dict)

    return jsonify(temps)

# A start/end route that:
# Accepts the start and end dates as parameters from the URL 
# Returns the min, max, and average temperatures calculated from the given start date to the given end date 

@app.route("/api/v1.0/<start>/<end>")
def get_temps_start_end(start, end):
    session = Session(engine)
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in result:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps_dict['Average Temperature'] = avg_temp
       
        temps.append(temps_dict)

    return jsonify(temps)


if __name__ == '__main__':
    app.run(debug=True)