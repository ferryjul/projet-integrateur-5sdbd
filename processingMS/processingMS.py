from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import csv
from requests import get, put
import os
from datetime import datetime, timedelta

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


class StationsFillingRateJSONQuery(Resource):

	@staticmethod
	def get_correct_stations_numBikes_json(timeAhead):
		actualRates = get(url='http://localhost:80/stations_current_status.json')
		
		# Computing target dates
		now = datetime.now()# + timedelta(hours = 4464) # pour taper dans les csv chargés !
		dateObj =  now.strftime('%m-%d %H:%M:%S')#%Y-
		year = int(now.strftime("%Y"))
		year = year - 1
		dateWanted = str(year) + "-" + dateObj

		nowPlus10 = now + timedelta(hours=timeAhead)
		dateObj2 =  nowPlus10.strftime('%m-%d %H:%M:%S')#%Y-
		year = int(nowPlus10.strftime("%Y"))
		year = year - 1
		dateWanted2 = str(year) + "-" + dateObj2

		# Request data to Cassandra
		try:
			req = "http://192.168.37.106/storageMS/sql-query/\"SELECT json * FROM data WHERE start_time >= '%s' AND  start_time <= '%s' ALLOW FILTERING\"" %(dateWanted, dateWanted2)
			res = get(req)
			if(res.status_code != 200):
				print(res.text)
		except ConnectionError:
			return "failed to connect to Cassandra"
		
		# Compute past flows
		station_dict = dict()

		#print(res.text)
		data = res.json()
		l = len(data)
		kk = 0
		i = 0
		j = 0
		index = 0
		for line in data:
			stationName = line["start_station_id"]
			if not (stationName in station_dict):
				station_dict[stationName] = dict()
				for i in range(0,24):
					station_dict[stationName][i] = [0, 0]
			dateStr = line["start_time"]
			if '.' in dateStr:
				dateC = dateStr.split('.')
				dateStr = dateC[0]
			dateObj =  datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
			ok = False
			while(not ok):
				iPlus1 = (i+1)
				if iPlus1 != 24:
					iPlus1 = '%d:00:00' %iPlus1
				else:
					iPlus1 = '23:59:59'
				if(datetime.strptime('%d:00:00' %i, '%H:%M:%S').time() <= dateObj.time() and dateObj.time() <= datetime.strptime(iPlus1, '%H:%M:%S').time()):
					station_dict[stationName][i][0] = station_dict[stationName][i][0] + 1
					ok = True
				else:
					if i == 23:
						i = 0
					else:
						i = i + 1
			stationName = line["end_station_id"]
			if not (stationName in station_dict):
				station_dict[stationName] = dict()
				for i in range(0,24):
					station_dict[stationName][i] = [0, 0]
			dateStr = line["stop_time"]
			if '.' in dateStr:
				dateC = dateStr.split('.')
				dateStr = dateC[0]
			dateObj =  datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
			ok = False
			while(not ok):
				jPlus1 = (j+1)
				if jPlus1 != 24:
					jPlus1 = '%d:00:00' %jPlus1
				else:
					jPlus1 = '23:59:59'
				if(datetime.strptime('%d:00:00' %j, '%H:%M:%S').time() <= dateObj.time() and dateObj.time() <= datetime.strptime(jPlus1, '%H:%M:%S').time()):
					station_dict[stationName][j][1] = station_dict[stationName][j][1] + 1
					ok = True
				else:
					if j == 23:
						j = 0
					else:
						j = j + 1
			kk = kk + 1
			index = index + 1

		stations_new = dict()
		# Computing previsional number of bikes
		for stationName in station_dict:
			nbBase = actualRates["stations"][stationName]["num_bikes_available"]
			flowsBest = [nbBase]
			for i in range(0, timeAhead-1):
				nbBase = nbBase + station_dict[stationName][i][1] - station_dict[stationName][i][0]
				flowsBest.append(nbBase)
			stations_new[stationName] = flowsBest
		return jsonify(stations_new)

	def get(self, timeAhead):
		return StationsFillingRateJSONQuery.get_correct_stations_numBikes_json(timeAhead)

class Update_orchestrateur(Resource):
    def get(self):
        try:
            put("http://" + ip_orchestrateur + "/storageMS/update")
        except:
            pass
        return "Done"

# Give GET request to get a corrected version of the realtime station status json
api.add_resource(StationsStatusJSONQuery, '/stations_current_status.json')
api.add_resource(StationsFillingRateJSONQuery, '/predict/<int:timeAhead>')

# Update method in case the orchestrateur has to reboot, to avoid the need to reboot each MS
api.add_resource(Update_orchestrateur, '/reboot')

# Ping method for the orchestrateurMS
api.add_resource(Ping, '/ping')

api.add_resource(Test, '/test/<path:data>')


if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
