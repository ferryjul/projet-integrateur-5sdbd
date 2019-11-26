from flask import Flask, request, redirect
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
import requests
import os

app = Flask(__name__)
api = Api(app)

storage = []



class storageMS(Resource):
    def get(self, req):
        if(len(storage) > 0):
            #redirect to ip of storageMS with the input request transfered as well
            return redirect("http://" + str(storage[0]) + "/" + req, code=302)
        else:
            return "Storage MicroService has not started yet"

    def put(self, ip):
        global storage
        if(ip not in storage):
            storage.append(ip)
        return "Done"



# Access the storage microservice
api.add_resource(storageMS, '/storageMS/GET/<path:rea>')
api.add_resource(storageMS, '/storageMS/PUT/<path:ip')



if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
