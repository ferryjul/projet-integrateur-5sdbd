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

class StationsStatusJSONQuery(Resource):
	# Make and return a realtime stations status json indexed by station_id
	@staticmethod
	def get_correct_stations_status_json():
		r = get(url='https://gbfs.citibikenyc.com/gbfs/en/station_status.json')
		original_stations_status_json = r.json()

		# Instantiate and build a stations status dict indexed by station_id
		sorted_stations_status = {}	
		for i in range(len(original_stations_status_json["data"]["stations"])):
		    sorted_stations_status[original_stations_status_json["data"]["stations"][i]["station_id"]] = original_stations_status_json["data"]["stations"][i]
		
		# Corrected json as a dictionary
		corrected_stations_status_dict = {
		    'last_updated' : original_stations_status_json['last_updated'],
		    'stations' : sorted_stations_status,
		}

		# JSONify then return the corrected_station_status
		return jsonify(corrected_stations_status_dict)

	def get(self):
		return StationsStatusJSONQuery.get_correct_stations_status_json()

# Give GET request to get a corrected version of the realtime station status json
api.add_resource(StationsStatusJSONQuery, '/stations_current_status.json')

# Ping method for the orchestrateurMS
api.add_resource(Ping, '/ping')

api.add_resource(Test, '/test/<path:data>')


if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
