from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
import MySQLdb
import csv
import requests
import os
import shutil

db_connect = create_engine('sqlite:///chinook.db')
app = Flask(__name__)
api = Api(app)
table_name = 'data'
column_names = '(trip_id, tripduration, starttime, stoptime, start_station_id, \
                start_station_name, start_station_latitude, start_station_longitude, \
                end_station_id, end_station_name, end_station_latitude, end_station_longitude, \
                bikeid, usertype, birth_year, gender)'
class Dataset(Resource):
    def get(self, dataset_address):
        # Open BDD
        print("Opening BDD")
        mydb = MySQLdb.connect(host='localhost',
            user='root',
            passwd='useruser',
            db='mydb')
        cursor = mydb.cursor()
        # Download and save file
        print("Downloading file")
        file = requests.get(dataset_address, stream=True)
        dump = file.raw
        location = os.path.relpath("./")
        with open("file_tmp.csv", 'wb') as location:
            shutil.copyfileobj(dump, location)
        del dump
        # Load csv in database
        print("Loading dataset")
        csv_data = csv.reader(open("/home/user/tests/JC-201509-citibike-tripdata.csv"))
        first = True
        for row in csv_data:
            # Allow blank cells
            for i in range(len(row)):
                if row[i] == '':
                    row[i] = None
            if first:
                first = False
            else:
                unique_id = str(hash(str(row)))
                row = [unique_id] + row

                try:
                    cursor.execute('INSERT INTO data(trip_id, trip_duration, start_time, stop_time,    start_station_id, \
                    start_station_name, start_station_latitude, start_station_longitude, \
                    end_station_id, end_station_name, end_station_latitude, end_station_longitude, \
                    bike_id, user_type, birth_year, gender )' \
                    'VALUES(%s, %s, %s, %s, %s, \
                    %s, %s, %s, \
                    %s, %s, %s, %s, \
                    %s, %s, %s, %s)', row)
                except:
                    pass;
        # Close BDD
        print("Closing BDD")
        mydb.commit()
        cursor.close()
        # Delete temporary file
        print("Deleting temporary files")
        os.remove('file_tmp.csv')
        return "Done"

class DatasetLocal(Resource):
    def get(self, dataset_address):
        # Open BDD
        print("Opening BDD")
        mydb = MySQLdb.connect(host='localhost',
            user='root',
            passwd='useruser',
            db='mydb')
        cursor = mydb.cursor()
        # Load csv in database
        print("Loading dataset")
        csv_data = csv.reader(open("/home/user/tests/JC-201509-citibike-tripdata.csv"))
        first = True
        for row in csv_data:
            # Allow blank cells
            for i in range(len(row)):
                if row[i] == '':
                    row[i] = None
            if first:
                first = False
            else:
                unique_id = str(hash(str(row)))
                row = [unique_id] + row
                try:
                    cursor.execute('INSERT INTO data(trip_id, trip_duration, start_time, stop_time,    start_station_id, \
                    start_station_name, start_station_latitude, start_station_longitude, \
                    end_station_id, end_station_name, end_station_latitude, end_station_longitude, \
                    bike_id, user_type, birth_year, gender )' \
                    'VALUES(%s, %s, %s, %s, %s, \
                    %s, %s, %s, \
                    %s, %s, %s, %s, \
                    %s, %s, %s, %s)', row)
        # Close BDD
        print("Closing BDD")
        mydb.commit()
        cursor.close()
        return "Done"

# Give URL to dataset
api.add_resource(Dataset, '/add-distant-dataset/<dataset_address>') # Route_1

# Give absolute path to dataset
api.add_resource(DatasetLocal, '/add-local-dataset/<dataset_address>') # Route_2



if __name__ == '__main__':
     app.run(port='80', host='192.168.1.5')
