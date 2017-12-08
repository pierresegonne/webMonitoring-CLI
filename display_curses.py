import time
import curses
from multiprocessing import Process, Queue

import sys
from collections import OrderedDict

import monitor
from data import data_utils
from data import messages as msg

class WebmonitoringCurses(object):
    """Class that handles all the display of the application
    From initializing built-in curses
    To refreshing the screen (until q is pressed)
    To positioning the data on the screen

    Note : The data comes from multiprocessing queues
    """

    def __init__(self,username):
        """
        Is called when the monitor argument is passed on main
        :param username:
        """

        # Getting the user - MUST EXIST
        self.user = data_utils.getUser(username)
        if not self.user:
            print(msg.init_monitoring_usernotfound)
            return

        # Queues to transmit data
        self.queueTwoMin = Queue()
        self.queueTenMin = Queue()
        self.queueHour = Queue()
        self.queueAlerts = Queue()

        # Queue to end
        self.queueTermination = Queue()

        # Dic for displayed data
        # key : website name | value : {description : str, lastTenMinute : {}, lastHour: {} }
        # Ordered alphabetically to map stats to website name more easily
        self.websitesStats = {}
        for website in self.user.mySites.values():
            self.websitesStats[website.name] = {'description': str(website), 'lastTenMin': None, 'lastHour': None}
        self.websitesStats = OrderedDict(sorted(self.websitesStats.items()))

        # List of Alerts
        self.displayedAlerts = []


        # Monitoring process
        # Important not to put the args in the function as it would trigger its start
        self.monit_daemon = Process(target= monitor.startMonitor,
                               args=(self.user, self.queueTwoMin, self.queueTenMin, self.queueHour, self.queueAlerts, self.queueTermination))

        # Display process
        display = Process(target=self.startCurses, args=())

        # START
        self.monit_daemon.start()
        display.start()


        return


    def startCurses(self):
        """
        Wraps the curses display
        And once cur3ses is exited through q, terminates monitoring
        :return:
        """
        # Wrapper for curses to render functionnal terminal if there is an issue
        curses.wrapper(self.run)
        # Terminate the monitoring process
        self._terminateMonitoring()

    def _terminateMonitoring(self):
        """
        Termination of all processes and subprocesses,
        That would go on running in background
        Trough the use of a queue to indicate to the child processes that they should stop
        :return:
        """
        # Put termination message in the queue
        self.queueTermination.put({'msg': 'terminate'})
        print(msg.curses_goodbye_1)
        print(msg.curses_goodbye_2)
        print(msg.curses_goodbye_3)
        print(msg.curses_goodbye_4)
        # Terminate the parent monitoring process
        self.monit_daemon.terminate()

    def run(self, stdscr):
        """
        Curses loop
        Non blocking inputs, which mean that curses doesn't wait for the user imput
        And iterates through the loop. This allow to refresh the screen every 0.5 sec
        STDSCR is the screen
        :param stdscr:
        :return:
        """

        # Cursor, Opt
        k=0
        cursor_x = 0
        cursor_y = 0


        # Set the colors
        self.initcolors()

        # Clear and refresh the screen for a blank canvas
        self.clearScreen(stdscr)

        # Non blocking char
        stdscr.nodelay(True)

        # No display of the cursor can raise an exception
        try:
            curses.curs_set(0)
        except Exception:
            print(msg.curses_cursor_inv)

        # Time keeper - allows to know when to refresh the stats
        self.timekeeper_sec = 0
        self.timekeeper_min = 0

        # Loop where k is the last character pressed
        while (k != ord('q')):

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Cursor movement, Opt
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
            self.addStats(stdscr)
            # Addition of the alerts
            self.addAlerts(stdscr)

            # Cursor movement, Opt
            stdscr.move(cursor_y, cursor_x)

            # Refresh the screen
            stdscr.refresh()

            # Wait for next input
            k = stdscr.getch()

            # Large refresh time to prevent visible screen refreshes, can be reduced if the cursor is to be used
            time.sleep(0.5)

            # increment the timekeeper
            self.timekeeper_sec += 0.5

        return


    def initcolors(self):
        """
        Define all colors for the display and store them in a dic
        :return:
        """
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
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(11, curses.COLOR_BLUE, curses.COLOR_WHITE)

        self.ifOK_color = curses.color_pair(6) | curses.A_BOLD
        self.ifWARNING_color = curses.color_pair(7) | curses.A_BOLD
        self.ifCRITICAL_color = curses.color_pair(2) | curses.A_BOLD
        self.ifTitle_color = curses.color_pair(8) | curses.A_BOLD
        self.ifSection_color = curses.color_pair(1)
        self.ifFrame_color = curses.color_pair(4)
        self.ifWebsiteName_color = curses.color_pair(8)
        self.ifFooter_color = curses.color_pair(3)
        self.ifIndicator_color = curses.color_pair(9) | curses.A_BOLD
        self.ifSpecial_color = curses.color_pair(5) | curses.A_BOLD
        self.ifDefault_color = curses.color_pair(10) | curses.A_BOLD

        self.color_dic = {
            'OK': self.ifOK_color,
            'WARNING': self.ifWARNING_color,
            'CRITICAL': self.ifCRITICAL_color,
            'TITLE': self.ifTitle_color,
            'SECTION': self.ifSection_color,
            'FRAME': self.ifFrame_color,
            'WEBSITENAME': self.ifWebsiteName_color,
            'FOOTER': self.ifFooter_color,
            'INDICATOR': self.ifIndicator_color,
            'SPECIAL': self.ifSpecial_color,
            'DEFAULT': self.ifDefault_color
        }

    def clearScreen(self, stdscr):
        """
        Clears the screen
        :param stdscr:
        :return:
        """
        stdscr.clear()
        stdscr.refresh()

    def createFrame(self, stdscr):
        """
        Creation of the frame, be it the general structure,
        Title and sections = Everything that is not dependant
        On the user data
        :param stdscr:
        :return:
        """
        height, width = stdscr.getmaxyx()
        # Check sufficient height
        self.minHeight = 9
        if height < self.minHeight:
            self._terminateMonitoring()
            sys.exit(msg.window_err_height)

        # Titles and fixed elements
        self.windowTitle_1 = msg.window_title_1[:width-len(msg.window_author)-1]
        self.windowTitle_2 = msg.window_title_2[:width-len(msg.window_author)-1]
        self.windowTitle_3 = msg.window_title_3[:width-len(msg.window_author)-1]
        self.windowTitle_4 = msg.window_title_4[:width-len(msg.window_author)-1]
        self.author = msg.window_author[:int(width*0.3)-1]
        self.monitoringTitle = msg.window_monitoring_title[:int(width*0.7)-1]
        self.alertTitle = msg.window_alert_title[:int(width*0.3)-1]
        self.tenMinSection = msg.window_monitoring_tenMin
        self.hourSection = msg.window_monitoring_hour
        self.quitIndicator = msg.window_quit[:width-1]

        # Header footer height
        self.headerHeight = 5
        self.subHeaderHeight = self.headerHeight + 3
        self.footerHeight = 1


        # Position calculations
        # (y,x) for curses, starting from the top left corner
        self.windowTitle_pos = (0,0)
        self.windowAuthor_pos = (0,width-len(self.author)-1)
        self.windowMonitoringTitle_pos = (self.headerHeight,0)
        self.windowAlertTitle_pos = (self.headerHeight,int(width*0.7)+2)
        self.windowTenMinSection_pos = (self.headerHeight,(int(width*0.7)-6-len(self.monitoringTitle))//2+len(self.monitoringTitle)-len(self.tenMinSection))
        self.windowHourSection_pos = (self.headerHeight,int(width*0.7)-6-len(self.hourSection))
        self.windowQuitIndicator = (height-self.footerHeight,0)

        # Rendering fields =======

        # Turning on attributes for title
        stdscr.attron(self.color_dic['TITLE'])
        # Rendering title
        stdscr.addstr(self.windowTitle_pos[0], self.windowTitle_pos[1], self.windowTitle_1)
        stdscr.addstr(self.windowTitle_pos[0]+1, self.windowTitle_pos[1], self.windowTitle_2)
        stdscr.addstr(self.windowTitle_pos[0]+2, self.windowTitle_pos[1], self.windowTitle_3)
        stdscr.addstr(self.windowTitle_pos[0]+3, self.windowTitle_pos[1], self.windowTitle_4)
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
        for i in range(self.headerHeight,height-1):
            stdscr.addstr(i,self.windowHourSection_pos[1]+1+len(self.hourSection),'|')
        # Turning off attributes for framing
        stdscr.attroff(self.color_dic['FRAME'])
        return

    def addWebsites(self,stdscr):
        """
        Add the websitesNames to the display,
        Ordered in alphabetical order, are only displayed the sites that fit into
        The window
        :param stdscr:
        :return:
        """
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
        """
        Add the indicators names to the display,
        Truncate them if necessary and place them
        :param stdscr:
        :return:
        """
        height, width = stdscr.getmaxyx()

        # Turning on attributes for indicators
        stdscr.attron(self.color_dic['INDICATOR'])
        # Rendering indicators
        self.indicators = OrderedDict(sorted(monitor.indicatorsTypes.items()))
        nbrInd = len(self.indicators.keys())

        # Check sufficient width
        self.indWidth = ((int(width * 0.7) - 6 - len(self.monitoringTitle)) // 2) // (nbrInd-1)
        if self.indWidth < 4:
            self._terminateMonitoring()
            sys.exit(msg.window_err_width)

        # Placing indicators
        indw = 0
        for indicator in self.indicators.keys():
            # Computed
            if (indicator != 'STA') :
                stdscr.addstr(self.subHeaderHeight-2, len(self.monitoringTitle)+1 + self.indWidth*indw + int(
                    (self.indWidth//2)-(len(indicator)//2)-(len(indicator)%2)), indicator)
                stdscr.addstr(self.subHeaderHeight - 2, len(self.monitoringTitle) + 1 + ((int(width * 0.7) - len(self.monitoringTitle)) // 2) + self.indWidth * indw + int(
                    (self.indWidth // 2) - (len(indicator) // 2) - (len(indicator) % 2)), indicator)
                indw += 1
            # Status
            else:
                stdscr.addstr(self.subHeaderHeight-2, int(width*0.7)-3, indicator)

        # Turning off attributes for indicators
        stdscr.attroff(self.color_dic['INDICATOR'])

        # Legend

        # Turning on attributes for legend
        stdscr.attron(self.color_dic['FOOTER'])

        # Placing legends

        # width for legends
        indWidth_legends = (width - len(msg.window_quit)) // nbrInd
        indw = 0
        for indicator in self.indicators.keys():
            legend_indicator = '| ' + indicator + '=' + self.indicators[indicator][:indWidth_legends]
            stdscr.addstr(height-self.footerHeight, len(msg.window_quit) + indw*indWidth_legends, legend_indicator)
            indw += 1

        # Turning off attributes for legend
        stdscr.attroff(self.color_dic['FOOTER'])
        return

    def addStats(self, stdscr):
        """
        Add all of the latest stats to the screen
        :param stdscr:
        :return:
        """

        # Update of the stats dic
        self.checkTimekeepers()

        # Display - take only the websites that will fit in the screen
        height, width = stdscr.getmaxyx()
        websiteNames = list(self.websitesStats.keys())[:height - (self.subHeaderHeight + self.footerHeight)]

        # Rendering websites
        indweb = 0
        for websiteName in websiteNames:

            indwidth = 0
            # 10 Min
            for indicator in list(self.indicators.values()):
                # Only Computed
                if indicator != 'status':
                    if self.websitesStats[websiteName]['lastTenMin']:
                        # Get the value of the indicator from the sites stats which has the sub object lastenMin, which has the sub object indicators
                        indicator_val = self.websitesStats[websiteName]['lastTenMin']['indicators'][indicator]
                        # Only 2 digits after the decimal point
                        indicator_val = round(indicator_val, 2)
                        # Truncated str
                        indicator_val = str(indicator_val)[:self.indWidth]
                    else :
                        indicator_val = msg.window_default_stat
                    attrCode = self.turnOnAttrStat(stdscr, indicator, indicator_val)
                    stdscr.addstr(self.subHeaderHeight+indweb, len(self.monitoringTitle)+1 + self.indWidth*indwidth + int(
                    (self.indWidth//2)-(len(indicator_val)//2)-(len(indicator_val)%2)),indicator_val)
                    self.turnOffAttr(stdscr, attrCode)
                    indwidth += 1


            indwidth = 0
            # 1 Hour
            for indicator in list(self.indicators.values()):
                # Only Computed
                if indicator != 'status':
                    if self.websitesStats[websiteName]['lastHour']:
                        # Get the value of the indicator from the sites stats which has the sub object lasHour, which has the sub object indicators
                        indicator_val = self.websitesStats[websiteName]['lastHour']['indicators'][indicator]
                        # Only 2 digits after the decimal point
                        indicator_val = round(indicator_val, 2)
                        # Truncated str
                        indicator_val = str(indicator_val)[:self.indWidth]
                    else :
                        indicator_val = msg.window_default_stat
                    attrCode = self.turnOnAttrStat(stdscr, indicator, indicator_val)
                    stdscr.addstr(self.subHeaderHeight+indweb, len(self.monitoringTitle) + 1 + ((int(width * 0.7) - len(self.monitoringTitle)) // 2) + self.indWidth * indwidth + int(
                    (self.indWidth // 2) - (len(indicator_val) // 2) - (len(indicator_val) % 2)), indicator_val)
                    self.turnOffAttr(stdscr, attrCode)
                    indwidth += 1

            # Status
            indicator = 'status'
            if self.websitesStats[websiteName]['lastTenMin']:

                # Get the status from the last 10 sec refresh
                # Always XXX so no truncating
                status_val = str(self.websitesStats[websiteName]['lastTenMin']['indicators']['status'])
            else :
                status_val = msg.window_default_stat
            attrCode = self.turnOnAttrStat(stdscr, indicator, status_val)
            stdscr.addstr(self.subHeaderHeight + indweb, int(width * 0.7) - 3, status_val)
            self.turnOffAttr(stdscr, attrCode)


            indweb += 1
        return


    def addAlerts(self, stdscr):
        """
        Add alerts to the window
        :param stdscr:
        :return:
        """
        height, width = stdscr.getmaxyx()
        # Empty the alerts queue and thus get all the alerts
        self.emptyAlertsQueue()

        # Alerts depending on the size of the screen
        alerts = self.displayedAlerts[:height - (self.subHeaderHeight + self.footerHeight)]

        # Rendering alerts
        inda = 0
        for alert in alerts:
            attrCode = self.turnOnAttrAlert(stdscr, alert['status'])
            # Stylized alert msg
            alertMessage = msg.alert2string(alert)[:int(width*0.3)-1]
            stdscr.addstr(height-2-inda, int(width*0.7)+2, alertMessage)
            self.turnOffAttr(stdscr, attrCode)
            inda += 1
        return


    def checkTimekeepers(self):
        """
        Checks the values of the timekeepers and calls the update of the stats dic
        :return:
        """

        if self.timekeeper_sec >= 10 :
            self.timekeeper_sec = 0
            self.timekeeper_min += 1
            # Both 10 sec and 1min
            if self.timekeeper_min >= 6:
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
        while not self.queueHour.empty():
            statHour = self.queueHour.get()
            self.websitesStats[statHour['website'].name]['lastHour'] = statHour
        return

    def emptyAlertsQueue(self):
        """
        Empties the alert queue and updates the alerts list
        Newest alerts are inserted at the beginning of the list
        To make it easier to display only the latest
        :return:
        """
        while not self.queueAlerts.empty():
            self.displayedAlerts.insert(0,self.queueAlerts.get())
        return


    def turnOnAttrStat(self, stdscr, indicator, indicator_val):
        """
        Turn on attributes for the stats,
        Colors and fonts weight
        :param stdscr:
        :param indicator:
        :param indicator_val:
        :return:
        """

        # Initialization
        if indicator_val == msg.window_default_stat:
            stdscr.attron(self.color_dic['DEFAULT'])
            return ('DEFAULT')
        else :

            # AVAILABILITY
            if indicator == 'availability':
                if 0.95 <= float(indicator_val) :
                    stdscr.attron(self.color_dic['OK'])
                    return ('OK')
                if 0.80 < float(indicator_val) < 0.95:
                    stdscr.attron(self.color_dic['WARNING'])
                    return ('WARNING')
                if 0.80 >= float(indicator_val):
                    stdscr.attron(self.color_dic['CRITICAL'])
                    return ('CRITICAL')
            # STATUS
            elif indicator == 'status':
                if str(indicator_val)[0] == '2':
                    stdscr.attron(self.color_dic['OK'])
                    return ('OK')
                elif str(indicator_val)[0] == '4':
                    stdscr.attron(self.color_dic['CRITICAL'])
                    return ('CRITICAL')
                else :
                    stdscr.attron(self.color_dic['SPECIAL'])
                    return ('SPECIAL')

            # DEFAULT
            else :
                stdscr.attron(self.color_dic['DEFAULT'])
                return ('DEFAULT')

    def turnOnAttrAlert(self, stdscr, status):
        """
        Turn on attributes for the alerts messages,
        Colors and fonts weight
        :param stdscr:
        :param status:
        :return:
        """
        if status == 'UP':
            stdscr.attron(self.color_dic['OK'])
            return ('OK')
        if status == 'DOWN':
            stdscr.attron(self.color_dic['CRITICAL'])
            return ('CRITICAL')

    def turnOffAttr(self, stdscr, attrCode):
        """
        Turns off attribute, based on the attrcode returned by the turn on method
        :param stdscr:
        :param attrCode:
        :return:
        """
        stdscr.attroff(self.color_dic[attrCode])
        return

# ====================================