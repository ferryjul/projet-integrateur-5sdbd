import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os.path
import pickle
import heapq
from datetime import datetime
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

def initStation(stationName):
    station_dict[stationName] = dict()
    for dayStr in days:
        station_dict[stationName][dayStr] = dict()
        for i in range(0,24):
            station_dict[stationName][dayStr][i] = [0, 0]

#input_file = "JC-201509-citibike-tripdata.csv"
#input_file = "201306-citibike-tripdata.csv"
#input_file = "2014-02 - Citi Bike trip data.csv"
input_file = "201909-citibike-tripdata.csv"
image_name = "bigdatasetbackground-bestQ.png"
useImage = True
nbArrows = 200
max_radius = 70
days=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
station_dict = dict()
if os.path.exists("./" + input_file + "-stations_pred.dump"):
    with open(input_file + "-stations_pred.dump", 'rb') as handle: 
        station_dict = pickle.load(handle)
    print("Retrieved dictionnary from local directory.")
else:
    data = pd.read_csv(input_file)
    l = len(data.iloc[:,4])
    # Initial call to print 0% progress
    printProgressBar(0, l, prefix = 'Discovering stations:', suffix = 'Complete', length = 50)
    kk = 0
    i = 0
    j = 0
    for index in range(len(data.iloc[:,4])):
        stationName = data.iloc[:,4][index]
        if not (stationName in station_dict):
            initStation(stationName)
        dateStr = data.iloc[:,1][index]
        if '.' in dateStr:
            dateC = dateStr.split('.')
            dateStr = dateC[0]
        dateObj =  datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
        dayStr = days[dateObj.weekday()]
        #print("Date = ", dateStr, ", Day = ", dayStr)
        ok = False
        while(not ok):
            iPlus1 = (i+1)
            if iPlus1 != 24:
                iPlus1 = '%d:00:00' %iPlus1
            else:
                iPlus1 = '23:59:59'
            if(datetime.strptime('%d:00:00' %i, '%H:%M:%S').time() <= dateObj.time() and dateObj.time() <= datetime.strptime(iPlus1, '%H:%M:%S').time()):
                #print(dateStr, " between %d and %d am" %(i, i+1))
                station_dict[stationName][dayStr][i][0] = station_dict[stationName][dayStr][i][0] + 1
                ok = True
            else:
                if i == 23:
                    i = 0
                else:
                    i = i + 1
        stationName = data.iloc[:,8][index]
        if not (stationName in station_dict):
            initStation(stationName)
        dateStr = data.iloc[:,2][index]
        if '.' in dateStr:
            dateC = dateStr.split('.')
            dateStr = dateC[0]
        dateObj =  datetime.strptime(dateStr, '%Y-%m-%d %H:%M:%S')
        dayStr = days[dateObj.weekday()]
        #print("Date = ", dateStr, ", Day = ", dayStr)
        ok = False
        while(not ok):
            jPlus1 = (j+1)
            if jPlus1 != 24:
                jPlus1 = '%d:00:00' %jPlus1
            else:
                jPlus1 = '23:59:59'
            if(datetime.strptime('%d:00:00' %j, '%H:%M:%S').time() <= dateObj.time() and dateObj.time() <= datetime.strptime(jPlus1, '%H:%M:%S').time()):
                #print(dateStr, " between %d and %d am" %(i, i+1))
                station_dict[stationName][dayStr][j][1] = station_dict[stationName][dayStr][j][1] + 1
                ok = True
            else:
                if j == 23:
                    j = 0
                else:
                    j = j + 1
        if kk%1000 == 0:
            printProgressBar(index + 1, l, prefix = 'Discovering stations:', suffix = 'Complete', length = 50)
        kk = kk + 1
    with open(input_file + "-stations_pred.dump", 'wb') as handle:
        pickle.dump(station_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Dumped computed dictionnary.")
    print("Processed ", l, "lines of data.")


#plt.axis('equal')
heap = []
for s in station_dict:
    tot = 0
    for d in days:
        for t in range(0,24):
            tot = tot + station_dict[s][d][t][0] + station_dict[s][d][t][1]
    #print(s, tot)
    heapq.heappush(heap, ((-1)*tot,s))

stationName = heapq.heappop(heap)[1]
stationName = heapq.heappop(heap)[1]
stationName = heapq.heappop(heap)[1]
print("Best station = ", stationName)
for day in days:
    l = []
    lB = []
    lDelta = []
    #"Concord St & Bridge St"#"Greenwich St & N Moore St"
    for v in station_dict[stationName][day]:
        l.append(station_dict[stationName][day][v][0])
        lB.append(station_dict[stationName][day][v][1])
        lDelta.append(station_dict[stationName][day][v][1]-station_dict[stationName]["Monday"][v][0])
    line = []
    for i in range(0,24):
        line.append(0)
        

    #plt.scatter(range(0,24), l, label="taken-bikes")
    plt.plot(range(0,24), lDelta, label="given-bikes")
    plt.plot(range(0,24), line)
    plt.title(day)
    #plt.arrow(station_dict[bestd][2], station_dict[bestd][1], station_dict[bests][2]-station_dict[bestd][2], station_dict[bests][1]-station_dict[bestd][1], head_width=0.003, head_length=0.003, fc='lightblue', ec='black')
    plt.show()
