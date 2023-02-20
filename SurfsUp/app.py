#------------------------------------------------
#Database Setup - Dependencies

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import pandas as pd 

#-------------------------------------------------
# Database Setup

# create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#------------------------------------------------
# Flask Setup

# 1. import Flask
from flask import Flask, jsonify

# 2. Create an app
app = Flask(__name__)

#------------------------------------------------
# Flask Routes

# start at the home page and list all the available routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii climate site!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/<start><br/>"
        f"/api/v1.0/temp/<start>/<end><br/>"
    )

#Convert the query results from precipitation analysis for the last 12 months of data
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session
    session = Session(engine)

    # Return dates and precipitation
    # Query dates and precipitation for most recent 12-month period
    # Calculate start date (2017-08-23)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #Calculate end date (2016-8-24)
    last_12_months = dt.date(2017, 8, 23) - dt.timedelta(days=364)

    # Perform a query to retrieve the data and precipitation scores between 2017-08-23 & 2016-08-24
    year_precipitation = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date >= '2016-08-23', Measurement.prcp != None).\
            order_by(Measurement.date).all()

    session.close()

    # Create a dictionary and append to a list called (precipitation)
    precipitation = []
    for date, prcp in year_precipitation:
        row = {}
        row["date"] = date
        row["prcp"] = prcp
        precipitation.append(row)

    return jsonify(precipitation)


# Retrun a JSON list of stations

@app.route("/api/v1.0/stations")
def stations():
    # Create our session
    session = Session(engine)

    """Return list of stations"""
    # Query all station
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # return the JSON representation of the dictionary
    return jsonify(all_stations)

# Query the dates and temperatures of the most active station for the previous year

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
    session = Session(engine)

    # Return list of temperatures from most active station for past year
    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    active_stations= session.query(Measurement.station,func.count(Measurement.station)).\
                               group_by(Measurement.station).\
                               order_by(func.count(Measurement.station).desc()).all()
                               

    # Using the most active station id query the last 12 months of temperature observations
    year_temperature= session.query(Measurement.tobs).\
                filter(Measurement.date >= '2016-08-23', 
                Measurement.station == 'USC00519281').\
                order_by(Measurement.tobs).all()

    session.close()

    # Convert list of tuples into normal list
    tobs = list(np.ravel(year_temperature))

    # return the JSON representation of the dictionary
    return jsonify(tobs)

# Return a JSON list of the minimum, average, and maximum temperatures for specific 
# start date and/or start-end range

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    # Create our session
    session = Session(engine)

    # Return list of temperature statistics (min/max/avg) depending on a specified start/end date range
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)] 
    if not end:
        results = session.query(*sel).\
            filter(Measurement.date <= start).all()
        
        temp = list(np.ravel(results))
        return jsonify(temp)
    else:
        results = session.query(*sel).\
           filter(Measurement.date >= start).\
           filter(Measurement.date <= end).all()
        session.close()
        temp = list(np.ravel(results))
        return jsonify(temp=temp)

    
    
if __name__ == "__main__":
    app.run(debug=True)
