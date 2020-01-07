from flask import Flask, request
from flask_restful import Resource, Api
import json
from flask_jsonpify import jsonify
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import csv
from requests import get, put
import os
import shutil
import hashlib
import datetime
import time

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
                row[2] = row[2].split('.')[0]
                row[3] = row[3].split('.')[0]
            except:
                pass

            try:
                row[2] = datetime.datetime.strptime(row[2], '%m/%d/%Y %H:%M:%S')
                row[3] = datetime.datetime.strptime(row[3], '%m/%d/%Y %H:%M:%S')
            except:
                pass

            try:
                row[2] = datetime.datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S')
                row[3] = datetime.datetime.strptime(row[3], '%Y-%m-%d %H:%M:%S')
            except:
                pass

            try:
                rq = "INSERT INTO data(trip_id, trip_duration, start_time, stop_time, start_station_id, \
                start_station_name, start_station_latitude, start_station_longitude, \
                end_station_id, end_station_name, end_station_latitude, end_station_longitude, \
                bike_id, user_type, birth_year, gender ) VALUES ('%s',%s,'%s',\
                '%s',%s,'%s',%s,%s,%s,'%s',%s,%s,%s,'%s',%s,%s)"

                rq = rq % tuple(row)


                results = session.execute(rq)

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
        start = time.time()
        try:
                print(sql_query[1:-1])
                statement = SimpleStatement(sql_query[1:-1], fetch_size=100)
                print("statement done")
                result = session.execute(statement)
                print("execute done")
                results = list(result)
                print("list done")
                
        except Exception as e:
            close_db()
            print("ERROR CASSANDRA")
            print(e)
            return "ERROR CASSANDRA DE SES MORTS " + str(e)
        stop = time.time()

        print("query time: ", stop-start)

        close_db()
        H = []
        start = time.time()
        print("nb element", len(results))
        print("iteration start")
        for w in results:
            a = str(w).split("'")[1]
            H.append(json.JSONDecoder().decode(a))
        stop = time.time()
        print("parsing time: ", stop-start)
        print("start jsonify")
        return jsonify(H)

class Ping(Resource):
    def get(self):
        return "Done"

class Update_orchestrateur(Resource):
    def get(self):
        try:
            put("http://" + ip_orchestrateur + "/storageMS/update")
        except:
            pass
        return "Done"


# Ping method for the orchestrateurMS
api.add_resource(Ping, '/ping')

# Update method in case the orchestrateur has to reboot, to avoid the need to reboot each MS
api.add_resource(Update_orchestrateur, '/reboot')

# Give URL to dataset
api.add_resource(Dataset, '/add-distant-dataset/<path:dataset_address>')

# Give absolute path to dataset
api.add_resource(DatasetLocal, '/add-local-dataset/<path:dataset_address>')

# Give SQL request to execute on the database
api.add_resource(ExecSQLQuery, '/sql-query/<path:sql_query>')



if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
