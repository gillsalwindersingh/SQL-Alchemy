import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from datetime import datetime as dt
from datetime import timedelta

engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Flask routes

@app.route("/")
def welcome():
    #All available api routes
    return (
        f"Home Page  Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Enter Start Date as YYYY-MM-DD. Provides TMIN, TAVG, and TMAX for each date.<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"Enter Start Date and End Date as YYYY-MM-DD. separated by a ,. Provides TMIN, TAVG, and TMAX for the interval.<br/>"
        f"/api/v1.0/start_end_date/<start_date>,<end_date"
    )


# Precipitation Measurements (back one year from last measurement date)

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Calculate the date 1 year ago from the last data point in the database - needed in more than one area
    query_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    query_date_end = dt.strptime(query_date, "('%Y-%m-%d',)") 
    year_calc = timedelta(days=365)
    query_date_start = query_date_end - year_calc

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date>=query_date_start).\
    order_by(Measurement.date).all()

    all_precipit = {}
    for date, prcp in results:
        all_precipit[date]=prcp

    return jsonify(all_precipit)


# List of Stations

@app.route("/api/v1.0/stations")
def stations():

    return jsonify(session.query(Station.station, Station.name).all()) 


# Temperature observations of the previous year

@app.route("/api/v1.0/tobs")
def temperatures():
 
    # Calculate the date 1 year ago from the last data point in the database - needed in more than one area
    query_date = str(session.query(Measurement.date).order_by(Measurement.date.desc()).first())
    query_date_end = dt.strptime(query_date, "('%Y-%m-%d',)") 
    year_calc = timedelta(days=365)
    query_date_start = query_date_end - year_calc

    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date>=query_date_start).all()

    all_temp = {}
    for date, temp in results:
        all_temp[date]=temp

    return jsonify(all_temp)

# Temperatures Min, Max, and Average from a Start Date
@app.route("/api/v1.0/start_date/<start_date>")
def temperature_start(start_date):

    query_date = dt.strptime(str(start_date), "%Y-%m-%d")
    results_temp = session.query(Measurement.date, func.min(Measurement.tobs),\
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=query_date).\
        group_by(Measurement.date).all() 

    all_temp = {}
    for date, mint, avt, maxt in results_temp:
        all_temp[date]=(mint, avt, maxt)   
    
    return jsonify(all_temp)


#Temperatures Min, Max, and Average for an interval
@app.route("/api/v1.0/start_end_date/<start_date>,<end_date>")

def temperature_start_end(start_date, end_date):
    
    start_d = dt.strptime(str(start_date), "%Y-%m-%d")
    end_d = dt.strptime(str(end_date), "%Y-%m-%d")

    return_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_d).filter(Measurement.date <= end_d).all()

    return jsonify(return_range)

if __name__ == "__main__":
    app.run(debug=True)