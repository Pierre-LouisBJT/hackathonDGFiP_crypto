"""
Init script, so the app is up and running
"""

import pandas as pd
import os 

#create an instance of dataframe
d = {'Address' : ['0x1259b2a159b63f918239dFE6E8674e9ab7B705f9'], 'Flag':['Aucun'], 'Notes':['Adresse réeele utilée en test, cf https://etherscan.io/address/0x1259b2a159b63f918239dfe6e8674e9ab7b705f9']}
df = pd.DataFrame(data=d)

#create a database file in the /data directory
os.makedirs('./data', exist_ok=True)  
df.to_csv('./data/db_proprietary.csv')

#check if the transaction folder exists
os.makedirs('./data/transactions', exist_ok=True)  

print('--- Init OK ---')