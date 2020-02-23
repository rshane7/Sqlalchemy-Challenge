# Python script uses flask and SQL alchemy to create API requests for weather data from Hawaii.

# Import dependencies.
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#---------------------------------------------------------------------------------------------------------------------- 
# Rubric - API SQLite Connection & Landing Page 
#          The Flask Application does all of the following: 
#              ✓ Correctly generates the engine to the correct sqlite file 
#              ✓ Uses ​automap_base()​ and reflects the database schema 
#              ✓ Correctly saves references to the tables in the sqlite file (measurement and station) 
#              ✓ Correctly creates and binds the session between the python app and database 
#----------------------------------------------------------------------------------------------------------------------

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)
# Save references to tables
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/mostactivetobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start_date/end_date/<start_date>/<end_date>"
    )

#----------------------------------------------------------------------------------------------------------------------
# Rubric - API Static Routes 
#    The static routes do all of the following: 
#    Precipitation route 
#        ✓ Returns the jsonified precipitation data for the last year in the database.
#        ✓ Returns json with the date as the key and the value as the precipitation Stations route. 
#        ✓ Returns jsonified data of all of the stations in the database Tobs route. 
#        ✓ Returns jsonified data for the most active station (USC00519281) for the last year of data. 
#----------------------------------------------------------------------------------------------------------------------

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return JSON where (Key: date / Value: precipitation)"""

    print("Precipitation API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the most recent date in dataset.
    # Convert to datetime object for calculation below.
    max_date = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).limit(1).all()
    max_date = max_date[0][0]
    max_date = dt.datetime.strptime(max_date, "%Y-%m-%d")

    # Calculate the date 1 year ago from the last data point in the database
    year_ago = max_date - dt.timedelta(days=366)

    # Perform a query to retrieve the last 12 months of precipitation data.
    precipitations = session.query(func.strftime("%Y-%m-%d", Measurement.date), Measurement.prcp).\
            filter(func.strftime("%Y-%m-%d", Measurement.date) >= year_ago).all()

    # Iterate through precipitations to append all key/values to precipitation dictionary.
    # Append precipitation dictionary to list, then return jsonify. 
    all_precipitations = []
    for date, prcp in precipitations:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitations.append(precipitation_dict)

    return jsonify(all_precipitations)

@app.route("/api/v1.0/stations")
def stations():
    """Return JSON API for all stations in dataset."""

    print("Stations API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query all stations in the dataset.
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Iterate through stations to append all key/values to station dictionary.
    # Append station dictionary to list, then return jsonify. 
    all_stations = []
    for id, station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict["id"] = id
        station_dict["station"] = station
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)

    return jsonify(all_stations)
    
# most active station  last year of data
@app.route("/api/v1.0/mostactivetobs")
def last_year_tobs_most_active():    

    print("Most Active Station API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # last date in the dataset and year from last date calculations
    last_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()[0]
    last_year = str(dt.datetime.strptime(last_date,"%Y-%m-%d")-dt.timedelta(days=365))
   
    last_year_tobs_most_active = session.query(Measurement.station,Measurement.date,Measurement.tobs).\
 	    filter(Measurement.date >=last_year, Measurement.date <=last_date, Measurement.station == 'USC00519281').\
 		order_by(Measurement.date).all()

    # Iterate through temperatures to append all key/values to temperature dictionary.
    # Append temperature dictionary to list, then return jsonify.
    all_mostactivetobs = []
    for station, date, tobs in last_year_tobs_most_active:
        last_year_tobs_most_active_dict = {}
        last_year_tobs_most_active_dict["station"] = station
        last_year_tobs_most_active_dict["date"] = date
        last_year_tobs_most_active_dict["tobs"] = tobs
        all_mostactivetobs.append(last_year_tobs_most_active_dict)

    return jsonify(all_mostactivetobs)    

#----------------------------------------------------------------------------------------------------------------------
# Rubric - API Dynamic Route 
#   The dynamic route does all of the following: 
#   Start route 
#      ✓ Route accepts the start date as a parameter from the URL 
#   Start/end route 
#      ✓ Route accepts the start and end dates as parameters from the URL 
#      ✓ Returns the min, max, and average temperatures calculated from the given start date to the given end date   ✓ Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset 
#----------------------------------------------------------------------------------------------------------------------

@app.route("/api/v1.0/start/<start>/")
def calc_start_temps(start):
    """Return a JSON API of the minimum temperature, the average temperature, and the max temperature...
    for all dates greater than and equal to the start date."""

    print("Calculate Start Temps. API request received.")
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query will accept start date in the format '%Y-%m-%d' and return the minimum, average, and maximum temperatures
    # for all dates from that date.
    start_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Iterate through start temps to append all key/values to Start (Date) Calc Temp dictionary.
    # Append Start (Date) Calc Temp dictionary to list, then return jsonify.
    all_start_calc_temps = []
    for result in start_temps:
        start_calc_temp_dict = {}
        start_calc_temp_dict["min_temp."] = result[0]
        start_calc_temp_dict["avg_temp."] = result[1]
        start_calc_temp_dict["max_temp."] = result[2]
        all_start_calc_temps.append(start_calc_temp_dict)

    return jsonify(all_start_calc_temps)

@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>")
def calc_start_end_temps(start_date, end_date):
#    Return a JSON API of the minimum temperature, the average temperature, and the max temperature 
#    between the start and end date inclusive.

    print("Calculate Start/End Temps. API request received.")

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query will accept start and end dates in the format '%Y-%m-%d' and return the minimum, average, and 
    # maximum temperatures for all dates in that range.
    start_end_temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Iterate through start temps to append all key/values to Start (Date) Calc Temp dictionary.
    # Append Start (Date) Calc Temp dictionary to list, then return jsonify.
    all_calc_start_end_temps = []
    for result in start_end_temps:
        calc_start_end_temp_dict = {}
        calc_start_end_temp_dict["min_temp."] = result[0]
        calc_start_end_temp_dict["avg_temp."] = result[1]
        calc_start_end_temp_dict["max_temp."] = result[2]
        all_calc_start_end_temps.append(calc_start_end_temp_dict)

    return jsonify(all_calc_start_end_temps)

if __name__ == '__main__':
    app.run(debug=True)

session.close()

#----------------------------------------------------------------------------------------------------------------------
#                                                      THE END
#----------------------------------------------------------------------------------------------------------------------
