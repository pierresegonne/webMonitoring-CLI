import requests
import urllib.request
import curses
import sys
import time
import multiprocessing
import _pickle as pickle
from multiprocessing import Process, Queue
import random

from urllib.parse import urlparse

def main():

    req = requests.get('https://tutorialedge.net/python/python-multiprocessing-tutorial/')
    print(type(req.status_code))
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
    p = multiprocessing.current_process()
    print('Starting:', p.name, p.pid)
    sys.stdout.flush()
    dicT = {}
    time.sleep(0)
    while True:
        timeC = time.time()
        print('daemon running')
        dicT[timeC] = timeC
        writepkl(dicT)
        sys.stdout.flush()
        time.sleep(1)
    print('Exiting :', p.name, p.pid)
    sys.stdout.flush()

def non_daemon():
    p = multiprocessing.current_process()
    print('Starting:', p.name, p.pid)
    while True:
        print('non-daemon running')
        print(readpkl())
        sys.stdout.flush()
        print(testcounter)
        time.sleep(2)

    print('Exiting :', p.name, p.pid)
    sys.stdout.flush()

path = 'test.pkl'
def writepkl(data,path=path):
    with open(path, 'wb') as serializer:
        pickle.dump(data, serializer, -1)

def readpkl(path=path):
    try :
        with open(path, 'rb') as reader:
            return pickle.load(reader)
    except FileNotFoundError:
        return {}

def rand_num(queue):
    num = random.random()
    queue.put(num)

if __name__=='__main__':
    main()

    queue = Queue()

    processes = [Process(target=rand_num, args=(queue,)) for x in range(12)]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    results = [queue.get() for p in processes]

    print(results)

    d = multiprocessing.Process(name='daemon', target=daemon)
    d.daemon = True

    n = multiprocessing.Process(name='non-daemon', target=non_daemon)
    n.daemon = False

    d.start()
    time.sleep(2)
    n.start()
    d.join()

