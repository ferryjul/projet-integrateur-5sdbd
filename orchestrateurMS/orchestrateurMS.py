from flask import Flask, request, redirect
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
from  requests import get, put
import os
from threading import Thread
import time

app = Flask(__name__)
api = Api(app)


storage = []


#Class for the real time update of online microservices
class updateOnline(Thread):
    def __init__(self, ip):
        Thread.__init__(self)
        self.ip = ip

    def run(self):
        while True:
            try:
                z = get("http://" + self.ip + "/ping").content
                print("z: ", z)
                if(z != b'"Done"\n'):
                    break
            except:
                break
            time.sleep(5)
        print("Microservice disconnected at ip: ", self.ip)
        storage.remove(self.ip)



class storageMS(Resource):
    def get(self, req):
        if(len(storage) > 0):
            #redirect to ip of storageMS with the input request transfered as well
            return redirect("http://" + str(storage[0]) + "/" + req, code=302)
        else:
            return "Storage MicroService has not started yet"

    def put(self, req):
        if(req=="update"):
            global storage
            ip = str(request.remote_addr)
            if(ip not in storage):
                storage.append(ip)
                print("Ajout ip storage: ", ip)
                thread = updateOnline(ip)
                thread.start()
        return "Done"



# Access the storage microservice
api.add_resource(storageMS, '/storageMS/<path:req>')



if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
