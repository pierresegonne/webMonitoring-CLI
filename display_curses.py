import time
import curses
from curses import wrapper
import multiprocessing
from multiprocessing import Process, Queue

import sys
from collections import OrderedDict

import monitor
from data import data_utils
from data import messages as msg

class WebmonitoringCurses(object):

    def __init__(self,username):

        # getting the user
        self.user = data_utils.getUser(username)
        if not self.user:
            print(msg.init_monitoring_usernotfound)
            return

        # queues to transmit data
        self.queueTwoMin = Queue()
        self.queueTenMin = Queue()
        self.queueAlerts = Queue()

        # Dic for displayed data
        self.websitesStats = {}
        for website in self.user.mySites.values():
            self.websitesStats[website.name] = {'description': str(website), 'lastTenMin': None, 'lastHour': None}
        self.websitesStats = OrderedDict(sorted(self.websitesStats.items()))


        # monitoring process
        print('yoyoy')
        # important not to put the args in the function as it would trigger its start
        monit_daemon = Process(target= monitor.startMonitor,
                               args=(self.user, self.queueTwoMin, self.queueTenMin, self.queueAlerts))

        # display process
        print('weq')
        display = Process(target=self.startCurses, args=())

        monit_daemon.start()
        display.start()

        return


    def startCurses(self):
        self.minHeight = 10
        curses.wrapper(self.run)

    def run(self,stdscr):
        k=0
        cursor_x = 0
        cursor_y = 0

        # Set the colors
        self.initcolors()

        # Clear and refresh the screen for a blank canvas
        self.clearScreen(stdscr)

        # Non blocking char
        stdscr.nodelay(True)

        # Time keeper
        self.timekeeper_sec = 0
        self.timekeeper_min = 0

        # Loop where k is the last character pressed
        while (k != ord('q')):

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            if k == curses.KEY_DOWN:
                cursor_y = cursor_y + 1
            elif k == curses.KEY_UP:
                cursor_y = cursor_y - 1
            elif k == curses.KEY_RIGHT:
                cursor_x = cursor_x + 1
            elif k == curses.KEY_LEFT:
                cursor_x = cursor_x - 1

            cursor_x = max(0, cursor_x)
            cursor_x = min(width - 1, cursor_x)

            cursor_y = max(0, cursor_y)
            cursor_y = min(height - 1, cursor_y)

            # Creation of the curses frame
            self.createFrame(stdscr)
            # Addition of the websites names list
            self.addWebsites(stdscr)
            # Addition of the indicators
            self.addIndicators(stdscr)
            # Addition of the stats for each website
            # self.addStats(stdscr)
            # Addition of the alerts
            # self.addAlerts(stdscr)

            # Cursor movement
            stdscr.move(cursor_y, cursor_x)

            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()

            time.sleep(0.05)

            # increment the timekeeper
            self.timekeeper_sec += 0.05

        return


    def initcolors(self):
        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)

        self.ifOK_color = curses.color_pair(6) | curses.A_BOLD
        self.ifWARNING_color = curses.color_pair(7) | curses.A_BOLD
        self.ifCRITICAL_color = curses.color_pair(2) | curses.A_BOLD
        self.ifTitle_color = curses.color_pair(8) | curses.A_BOLD
        self.ifSection_color = curses.color_pair(1)
        self.ifFrame_color = curses.color_pair(4)
        self.ifWebsiteName_color = curses.color_pair(5)
        self.ifFooter_color = curses.color_pair(3)
        self.ifIndicator_color = curses.color_pair(9) | curses.A_BOLD

        self.color_dic = {
            'OK': self.ifOK_color,
            'WARNING': self.ifWARNING_color,
            'CRITICAL': self.ifCRITICAL_color,
            'TITLE': self.ifTitle_color,
            'SECTION': self.ifSection_color,
            'FRAME': self.ifFrame_color,
            'WEBSITENAME': self.ifWebsiteName_color,
            'FOOTER': self.ifFooter_color,
            'INDICATOR': self.ifIndicator_color
        }

    def clearScreen(self, stdscr):
        stdscr.clear()
        stdscr.refresh()

    def createFrame(self, stdscr):
        height, width = stdscr.getmaxyx()
        # Check sufficient height
        if height < self.minHeight:
            sys.exit(msg.window_err_height)
        self.windowTitle_1 = msg.window_title_1[:int(width*0.7)-1]
        self.windowTitle_2 = msg.window_title_2[:int(width*0.7)-1]
        self.windowTitle_3 = msg.window_title_3[:int(width*0.7)-1]
        self.author = msg.window_author[:int(width*0.3)-1]
        self.monitoringTitle = msg.window_monitoring_title[:int(width*0.7)-1]
        self.alertTitle = msg.window_alert_title[:int(width*0.3)-1]
        self.tenMinSection = msg.window_monitoring_tenMin
        self.hourSection = msg.window_monitoring_hour
        self.quitIndicator = msg.window_quit[:width-1]

        # Header footer height
        self.headerHeight = 4
        self.subHeaderHeight = self.headerHeight + 3
        self.footerHeight = 1

        # Position calculations
        # (y,x)
        self.windowTitle_pos = (0,0)
        self.windowAuthor_pos = (0,width-len(self.author)-1)
        self.windowMonitoringTitle_pos = (self.headerHeight,0)
        self.windowAlertTitle_pos = (self.headerHeight,int(width*0.7)+2)
        self.windowTenMinSection_pos = (self.headerHeight,(int(width*0.7)-len(self.monitoringTitle))//2+len(self.monitoringTitle)-len(self.tenMinSection))
        self.windowHourSection_pos = (self.headerHeight,int(width*0.7)-len(self.hourSection))
        self.windowQuitIndicator = (height-self.footerHeight,0)

        # Rendering strings

        # Turning on attributes for title
        stdscr.attron(self.color_dic['TITLE'])
        # Rendering title
        stdscr.addstr(self.windowTitle_pos[0], self.windowTitle_pos[1], self.windowTitle_1)
        stdscr.addstr(self.windowTitle_pos[0]+1, self.windowTitle_pos[1], self.windowTitle_2)
        stdscr.addstr(self.windowTitle_pos[0]+2, self.windowTitle_pos[1], self.windowTitle_3)
        stdscr.addstr(self.windowAuthor_pos[0], self.windowAuthor_pos[1], self.author)
        # Turning off attributes for title
        stdscr.attroff(self.color_dic['TITLE'])

        # Turning on attributes for sections
        stdscr.attron(self.color_dic['SECTION'])
        # Rendering sections
        stdscr.addstr(self.windowMonitoringTitle_pos[0],self.windowMonitoringTitle_pos[1],self.monitoringTitle)
        stdscr.addstr(self.windowAlertTitle_pos[0],self.windowAlertTitle_pos[1], self.alertTitle)
        stdscr.addstr(self.windowTenMinSection_pos[0],self.windowTenMinSection_pos[1], self.tenMinSection)
        stdscr.addstr(self.windowHourSection_pos[0],self.windowHourSection_pos[1], self.hourSection)
        # Turning off attributes for sections
        stdscr.attroff(self.color_dic['SECTION'])

        # Turning on attributes for footer
        stdscr.attron(self.color_dic['FOOTER'])
        # Render footer
        stdscr.addstr(self.windowQuitIndicator[0],self.windowQuitIndicator[1], self.quitIndicator)
        stdscr.addstr(self.windowQuitIndicator[0], len(self.quitIndicator), " " * (width - len(self.quitIndicator) - 1))
        # Turning off attributes for footer
        stdscr.attroff(self.color_dic['FOOTER'])

        # Turning on attributes for framing
        stdscr.attron(self.color_dic['FRAME'])
        # Render frame
        stdscr.addstr(self.headerHeight-1, 0, '-'*(width-1))
        stdscr.addstr(self.subHeaderHeight-1, 0, '-'*(width-1))
        for i in range(self.headerHeight,height-1):
            stdscr.addstr(i, int(width*0.7) + 1, '|')
        for i in range(self.headerHeight,height-1):
            stdscr.addstr(i,len(self.monitoringTitle)+1,'|')
        for i in range(self.headerHeight,height-1):
            stdscr.addstr(i,self.windowTenMinSection_pos[1]+1+len(self.tenMinSection),'|')
        # Turning off attributes for framing
        stdscr.attroff(self.color_dic['FRAME'])
        return

    def addWebsites(self,stdscr):
        height = stdscr.getmaxyx()[0]
        websiteNames = list(self.websitesStats.keys())[:height - (self.subHeaderHeight + self.footerHeight)]
        # Turning on attributes for websites
        stdscr.attron(self.color_dic['WEBSITENAME'])
        # Rendering websites
        indw = 0
        for websiteName in websiteNames:
            stdscr.addstr(self.subHeaderHeight+indw, 0, websiteName[:len(self.monitoringTitle)])
            indw += 1
        # Turning on attributes for websites
        stdscr.attroff(self.color_dic['WEBSITENAME'])
        return

    def addIndicators(self, stdscr):
        width = stdscr.getmaxyx()[1]

        # Turning on attributes for indicators
        stdscr.attron(self.color_dic['INDICATOR'])
        # Rendering indicators
        self.indicators = OrderedDict(sorted(monitor.indicatorsTypes.items()))
        nbrInd = len(self.indicators.keys())
        indWidth = ((int(width * 0.7) - len(self.monitoringTitle)) // 2) // nbrInd
        if indWidth < 4:
            # Check sufficient width
            sys.exit(msg.window_err_width)
        indw = 0
        for indicator in self.indicators.keys():
            stdscr.addstr(self.subHeaderHeight-2, len(self.monitoringTitle)+1 + indWidth*indw + int(
                (indWidth//2)-(len(indicator)//2)-(len(indicator)%2)), indicator)
            stdscr.addstr(self.subHeaderHeight - 2, len(self.monitoringTitle) + 1 + ((int(width * 0.7) - len(self.monitoringTitle)) // 2) + indWidth * indw + int(
                (indWidth // 2) - (len(indicator) // 2) - (len(indicator) % 2)), indicator)
            indw += 1

        # Turning off attributes for indicators
        stdscr.attroff(self.color_dic['INDICATOR'])

    def addStats(self, stdscr):
        # Update of the stats dic
        self.checkTimekeepers()
        # Display
        height = stdscr.getmaxyx()[0]
        websiteNames = list(self.websitesStats.keys())[:height - (self.subHeaderHeight + self.footerHeight)]
        # Turning on attributes for websites
        stdscr.attron(self.color_dic['OK'])
        # Rendering websites
        indw = 0
        # for websiteName in websiteNames:



        return


    def checkTimekeepers(self):
        """
        Checks the values of the timekeepers and calls the update of the stats dic
        :return:
        """
        if self.timekeeper_sec == 10 :
            self.timekeeper_sec = 0
            self.timekeeper_min += 1
            # Both 10 sec and 1min
            if self.timekeeper_min == 6:
                self.timekeeper_min = 0
                self.emptyTenMinQueue()
                self.emptyHourQueue()
                return True
            # Only 10 sec
            else :
                self.emptyTenMinQueue()
                return True
        return False

    def emptyTenMinQueue(self):
        """
        Empties the ten min queue and updates the stats dic
        :return:
        """
        while not self.queueTenMin.empty():
            statTenMin = self.queueTenMin.get()
            self.websitesStats[statTenMin['website'].name]['lastTenMin'] = statTenMin
        return

    def emptyHourQueue(self):
        """
        Empties the hour queue and updates the stats dic
        :return:
        """
        #TODO
        while not self.queueTenMin.empty():
            statTenMin = self.queueTenMin.get()
            self.websitesStats[statTenMin['website'].name]['lastTenMin'] = statTenMin
        return


        # ====================================


    def startCursesTest(self):
        # wrapper is a function that does all of the setup and teardown, and makes sure
        # your program cleans up properly if it errors!
        print('yo dawg')
        # websites
        self.websitesStats = {}
        for website in self.user.mySites.values():
            self.websitesStats[website.name] = {'description': str(website), 'lastTenMin': None}
        # alerts
        self.alerts=[]

        self.startPrinting()
        # for now no curses, let check that the whole systems is working !
        # wrapper(self.draw_menu)


    def startPrinting(self):
        time.sleep(5)
        while True:
            # start time important to make the check regular
            startTime = time.time()
            # 10s
            while not self.queueTenMin.empty():
                statTenMin = self.queueTenMin.get()
                self.websitesStats[statTenMin['website'].name]['lastTenMin'] = statTenMin
            # 1h

            # Alerts
            while not self.queueAlerts.empty():
                alert = self.queueAlerts.get()
                self.alerts.append(alert)
            print('\nAlerts : ')
            print(self.alerts)
            print('Websites : ')
            print(self.websitesStats)
            endTime = time.time()
            time.sleep(10-(endTime-startTime))


