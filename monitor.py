import time
import requests
from multiprocessing import Process, Queue
from datetime import timedelta
import mailSender

# Types of indicators
indicatorsTypes = {'MAX': 'maxTime', 'AVG': 'avgTime', 'AVA': 'availability', 'STA' : 'status'}

def startMonitor(user, queueTwoMin, queueTenMin, queueHour, queueAlerts, queueTermination, testDic = None):
    """
    Simple init of the class, for intelligibility.
    Starting all sub processes
    :param user:
    :param queueTwoMin:
    :param queueTenMin:
    :param queueHour:
    :param queueAlerts:
    :param queueTermination:
    :param testDic:
    :return:
    """
    Monitor(user, queueTwoMin, queueTenMin, queueHour, queueAlerts, queueTermination, testDic = testDic)

class Monitor(object):
    """
    Class that handles all the monitoring
    Subprocess are created for each monitored website, to handle different check intervals
    """

    def __init__(self, user, queueTwoMin, queueTenMin, queueHour, queueAlerts, queueTermination, testDic = None):
        """
        Init, calls at the end the monitor all functin that starts the processes
        :param user:
        :param queueTwoMin:
        :param queueTenMin:
        :param queueHour:
        :param queueAlerts:
        :param queueTermination:
        :param testDic:
        """
        # Start Time, keep track of the elapsed time
        self.originalTime = time.time()
        # User that uses the monitoring app, must exist !
        self.user = user

        # Queue to transmit all data
        self.queueTwoMin = queueTwoMin
        self.queueTenMin = queueTenMin
        self.queueHour = queueHour
        self.queueAlerts = queueAlerts

        # Queue for termination
        self.queueTermination = queueTermination

        # Alert Storage, to check whether raised alert are to be sent
        self.alertsDic = {}
        if testDic:
            self.alertsDic = testDic
        self.mailer = mailSender.MailSender(mailSender.mailrecipient)

        # Start monitoring
        self.monitorAll()


    def monitorAll(self):
        """
        Starts all subprocesses for each website
        :return:
        """

        websites = self.user.mySites.values()

        # subprocesses to get the requests logs
        self.processes = [Process(target=self.monitorOne, args=(website,)) for website in websites]

        for process in self.processes:
            process.daemon = True

        for process in self.processes:
            process.start()

        for process in self.processes:
            process.join()

        return

    def _terminateAll(self):
        """
        Terminate all processes.
        Need exception handling as it can be called several times
        :return:
        """

        # Termination of all processes
        try :
            for process in self.processes:
                process.terminate()
        except AttributeError:
            pass

        return




    def monitorOne(self,website):
        """
        Monitoring for each website
        :param website:
        :return:
        """
        checkInterval = website.checkInterval
        time.sleep(checkInterval)
        while self\
                .queueTermination.empty():
            startSubProcess = time.time()
            # todo define timeout for requests
            try :
                req = requests.get(website.url, timeout=checkInterval)
                reqCode = req.status_code
                reqTime = req.elapsed
            # Generic to handle all kind of http exceptions
            # Possible enhancement
            except Exception:
                continue
            # unix epoch time good for comparison
            currentTime = time.time()
            website.log[currentTime] = {'code': reqCode, 'responseTime': reqTime}
            # 2 mins
            twoMinsDic = self.getTimeframedData(website, 120, currentTime=currentTime)
            self.queueTwoMin.put(twoMinsDic)
            # 10 mins
            tenMinsDic = self.getTimeframedData(website, 600, currentTime=currentTime)
            self.queueTenMin.put(tenMinsDic)
            # 1 hour
            hourDic = self.getTimeframedData(website, 3600, currentTime=currentTime)
            self.queueHour.put(hourDic)

            endSubProcess = time.time()
            # Wait for the next check
            try:
                time.sleep(checkInterval-(endSubProcess-startSubProcess))
            except ValueError:
                pass

        # Terminate all processes
        self._terminateAll()
        return


    # todo suppress old logs
    def getTimeframedData(self, website, timeframe, currentTime=time.time()):
        """
        Get all data for a given timeframe,
        If the timeframe is 2min checks for alerts
        :param website:
        :param timeframe:
        :param currentTime:
        :return:
        """
        timeList = list(website.log.keys())
        # inside the dic from most recent to most ancient
        # reverse order
        # list of time of requests
        inFrame = []
        # getting the times within the timeframe
        for listind in range(len(timeList)):
            if (currentTime-timeList[len(timeList)-1-listind] <= timeframe):
                inFrame.append(timeList[len(timeList)-1-listind])
        # Indicators
        # Max
        maxTime = self.computeMaxResponseTime(website, inFrame)
        # Avg
        avgTime = self.computeAvgResponsetime(website, inFrame)
        # Availability
        availability = self.computeAvailability(website, inFrame)
        # Status
        status = self.computeStatus(website, currentTime)

        # Alert checking with 120 timeframe
        if (timeframe == 120):
            self.checkForIsDownAlert(website= website, availability= availability)
            self.checkForIsUpAlert(website=website, availability=availability)


        return {'website': website, 'frame': timeframe,'time': currentTime, 'indicators': {'maxTime': maxTime, 'avgTime': avgTime, 'availability': availability, 'status': status}}


    def computeMaxResponseTime(self, website, inFrame):
        """
        Indicator n1
        :param website:
        :param inFrame:
        :return:
        """
        maxTime = 0
        for timeOfReq in inFrame:
            if website.log[timeOfReq]['responseTime'] > timedelta(seconds=maxTime):
                maxTime = self.timedeltaToFloat(website.log[timeOfReq]['responseTime'])
        return maxTime

    def computeAvgResponsetime(self,website, inFrame):
        """
        Indicator n2
        :param website:
        :param inFrame:
        :return:
        """
        avgTime = 0
        for timeOfReq in inFrame:
            avgTime += self.timedeltaToFloat(website.log[timeOfReq]['responseTime'])
        avgTime = avgTime / len(inFrame)
        return avgTime

    def computeAvailability(self, website, inFrame):
        """
        Indicator n3
        :param website:
        :param inFrame:
        :return:
        """
        availability = 0
        for timeReq in inFrame:
            # All 2XX response codes
            if website.log[timeReq]['code'] // 100 == 2:
                availability += 1
        availability = availability / len(inFrame)
        return availability

    def computeStatus(self, website, time):
        """
        Indicator n4, last response status
        :param website:
        :param time:
        :return:
        """
        return website.log[time]['code']

    def checkForIsDownAlert(self, website, availability):
        """
        Check for a isDown Alert.
        :param website:
        :param availability:
        :return:
        """
        checkTime = time.time()
        # Verify that the system has been running for longer than 2 minutes
        if (checkTime-self.originalTime >= 120):
            if availability < 0.8:
                # website already alerted, check if the alert is gone -> value : None
                if website.name in self.alertsDic:
                    if not self.alertsDic[website.name]:
                        alert = {'website': website.name, 'time': time.time(), 'availability': availability, 'status': 'DOWN'}
                        self.alertsDic[website.name] = alert
                        self.mailer.sendAlert(alert)
                        self.queueAlerts.put(alert)
                # no alert for this website before, no check
                else :
                    alert = {'website': website.name, 'time': time.time(), 'availability': availability, 'status': 'DOWN'}
                    self.alertsDic[website.name] = alert
                    self.mailer.sendAlert(alert)
                    self.queueAlerts.put(alert)

        return

    def checkForIsUpAlert(self, website, availability):
        """
        Check for is up Alert
        :param website:
        :param availability:
        :return:
        """
        checkTime = time.time()
        # Verify that the system has been running for longer than 2 minutes
        if (checkTime - self.originalTime >= 120):
            # Verify that the system has been alerted by the site
            if website.name in self.alertsDic:
                # Verify that the UP alert wasn't already sent
                if self.alertsDic[website.name]:
                    if availability > 0.8 :
                        alert = {'website': website.name, 'time': time.time(), 'availability': availability,
                                 'status': 'UP'}
                        self.alertsDic[website.name] = None
                        self.mailer.sendAlert(alert)
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


