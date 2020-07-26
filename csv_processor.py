import csv
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

def getActions():
    #returns a list of action - (date-time) tuples based on data from TIA file
    csv_file = open("MyTIA SAK 20180516-20190813 LogsitExport814191215AM DataForTeamAnalysis - Copy of Master for Analysis.csv", mode='r')
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    action_vs_time = []
    line_count = 0
    for row in csv_reader:
        if line_count != 0:
            action_vs_time.append((row["Action"], row["Date-Time"]))
        else:
            line_count += 1

    return action_vs_time

def parseByHeadacheIntensity(action_vs_time):
    headache_subset = []
    for pair in action_vs_time:
        if "Headache" in pair[0]:
            headache_subset.append(pair)

    headache_intensity_vs_time = []
    for pair in headache_subset:
        intensity_level = int(pair[0][11:12])
        headache_intensity_vs_time.append( (intensity_level, datetime.strptime(pair[1], '%m/%d/%Y %H:%M:%S')) )
    return headache_intensity_vs_time

def parseBySleepinessIntensity(action_vs_time):
    sleepy_subset = []
    for pair in action_vs_time:
        if "SSS" in pair[0]:
            sleepy_subset.append(pair)

    sleep_intensity_vs_time = []
    for pair in sleepy_subset:
        intensity_level = int(pair[0][6:7])
        sleep_intensity_vs_time.append( (intensity_level, datetime.strptime(pair[1], '%m/%d/%Y %H:%M:%S')) )
    return sleep_intensity_vs_time

def createIntensityFunction(intensity_vs_time, start_string):
    #returns second-by-second intensity since a given start time
    start_datetime = datetime.strptime(start_string, '%m/%d/%Y %H:%M:%S')
    intensity_deltas = []
    for i in range(len(intensity_vs_time) - 1):
        if i == 0:
            intensity_deltas.append( (intensity_vs_time[i][0], (intensity_vs_time[i][1] - start_datetime)) )
        else:
            intensity_deltas.append( (intensity_vs_time[i][0], (intensity_vs_time[i+1][1] - intensity_vs_time[i][1])) )
    intensity_function = []
    for pair in intensity_deltas:
        num_seconds = (pair[1].days * 24 * 60 * 60) + pair[1].seconds
        for i in range(num_seconds):
            intensity_function.append(pair[0])

    return intensity_function

def graphIntensityFunction(intensity_function, start_hour, end_hour):
    function_slice = intensity_function[start_hour*3600:end_hour*3600]
    x = np.linspace(0.0, (end_hour - start_hour), 3600*(end_hour - start_hour))
    plt.plot(x, function_slice, 'o', color='black')
    plt.show()

def postProcessHeadacheIntensity(headache_intensity_vs_time):
    #enforces the condition that headache 1 lasts for only 5 seconds before heading back to headache 0
    augmented_headache_intensity_vs_time = []
    for pair in headache_intensity_vs_time:
        if pair[0] == 1:
            augmented_headache_intensity_vs_time.append(pair)
            augmented_headache_intensity_vs_time.append((0, pair[1] + timedelta(0, 5) ) )
        else:
            augmented_headache_intensity_vs_time.append(pair)

    return augmented_headache_intensity_vs_time








if __name__ == "__main__":
    action_vs_time = getActions()

    headache_intensity_vs_time = parseByHeadacheIntensity(action_vs_time)
    augmented_headache_intensity_vs_time = postProcessHeadacheIntensity(headache_intensity_vs_time)
    headache_intensity_function = createIntensityFunction(augmented_headache_intensity_vs_time, "5/17/2018 00:00:00")

    graphIntensityFunction(headache_intensity_function, 310, 311)
