import os
import PySimpleGUI as sg
from PIL import Image
from io import BytesIO
import time
import threading

def t1():
    for i in range(10):
        print('线程1执行中。。。')
        time.sleep(1.5)

def t2():
    for i in range(10):
        print('2号线程执行中>>>>>')
        time.sleep(1.5)

thread1 = threading.Thread(target=t1)
thread1.daemon = True
thread1.tag = '1号'

thread2 = threading.Thread(target=t2)
thread2.daemon = True
thread2.tag = '2号'

thread1.start()
thread2.start()

print(threading.enumerate())

while True:
    for t in threading.enumerate():
        if 't1' in t.name:
            print(t.tag)
            print(t.name)
    time.sleep(3)