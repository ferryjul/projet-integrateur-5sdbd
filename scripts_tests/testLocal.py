import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os.path
import pickle
import heapq

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
#input_file = "201909-citibike-tripdata.csv"
image_name = "bigdatasetbackground-bestQ.png"
useImage = True
nbArrows = 200
max_radius = 70
station_dict = dict()
it_dict = dict()

if os.path.exists("./" + input_file + ".dump") and os.path.exists("./" + input_file + "-it.dump") :
    with open(input_file + ".dump", 'rb') as handle:
        station_dict = pickle.load(handle)
    print("Retrieved dictionnary from local directory.")
    with open(input_file + "-it.dump", 'rb') as handle:
        it_dict = pickle.load(handle)
    print("Retrieved it dictionnary from local directory.")
else:
    data = pd.read_csv(input_file) 
    l = len(data.iloc[:,4])
    # Initial call to print 0% progress
    printProgressBar(0, l, prefix = 'Discovering stations:', suffix = 'Complete', length = 50)
    for index in range(len(data.iloc[:,4])):
        if not (data.iloc[:,4][index]) in it_dict:
            it_dict[data.iloc[:,4][index]] = dict()
            it_dict[data.iloc[:,4][index]][data.iloc[:,8][index]] = 1
        elif not(data.iloc[:,8][index] in it_dict[data.iloc[:,4][index]]) :
            it_dict[data.iloc[:,4][index]][data.iloc[:,8][index]] = 1
        else:
            it_dict[data.iloc[:,4][index]][data.iloc[:,8][index]] = it_dict[data.iloc[:,4][index]][data.iloc[:,8][index]] + 1
        if not (data.iloc[:,4][index]) in station_dict:
            station_dict[data.iloc[:,4][index]] = [data.iloc[:,3][index], data.iloc[:,5][index], data.iloc[:,6][index], 1, 0]
        else:
            currNbDepartures = station_dict[data.iloc[:,4][index]][3]
            currNbArrivals = station_dict[data.iloc[:,4][index]][4]
            station_dict[data.iloc[:,4][index]] = [data.iloc[:,3][index], data.iloc[:,5][index], data.iloc[:,6][index], currNbDepartures+1, currNbArrivals]
        if not (data.iloc[:,8][index]) in station_dict:
            station_dict[data.iloc[:,8][index]] = [data.iloc[:,7][index], data.iloc[:,9][index], data.iloc[:,10][index], 0, 1]
        else:
            currNbDepartures = station_dict[data.iloc[:,8][index]][3]
            currNbArrivals = station_dict[data.iloc[:,8][index]][4]
            station_dict[data.iloc[:,8][index]] = [data.iloc[:,7][index], data.iloc[:,9][index], data.iloc[:,10][index], currNbDepartures, currNbArrivals+1]
        printProgressBar(index + 1, l, prefix = 'Discovering stations:', suffix = 'Complete', length = 50)
    with open(input_file + ".dump", 'wb') as handle:
        pickle.dump(station_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Dumped computed dictionnary.")
    with open(input_file + "-it.dump", 'wb') as handle:
        pickle.dump(it_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Dumped computed it dictionnary.")
    print("Processed ", l, "lines of data.")

heap = []
for d in it_dict:
    for s in it_dict[d]:
        heapq.heappush(heap, ((-1)*it_dict[d][s],[d,s]))
i = 0
while i < nbArrows:    
    el = heapq.heappop(heap)
    nb = el[0]
    bestd = el[1][0]
    bests = el[1][1]
    print("orig:", bestd, ", dest:", bests, "traffic = ", nb)
    plt.arrow(station_dict[bestd][2], station_dict[bestd][1], station_dict[bests][2]-station_dict[bestd][2], station_dict[bests][1]-station_dict[bestd][1], head_width=0.003, head_length=0.003, fc='lightblue', ec='black')
    i = i + 1
           
            
#print("best trip : ", bestd, " to ", bests, "( ", maxT, " trips)")

#print(stations)
latitudes = [station_dict[i][2] for i in station_dict]
longitudes = [station_dict[i][1] for i in station_dict]
departures = [station_dict[i][3] for i in station_dict]
arrivals = [station_dict[i][4] for i in station_dict]

traffic = departures + arrivals
trafficSize = []
colorPoints = []
max_traffic = max(traffic)
print("max traffic = ", max_traffic)
ij = 0
for s in station_dict:
    trafficSize.append((traffic[ij]/max_traffic)*max_radius)
    #plt.annotate(s, (station_dict[s][2], station_dict[s][1]))
    if 0.9*max_traffic < (traffic[ij]):
        colorPoints.append('red')
        #plt.annotate(s, (station_dict[s][2], station_dict[s][1]), fontsize=15, va='bottom', color='red')
    else:
        colorPoints.append('blue')
    ij = ij + 1
if(useImage):  
    im = plt.imread(image_name)
    print("loaded background image")

plt.axis([-74.03, -73.9,40.65, 40.82])
#plt.axis('equal')
plt.scatter(latitudes, longitudes, s=trafficSize, c = colorPoints)
plt.imshow(im, zorder=0, extent=[-74.03, -73.9,40.65, 40.82])
print("Found ", len(station_dict), " stations.")
#plt.arrow(station_dict[bestd][2], station_dict[bestd][1], station_dict[bests][2]-station_dict[bestd][2], station_dict[bests][1]-station_dict[bestd][1], head_width=0.003, head_length=0.003, fc='lightblue', ec='black')
plt.show()

'''
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
traffic = [10, 5, 5, 6, 1]
max_traffic = max(traffic)
print("max = ", max_traffic)
ij = 0
for s in station_names:
    traffic.append((traffic[ij]/max_traffic)*max_radius)
plt.scatter(latitudes, longitudes , s=traffic)
print("Found ", len(station_names), " stations.")

# To print names uncomment
for i, txt in enumerate(station_names):
    plt.annotate(txt, (latitudes[i], longitudes[i]))
plt.show()
'''