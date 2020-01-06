import csv
import hashlib
import sys
import os
import time

restart = "sudo service cassandra restart"

dirname = '/home/user/CSV_data/final/'

for filename in os.listdir(dirname):
	cmd = "cqlsh 192.168.1.4 -e \"COPY mydb.data (trip_id, trip_duration, start_time, stop_time, start_station_id, start_station_name, start_station_latitude, start_station_longitude, end_station_id, end_station_name, end_station_latitude, end_station_longitude, bike_id, user_type, birth_year, gender) FROM '" + dirname + filename + "' WITH DELIMITER=',' AND HEADER=TRUE\""

	print(cmd)

	os.system(cmd)

	time.sleep(10)

	os.system(restart)

	time.sleep(10)

	print("done")


