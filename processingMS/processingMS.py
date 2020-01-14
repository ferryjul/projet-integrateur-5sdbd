from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import csv
from requests import get, put
import os
from datetime import datetime, timedelta
import heapq

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
		actualRates = actualRates.json()
		# Computing target dates
		now = datetime.now()# + timedelta(hours = 4464) # pour taper dans les csv chargés !
		dateObj =  now.strftime('%m-%d %H:%M:%S')#%Y-
		year = int(now.strftime("%Y"))
		HOUR = int(now.strftime("%H"))
		year = year - 1
		dateWanted = str(year) + "-" + dateObj

		nowPlus10 = now + timedelta(hours=timeAhead)
		dateObj2 =  nowPlus10.strftime('%m-%d %H:%M:%S')#%Y-
		year = int(nowPlus10.strftime("%Y"))
		year = year - 1
		dateWanted2 = str(year) + "-" + dateObj2
		print("Wanted interval = ", dateWanted, " to ", dateWanted2)
		req = "http://192.168.37.106/storageMS/sql-query/\"SELECT json * FROM data WHERE start_time >= '%s' AND  start_time <= '%s' ALLOW FILTERING\"" %(dateWanted, dateWanted2)
		print("requesting to Cassandra :", req)
		# Request data to Cassandra
		try:
			res = get(req)
			if(res.status_code != 200):
				print("error message : ", res.text)
				return res.text
		except ConnectionError:
			return "failed to connect to Cassandra"
		
		print(len(res.json()), " elements in dict.")
		if "ERROR CASSANDRA" in res.text:
			return "Erreur de Cassandra -> elle a pas les données"
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
			if str(stationName) in actualRates["stations"]:
				nbBase = int(actualRates["stations"][str(stationName)]["num_bikes_available"])
				flowsBest = [nbBase]
				cnt = 0
				i = HOUR
				while cnt < timeAhead:
				#for i in range(HOUR, timeAhead-1):
					if i >= 24:
						i = 0
					nbBase = nbBase + station_dict[stationName][i][1] - station_dict[stationName][i][0]
					#print("[station %d] Plus %d bikes, Moins %d bikes" %(stationName,station_dict[stationName][i][1],station_dict[stationName][i][0]))
					flowsBest.append(nbBase)
					i = i + 1
					cnt = cnt + 1
				stations_new[stationName] = flowsBest
		return jsonify(stations_new)

	def get(self, timeAhead):
		return StationsFillingRateJSONQuery.get_correct_stations_numBikes_json(timeAhead)

class DamagedBikesJSONQuery(Resource):

	@staticmethod
	def get_correct_damaged_json(date_1, date_2):
		date1 = datetime.datetime.strptime(date_1, '%Y-%m-%d %H:%M:%S')
		date2 = datetime.datetime.strptime(date_2, '%Y-%m-%d %H:%M:%S')
		print("Requesting data")
		# Interrogation de Cassandra
		try:
			res = get("http://192.168.37.106/storageMS/sql-query/\"SELECT json * FROM data WHERE start_time >= '%s' AND  start_time <= '%s' ALLOW FILTERING\"" %(date1, date2))
			print("status = ", res.status_code)
		except ConnectionError:
			print("failed to connect to Cassandra")

		print("Got data")
		print(len(res.json()), " elements in dict.")

		brokenThreshold = 1
		station_dict = dict()
		it_dict = dict()
		itBis_dict = dict()
		data = res.json()
		l = len(data)
		index = 0
		for line in data:
			if not (line["start_station_id"]) in it_dict:
				it_dict[line["start_station_id"]] = dict()
				it_dict[line["start_station_id"]][line["end_station_id"]] = 1
			elif not(line["end_station_id"] in it_dict[line["start_station_id"]]) :
				it_dict[line["start_station_id"]][line["end_station_id"]] = 1
			else:
				it_dict[line["start_station_id"]][line["end_station_id"]] = it_dict[line["start_station_id"]][line["end_station_id"]] + 1
			if not (line["bike_id"]) in itBis_dict:
				itBis_dict[line["bike_id"]] = []
				itBis_dict[line["bike_id"]].append((line["start_station_id"],line["end_station_id"]))
			else:
				itBis_dict[line["bike_id"]].append((line["start_station_id"],line["end_station_id"]))
			if not (line["start_station_id"]) in station_dict:
				station_dict[line["start_station_id"]] = [line["start_station_id"], line["end_station_latitude"], line["end_station_longitude"], 1, 0]
			else:
				currNbDepartures = station_dict[line["start_station_id"]][3]
				currNbArrivals = station_dict[line["start_station_id"]][4]
				station_dict[line["start_station_id"]] = [line["start_station_id"], line["end_station_latitude"], line["end_station_longitude"], currNbDepartures+1, currNbArrivals]
			if not (line["end_station_id"]) in station_dict:
				station_dict[line["end_station_id"]] = [line["end_station_id"], line["end_station_latitude"], line["end_station_longitude"], 0, 1]
			else:
				currNbDepartures = station_dict[line["end_station_id"]][3]
				currNbArrivals = station_dict[line["end_station_id"]][4]
				station_dict[line["end_station_id"]] = [line["end_station_id"], line["end_station_latitude"], line["end_station_longitude"], currNbDepartures, currNbArrivals+1]
			index = index + 1

		heap = []
		for d in itBis_dict:
			for s in itBis_dict[d]:
				heapq.heappush(heap, ((+1)*(len(itBis_dict[d])),d))

		ok = False
		brokens = []
		while(not ok):
			b = heapq.heappop(heap)
			nb = b[0]
			aBike = b[1]
			if(nb > brokenThreshold):
				ok = True
			else:
				brokens.append(aBike)

		locationsDamaged = dict()
		print("Detected ", len(brokens), " bikes that might be damaged : ")
		for bikeB in brokens:
			locationsDamaged[bikeB]["Station"] = (itBis_dict[bikeB][len(itBis_dict[bikeB]) - 1][1])
			locationsDamaged[bikeB]["Trips"] = len(itBis_dict[bikeB])
			#print("Bike #", bikeB, "(Last seen at station : ", itBis_dict[bikeB][len(itBis_dict[bikeB]) - 1][1], ")")# -> ", len(itBis_dict[bikeB]), " trips.")
		
		return jsonify(locationsDamaged)

	def get(self, data):
		data = data.replace("\"", "")
		tabData = data.split("$")
		date1 = tabData[0]
		date2 = tabData[1]
		return DamagedBikesJSONQuery.get_correct_damaged_json(date1, date2)


class Update_orchestrateur(Resource):
    def get(self):
        try:
            put("http://" + ip_orchestrateur + "/storageMS/update")
        except:
            pass
        return "Done"

# Give GET request to get a corrected version of the realtime station status json
api.add_resource(StationsStatusJSONQuery, '/stations_current_status.json')

# In : Integer timeAhead
# Out : JSON : for each station, previsional filling rates for timeAhead intervals
api.add_resource(StationsFillingRateJSONQuery, '/predict/<int:timeAhead>')

# In : "date1$date2" where date is at format YYYY-MM-DD HH:mm:ss
# Out : JSON : list of damaged bikes along with their station location id
api.add_resource(DamagedBikesJSONQuery, '/damaged/<path:data>')

# Update method in case the orchestrateur has to reboot, to avoid the need to reboot each MS
api.add_resource(Update_orchestrateur, '/reboot')

# Ping method for the orchestrateurMS
api.add_resource(Ping, '/ping')

api.add_resource(Test, '/test/<path:data>')


if __name__ == '__main__':
     app.run(port='80', host='0.0.0.0')
