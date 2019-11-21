from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask.ext.jsonpify import jsonify
import MySQLdb
import csv
import requests
import os
import shutil

db_connect = create_engine('sqlite:///chinook.db')
app = Flask(__name__)
api = Api(app)

class Dataset(Resource):
    def get(self, dataset_address):
        # Open BDD
        mydb = MySQLdb.connect(host='localhost',
            user='root',
            passwd='useruser',
            db='mydb')
        cursor = mydb.cursor()
        # Download and save file
        file = requests.get(dataset_address, stream=True)
        dump = file.raw
        location = os.path.relpath("./")
        with open("file_tmp.csv", 'wb') as location:
            shutil.copyfileobj(dump, location)
        del dump
        # Load csv in database
        csv_data = csv.reader(file('file_tmp.csv'))
        for row in csv_data:
            cursor.execute('INSERT INTO testcsv(names, \
                classes, mark )' \
                'VALUES("%s", "%s", "%s")', 
                row)
        # Close BDD
        cursor.close()
        # Delete temporary file
        os.remove('file_tmp.csv')
        return "Done"

class DatasetLocal(Resource):
    def get(self, dataset_address):
        # Open BDD
        mydb = MySQLdb.connect(host='localhost',
            user='root',
            passwd='useruser',
            db='mydb')
        cursor = mydb.cursor()
        # Load csv in database
        csv_data = csv.reader(file(dataset_address))
        for row in csv_data:
            cursor.execute('INSERT INTO testcsv(names, \
                classes, mark )' \
                'VALUES("%s", "%s", "%s")', 
                row)
        # Close BDD
        cursor.close()
        return "Done"

# Give URL to dataset
api.add_resource(Dataset, '/add-distant-dataset/<dataset_address>') # Route_1

# Give absolute path to dataset
api.add_resource(DatasetLocal, '/add-local-dataset/<dataset_address>') # Route_2



if __name__ == '__main__':
     app.run(port='80')