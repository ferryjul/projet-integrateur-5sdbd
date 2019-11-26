from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import csv
from requests import get, put
import os

ip_orchestrateur = "192.168.37.106"

#Get online on the orchestrateurMS
try:
    put("http://" + ip_orchestrateur + "/processingMS/update")
except:
    pass

app = Flask(__name__)
api = Api(app)


class Ping(Resource):
    def get(self):
        return "Done"

class Test(Resource):
    def get(self, data):
        return "Done"

# Ping method for the orchestrateurMS
api.add_resource(Ping, '/ping')

api.add_resource(Test, '/test/<path:data>')


if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
