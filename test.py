import requests
import urllib.request
import curses
import sys
import time
import multiprocessing

from urllib.parse import urlparse

def main():

    dicTime = {}
    timea = time.time()
    dicTime[timea] = 1
    time.sleep(2)
    timeb = time.time()
    dicTime[timeb] = 2
    print(timeb-timea)
    print(dicTime.keys())
    print(list(dicTime.keys())[0])


    for timeEx in dicTime:
        print(timeEx)




def checkUrl(url):
    acceptedSchemesUrls = ['http','https']
    objUrl = urlparse(url)
    return (objUrl.scheme in acceptedSchemesUrls)
testcounter = 0

def daemon():
    global testcounter
    p = multiprocessing.current_process()
    print('Starting:', p.name, p.pid)
    sys.stdout.flush()
    time.sleep(0)
    while True:
        testcounter += 1
        print('daemon running')
        sys.stdout.flush()
        time.sleep(1)
    print('Exiting :', p.name, p.pid)
    sys.stdout.flush()

def non_daemon():
    p = multiprocessing.current_process()
    print('Starting:', p.name, p.pid)
    while True:
        print('non-daemon running')
        sys.stdout.flush()
        print(testcounter)
        time.sleep(2)

    print('Exiting :', p.name, p.pid)
    sys.stdout.flush()

if __name__=='__main__':
    main()

    # d = multiprocessing.Process(name='daemon', target=daemon)
    # d.daemon = True
    #
    # n = multiprocessing.Process(name='non-daemon', target=non_daemon)
    # n.daemon = False
    #
    # d.start()
    # time.sleep(2)
    # n.start()

