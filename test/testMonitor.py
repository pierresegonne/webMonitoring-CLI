import unittest
import monitor
import user
import website
from multiprocessing import Queue, Process
import time



class TestMonitor(unittest.TestCase):


    def testAlerting(self):
        
        # Adapt the user to an existing user
        username = 'joe'
        usr = user.User(username)
        testSite = website.Website(name='test', url='https://support.google.com/merchants/answer/160038?hl=en')
        usr.mySites['test'] = testSite
        print(usr)
        
        #Queues 
        queueTwoMin = Queue()
        queueTenMin = Queue()
        queueHour = Queue()
        queueAlerts = Queue()

        # Triggers the monitoring
        testProcess = Process(target=monitor.startMonitor, args=(usr, queueTwoMin, queueTenMin, queueHour, queueAlerts))
        testProcess.start()

        # Wait for some time
        print('Waiting a bit…')
        print(str(usr.mySites['test']))
        time.sleep(120)

        # End the process
        testProcess.terminate()

        # Put invalid url in the sites
        websitename = list(usr.mySites.keys())[0]
        usr.mySites[websitename].url = 'https://support.google.com/answer/160038?hl=en'
        print(str(usr.mySites[websitename]))

        # Retriggers the monitoring
        testProcess = Process(target=monitor.startMonitor, args=(usr, queueTwoMin, queueTenMin, queueHour, queueAlerts))
        testProcess.start()

        # Wait for some time
        print('Waiting for the alert DOWN to come up')
        time.sleep(200)

        # End the process
        testProcess.terminate()

        # Get the Alert down - Make it possible to raise the up alert
        # Up alerts can't be raised if a down alert is not present in the alertDic
        alertDown = queueAlerts.get()
        testDic = {'test':alertDown}
        queueAlerts.put(alertDown)

        # Put valid url in the sites
        usr.mySites[websitename].url = 'https://support.google.com/merchants/answer/160038?hl=en'
        print(str(usr.mySites[websitename]))

        # Retriggers the monitoring
        testProcess = Process(target=monitor.startMonitor, args=(usr, queueTwoMin, queueTenMin, queueHour, queueAlerts, testDic))
        testProcess.start()

        # Wait for some time
        print('Waiting for the alert UP to come up')
        time.sleep(300)

        # End the process
        testProcess.terminate()

        # Get all the alerts triggered
        alertsTriggered = []
        testAlerts = []
        while not queueAlerts.empty():
            alertsTriggered.insert(0,queueAlerts.get())

        # Get all the alerts tested, there may be some more
        for alert in alertsTriggered:
            if alert['website'] == websitename:
                testAlerts.append(alert)

        # Get the Status of the alerts tested
        statusTestedAlerts = []
        for alert in testAlerts:
            statusTestedAlerts.append(alert['status'])

        print(alertsTriggered)
        print(testAlerts)

        # Assertions - Only 2 alerts, one up one down
        self.assertEqual(len(testAlerts), 2)
        self.assertTrue('UP' in statusTestedAlerts)
        self.assertTrue('DOWN' in statusTestedAlerts)




if __name__ == '__main__':
    unittest.main()