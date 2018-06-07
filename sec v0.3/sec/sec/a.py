import pandas as pd 
from re import search
import os
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool 


database_folder = "Database files"
df = pd.read_csv(database_folder+ "/2016-QTR1 to 2018-QTR2.csv",chunksize = 100000)

# for chunk in df:
	# print(len(chunk))
	# break

import datetime
a = datetime.timedelta(seconds=100000)
print(a)


exit()




from multiprocessing import Process
import os,time

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f(name,name1):
    info('function f')
    print('hello', name,name1)


def m(a):
	print(a)

if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=['bob','bob'])
    p.start()
    while(time.sleep(3)):
    	pass

    p.join()