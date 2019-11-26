import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

#input_file = "JC-201509-citibike-tripdata.csv"
#input_file = "201306-citibike-tripdata.csv"
input_file = "2014-02 - Citi Bike trip data.csv"
data = pd.read_csv(input_file) 
# Initial call to print 0% progress
l = len(data.iloc[:,4])
printProgressBar(0, l, prefix = 'Discovering stations:', suffix = 'Complete', length = 50)
stations = []
station_names = []
for index in range(len(data.iloc[:,4])):
    if not (data.iloc[:,4][index]) in station_names:
        station_names.append(data.iloc[:,4][index])
        stations.append([data.iloc[:,3][index], data.iloc[:,4][index], data.iloc[:,5][index], data.iloc[:,6][index]])
    if not (data.iloc[:,8][index]) in station_names:
        station_names.append(data.iloc[:,8][index])
        stations.append([data.iloc[:,7][index], data.iloc[:,8][index], data.iloc[:,9][index], data.iloc[:,10][index]])
    printProgressBar(index + 1, l, prefix = 'Discovering stations:', suffix = 'Complete', length = 50)
#print(stations)
latitudes = [stations[i][2] for i in range(len(stations))]
longitudes = [stations[i][3] for i in range(len(stations))]
traffic = []
#for s in station_names:
#    traffic.append(1)
plt.scatter(latitudes, longitudes) #, s=traffic)
print("Found ", len(station_names), " stations.")

# To print names uncomment
'''for i, txt in enumerate(station_names):
    plt.annotate(txt, (latitudes[i], longitudes[i]))'''
plt.show()





'''
for index in range(len(data['Start Station Name'])):
    if not (data['Start Station Name'][index]) in station_names:
        station_names.append(data['Start Station Name'][index])
        stations.append([data['Start Station ID'][index], data['Start Station Name'][index], data['Start Station Latitude'][index], data['Start Station Longitude'][index]])
    if not (data['End Station Name'][index]) in station_names:
        station_names.append(data['End Station Name'][index])
        stations.append([data['End Station ID'][index], data['End Station Name'][index], data['End Station Latitude'][index], data['End Station Longitude'][index]])
#print(stations)
latitudes = [stations[i][2] for i in range(len(stations))]
longitudes = [stations[i][3] for i in range(len(stations))]
plt.scatter(latitudes, longitudes)
print("Found ", len(station_names), " stations.")
for i, txt in enumerate(station_names):
    plt.annotate(txt, (latitudes[i], longitudes[i]))
plt.show()
'''