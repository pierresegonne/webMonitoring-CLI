import time
import curses
from curses import wrapper
import multiprocessing
from multiprocessing import Process, Queue
import monitor
from data import data_utils
from data import messages as msg

class WebmonitoringCurses(object):

    hotkeys = {
        'q' : {'quit':'quit'}
    }

    def __init__(self,username):

        self.isTerminated = False

        # getting the user
        self.user = data_utils.getUser(username)
        if not self.user:
            print(msg.init_monitoring_usernotfound)
            return

        # queues to transmit data
        self.queueTwoMin = Queue()
        self.queueTenMin = Queue()
        self.queueAlerts = Queue()

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
        # wrapper is a function that does all of the setup and teardown, and makes sure
        # your program cleans up properly if it errors!
        print('yo dawg')
        wrapper(self.draw_menu)





    def draw_menu(self,stdscr):
        k = 0
        cursor_x = 0
        cursor_y = 0

        # Clear and refresh the screen for a blank canvas
        stdscr.clear()
        stdscr.refresh()

        # Start colors in curses
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

        # Loop where k is the last character pressed
        while (k != ord('q')):

            #refresh counter
            refresh_counter = 0

            # Initialization
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # if k == curses.KEY_DOWN:
            #     cursor_y = cursor_y + 1
            # elif k == curses.KEY_UP:
            #     cursor_y = cursor_y - 1
            # elif k == curses.KEY_RIGHT:
            #     cursor_x = cursor_x + 1
            # elif k == curses.KEY_LEFT:
            #     cursor_x = cursor_x - 1
            #
            # cursor_x = max(0, cursor_x)
            # cursor_x = min(width-1, cursor_x)
            #
            # cursor_y = max(0, cursor_y)
            # cursor_y = min(height-1, cursor_y)

            # Invisible cursor
            curses.curs_set(0)

            # Declaration of strings
            mainTitle = "My Websites"[:width-1]
            alertTitle = "Alerts"[:width-1]
            # subtitle = "Written by Clay McLeod"[:width-1]
            # keystr = "Last key pressed: {}".format(k)[:width-1]
            statusbarstr = "Press 'q' to exit | STATUS BAR | Pos: {}, {}".format(cursor_x, cursor_y)
            if k == 0:
                keystr = "No key press detected..."[:width-1]

            # pads
            main_pad = curses.newpad(len(self.user.mySites.keys())*2+2, 2)
            alert_pad = curses.newpad(3,1)

            #borders of the pad
            main_pad.box()
            alert_pad.box()

            # Position of the pads
            # Main
            pminrow_main = 1
            pmincol_main = 0
            sminrow_main = 1
            smincol_main = 0
            smaxrow_main = height-1
            smaxcol_main = int((width * 0.7))-1
            main_pad.refresh(pminrow_main, pmincol_main, sminrow_main, smincol_main, smaxrow_main, smaxcol_main)
            # Alert
            pminrow_alert = 1
            pmincol_alert = int((width * 0.7))
            sminrow_alert = 1
            smincol_alert = int((width * 0.7))
            smaxrow_alert = height-1
            smaxcol_alert = width
            alert_pad.refresh(pminrow_alert, pmincol_alert, sminrow_alert, smincol_alert, smaxrow_alert, smaxcol_alert)

            # Centering calculations
            start_x_mainTitle = 0
            start_x_alertTitle = int((width * 0.7))
            #start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
            start_y = 0

            # Rendering some text
            #whstr = "Width: {}, Height: {}".format(width, height)
            #stdscr.addstr(0, 0, whstr, curses.color_pair(1))

            # Render status bar
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(height-1, 0, statusbarstr)
            stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
            stdscr.attroff(curses.color_pair(3))

            # Turning on attributes for title
            stdscr.attron(curses.color_pair(2))
            stdscr.attron(curses.A_BOLD)

            # Rendering title
            stdscr.addstr(start_y, start_x_mainTitle, mainTitle)

            # Turning off attributes for title
            stdscr.attroff(curses.color_pair(2))
            stdscr.attroff(curses.A_BOLD)

            # Turning on attributes for alerts
            stdscr.attron(curses.color_pair(1))
            stdscr.attron(curses.A_BOLD)

            # Print rest of text
            stdscr.addstr(start_y, start_x_alertTitle, alertTitle)
            # stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
            # stdscr.addstr(start_y + 5, start_x_keystr, keystr)
            # stdscr.move(cursor_y, cursor_x)

            # Turning off attributes for the rest
            stdscr.attroff(curses.color_pair(1))
            stdscr.attroff(curses.A_BOLD)

            # Refresh the screen
            stdscr.refresh()

            # refresh counter increases
            refresh_counter += 1

            # sleep for 10sec
            # time.sleep(10)

            # Wait for next input
            k = stdscr.getch()






