# output the queried filings to a query.csv

import pandas as pd

database_name = "edgar_htm_idx.dta"
database = pd.read_stata(database_name)
print("There are a total of {} entries of filing links".format(str(len(database))))
print("Note: these are not document links, but filing links.")

# dropping the useless 'index' column
database.drop(columns = ['index'],inplace=True)

# output what you want to query.csv

print("Try 1000 first before the entire database")
print("Depending on the conditions, downloading 1 filing can take up to 30 seconds")
database.head(1000).to_csv("query.csv")

# uncomment this line below to create a csv that queries the entire database downloaded
# database.to_csv("query.csv") 
