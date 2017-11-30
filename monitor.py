import time
import requests
from data import data_utils

# process for one
def monitorOne(website):
    checkInterval = website.checkInterval
    while True:
        # todo define timeout
        req = requests.get(website.url, timeout=checkInterval)
        reqCode = req.status_code
        reqTime = req.elapsed
        # unix epoch time good for comparison
        currentTime = time.time()
        website.log[currentTime] = {'code':reqCode, 'responseTime':reqTime}
        time.sleep(checkInterval)

def twoMinsData(website):
    currentTime = time.time()
    # inside the dic from most recent to most ancient
    # reverse order
    timeList = list(website.log.keys())
    inTwoMins = []
    # getting the times within 2mins
    for listind in range(len(timeList)):
        if (currentTime-timeList[len(timeList)-1-listind] <= 120):
            inTwoMins.append(timeList[len(timeList)-1-listind])
    # iterate through the logs of the last two minutes
    maxTime = computeMaxResponseTime(website, inTwoMins)
    website.twoMins[currentTime] = {'maxRespTime' : maxTime}
    return

def tenMinsData():
    # duplicate 2mins in ten, change  120 in 600, actually we could merge the 2 func
    return

    # 2 min timeframe

    # 10 min timeframe


def computeMaxResponseTime(website, timeframe):
    maxTime = 0
    for timeReq in timeframe:
        if website.log[timeReq].responseTime > maxTime:
            maxTime = website.log[timeReq].responseTime
    return maxTime