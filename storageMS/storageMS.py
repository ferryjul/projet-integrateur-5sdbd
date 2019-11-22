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
import hashlib

app = Flask(__name__)
api = Api(app)

host='localhost'
user='root'
passwd='useruser'
db='mydb'

mydb = None
cursor = None

def open_db():
    global host
    global user
    global passwd
    global db
    global mydb
    global cursor

    # Open BDD
    print("Opening BDD")
    mydb = MySQLdb.connect(host, user, passwd, db)
    cursor = mydb.cursor()

def close_db():
    global mydb
    global cursor
    # Close BDD
    print("Closing BDD")
    mydb.commit()
    cursor.close()

def update_table(addr):
    open_db()
    # Load csv in database
    print("Loading dataset")
    csv_data = csv.reader(open(addr))
    first = True
    for row in csv_data:
        # Allow blank cells
        for i in range(len(row)):
            if row[i] == '':
                row[i] = None
        if first:
            first = False
        else:
            unique_id = str(hashlib.md5(str(row).encode()).hexdigest())
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
    close_db()




class Dataset(Resource):
    def get(self, dataset_address):
        # Download and save file
        print("Downloading file")
        file = requests.get(dataset_address[1:-1], stream=True)
        dump = file.raw
        location = os.path.relpath("./")
        with open("file_tmp.csv", 'wb') as location:
            shutil.copyfileobj(dump, location)
        del dump
        
        #Call update_table fct
        update_table(location)

        # Delete temporary file
        print("Deleting temporary files")
        os.remove('file_tmp.csv')
        return "Done"

class DatasetLocal(Resource):
    def get(self, dataset_address):
        #Call update_table fct
        update_table(dataset_address[1:-1])
        return "Done"

class ExecSQLQuery(Resource):
    def get(self, sql_query):
        #Execute the request on the table
        open_db()
        result = None

        try:
                cursor.execute(sql_query[1:-1])
                result = cursor.fetchall()
        except:
            close_db()
            return "Request failed: check you syntax"

        close_db()
        return jsonify(result)



# Give URL to dataset
api.add_resource(Dataset, '/add-distant-dataset/<path:dataset_address>')

# Give absolute path to dataset
api.add_resource(DatasetLocal, '/add-local-dataset/<path:dataset_address>')

# Give SQL request to execute on the database
api.add_resource(ExecSQLQuery, '/sql-query/<path:sql_query>')



if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
