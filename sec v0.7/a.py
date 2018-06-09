import datetime
import numpy as np 
import pandas as pd


path  = "Database files/2017-QTR1.csv"

df = pd.read_csv(path)

print((df.loc[df['index'].isin([-1])]).count())



# print(count)
# print(df.head())


