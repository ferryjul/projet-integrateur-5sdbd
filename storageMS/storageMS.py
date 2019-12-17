from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
from cassandra.cluster import Cluster
import csv
from requests import get, put
import os
import shutil
import hashlib

ip_orchestrateur = "192.168.37.106"

#Get online on the orchestrateurMS
try:
    put("http://" + ip_orchestrateur + "/storageMS/update")
except:
    pass


app = Flask(__name__)
api = Api(app)


db='mydb'
cluster = None
session = None

def open_db():
    global db
    global session
    global cluster

    # Open BDD
    print("Opening BDD")
    cluster = Cluster(['192.168.1.14', '192.168.1.4', '192.168.1.15'])
    session = cluster.connect(db)



def close_db():
    global session
    global cluster
    # Close BDD
    print("Closing BDD")
    cluster.shutdown()
    

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
                session.execute('INSERT INTO data(trip_id, trip_duration, start_time, stop_time,    start_station_id, \
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
                result = session.execute(sql_query[1:-1])
        except:
            close_db()
            return "Request failed: check you syntax"

        close_db()
        return jsonify(result)

class Ping(Resource):
    def get(self):
        return "Done"

# Ping method for the orchestrateurMS
api.add_resource(Ping, '/ping')

# Give URL to dataset
api.add_resource(Dataset, '/add-distant-dataset/<path:dataset_address>')

# Give absolute path to dataset
api.add_resource(DatasetLocal, '/add-local-dataset/<path:dataset_address>')

# Give SQL request to execute on the database
api.add_resource(ExecSQLQuery, '/sql-query/<path:sql_query>')



if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
