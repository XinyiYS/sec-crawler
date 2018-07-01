import os
import sklearn
import pandas as pd
import numpy as np


# csv = "Database files/2017-QTR1.csv"
# csv = "Database files/2017-QTR4.csv"
# csv = "Database files/2018-QTR1.csv"

# print(os.listdir("Database files"))
# for path in os.listdir("Database files"):
# 	df =  pd.read_csv(os.path.join("Database files",path))
# 	subdf = df[ ( df['filing'].str.contains("Q") & df['filing'].str.contains("10") )]
# 	subdf.to_csv('10Q.csv')
# 	size = os.path.getsize("10Q.csv")
# 	print("size of {} is {}".format(str(path),str(size)))
import re

directory = "/Volumes/SSD/"

# print(os.listdir("Downloaded data files"))

a = 123
regex = re.compile(str(a)+ " "+"123")
regexp = re.compile("Item 8\\.")
print(regexp.search("Item 8.asdasd").group())



# a = ("a","a")
# b = ("b","a")
# print(set(a).issubset(b))
