import datetime
import numpy as np 
import pandas as pd 

csv  = "Database files/2018-QTR1 to 2018-QTR2.csv"

df = pd.read_csv(csv)

import time


s = time.time()

# for i in range(100):
sub = df[df['cik']== 1084869] 






print(time.time()-s)
