import time
import requests
import multiprocessing
from multiprocessing import Process, Queue
from data import data_utils
from datetime import timedelta


def startMonitor(user, queueTwoMin, queueTenMin, queueAlerts):
    Monitor(user, queueTwoMin, queueTenMin, queueAlerts)

class Monitor(object):

    def __init__(self, user, queueTwoMin, queueTenMin, queueAlerts):
        self.user = user
        self.originalTime = time.time()
        # queue to transmit all data
        self.queueTwoMin = queueTwoMin
        self.queueTenMin = queueTenMin
        self.queueAlerts = queueAlerts
        # start monitoring
        self.monitorAll()


    def monitorAll(self):
        # main monitor process
        websites = self.user.mySites.values()


        # subprocesses to get the requests logs
        processes = [Process(target=self.monitorOne, args=(website,)) for website in websites]
        for process in processes:
            process.daemon = True
            process.start()

        for process in processes:
            process.join()
        return




    def monitorOne(self,website):
        """
        Monitoring for each website
        :param website:
        :return:
        """
        # print(website)
        checkInterval = website.checkInterval
        while True:
            startSubProcess = time.time()
            # todo define timeout
            req = requests.get(website.url, timeout=checkInterval)
            reqCode = req.status_code
            reqTime = req.elapsed
            # unix epoch time good for comparison
            currentTime = time.time()
            website.log[currentTime] = {'code': reqCode, 'responseTime': reqTime}
            # 2 mins
            twoMinsDic = self.getTimeframedData(website, 120, currentTime)
            self.queueTwoMin.put(twoMinsDic)
            # 10 mins
            tenMinsDic = self.getTimeframedData(website, 600, currentTime)
            self.queueTenMin.put(tenMinsDic)
            endSubProcess = time.time()
            # print(self.queueTwoMin)
            time.sleep(checkInterval-(endSubProcess-startSubProcess))


    # todo suppress old logs
    def getTimeframedData(self,website, timeframe, currentTime=time.time()):
        timeList = list(website.log.keys())
        # inside the dic from most recent to most ancient
        # reverse order
        # list of time of requests
        inFrame = []
        # getting the times within 2mins
        for listind in range(len(timeList)):
            if (currentTime-timeList[len(timeList)-1-listind] <= timeframe):
                inFrame.append(timeList[len(timeList)-1-listind])
        # Indicators
        # Max
        maxTime = self.computeMaxResponseTime(website, inFrame)
        avgTime = self.computeAvgResponsetime(website, inFrame)
        availability = self.computeAvailability(website, inFrame)
        if (timeframe == 120):
            self.checkForAvailabiltyAlert(website= website, availability= availability)
        # website.twoMins[currentTime] = {'maxRespTime' : maxTime}

        return {'website': website, 'frame': timeframe,'time': currentTime, 'indicators': {'maxTime': maxTime, 'avgTime': avgTime, 'availability': availability}}


    def computeMaxResponseTime(self, website, inFrame):
        maxTime = 0
        for timeOfReq in inFrame:
            if website.log[timeOfReq]['responseTime'] > timedelta(seconds=maxTime):
                maxTime = self.timedeltaToFloat(website.log[timeOfReq]['responseTime'])
        return maxTime

    def computeAvgResponsetime(self,website, inFrame):
        avgTime = 0
        for timeOfReq in inFrame:
            avgTime += self.timedeltaToFloat(website.log[timeOfReq]['responseTime'])
        avgTime = avgTime / len(inFrame)
        return avgTime

    def computeAvailability(self, website, inFrame):
        availability = 0
        for timeReq in inFrame:
            if website.log[timeReq]['code'] == 200:
                availability += 1
        availability = availability / len(inFrame)
        return availability

    def checkForAvailabiltyAlert(self,website,availability):
        if availability < 0.8:
            alert = {'website': str(website), 'time': time.time(), 'availability': availability}
            self.queueAlerts.put(alert)
        return

    def timedeltaToFloat(self,time_d):
        """
        Transforms a time delta type to a float, for readability on the display
        Note that only minutes are considered, because I assume that response times won't exceed an hour
        :param time_d:
        :return:
        """
        time_d_min = time_d / timedelta(minutes=1)
        time_d_s = time_d / timedelta(seconds=1)
        time_d_ms = time_d / timedelta(milliseconds=1)

        return (time_d_min * 60 + time_d_s + time_d_ms * 0.001)