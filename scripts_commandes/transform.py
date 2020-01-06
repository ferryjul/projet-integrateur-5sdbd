import csv
import hashlib
import sys
import os

basedir = '/home/user/CSV_data/'
dirname = '/home/user/CSV_data/final/'

for filename in os.listdir(basedir):
	if(filename = "final"):
		pass
	elif(filename not in os.listdir(dirname)):
		print("start: " + filename)
		with open(dirname + filename, mode='w') as employee_file:
			csv_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

			with open(basedir + filename) as csv_file:
				csv_reader = csv.reader(csv_file, delimiter=',')
				line_count = 0
				for row in csv_reader:
					for i in range(len(row)):
						if row[i] == '\\N' or row[i] == '':
							row[i] = None
					if line_count == 0:
						csv_writer.writerow(['trip_id'] + row)
					else:
						unique_id = str(hashlib.md5(str(row).encode()).hexdigest())
						row = [unique_id] + row

						csv_writer.writerow(row)
					line_count = line_count+1
		print(line_count)
	else:
		print("Already done")
		os.system("rm '" + basedir + filename + "'")