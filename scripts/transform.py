# Transform raw .csv from covid dataset to json for elasticsearch

# You can index multiple documents in bulk with JSON like:
"""
{"index":{"_id":"1"}}
{"account_number":1,"balance":39225,"firstname":"Amber","lastname":"Duke","age":32,"gender":"M","address":"880 Holmes Lane","employer":"Pyrami","email":"amberduke@pyrami.com","city":"Brogan","state":"IL"}
{"index":{"_id":"6"}}
{"account_number":6,"balance":5686,"firstname":"Hattie","lastname":"Bond","age":36,"gender":"M","address":"671 Bristol Street","employer":"Netagy","email":"hattiebond@netagy.com","city":"Dante","state":"TN"}
"""
# where "_id" are unique integers as strings

"""
To facilitate easily adding entries for every new day, structure json as:
{"index":{"_id:":1"}} // day 1
{"province/state country/region": [date, province/state, country/region, lat, lon, confirmed, deaths, recovered], "province/state country/region 2" [...]}
{"index":{"_id:":2"}} // day 2
{"province/state country/region": [date, province/state, country/region, lat, lon, confirmed, deaths, recovered], "province/state country/region 2" [...]}

Note: some values could be null. 

"""

"""
PUT my_index
{
  "mappings": {
    "properties": {
      "area": {
        "type": "nested" 
      }
    }
  }
}

PUT my_index/_doc/1
{
  "area" : [
    {
      "first" : "John",
      "last" :  "Smith"
    },
    {
      "first" : "Alice",
      "last" :  "White"
    }
  ]
}
"""

import csv
import pandas as pd
import numpy as np
import json
import os 
import logging 
from datetime import timedelta, date
import tqdm as tqdm

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger('transform')

csvs = []
jsons = []

"""
def read_csv(csv_path: str) -> csv.DictReader:
	if not os.path.exists(csv_path):
		log.Error("Invalid path to csv")
		return None
	
	return csv.DictReader(open(csv_path))
"""	
	
def get_csv(csv_path: str) -> pd.DataFrame:
	if not os.path.exists(csv_path):
		log.error("Invalid path to csv")
		return None
	
	return pd.read_csv(csv_path)
	

"""
def write_json(csv: csv.DictReader, json_path: str) -> bool:	
	

csvfile = open('file.csv', 'r')
jsonfile = open('file.json', 'w')

fieldnames = ("FirstName","LastName","IDNumber","Message")
reader = csv.DictReader( csvfile, fieldnames)
for row in reader:
    json.dump(row, jsonfile)
    jsonfile.write('\n')
"""

csvs = [None]*3
work_dir = os.path.join(os.getcwd(), 'extracted')
csvs_to_read = [os.path.join(work_dir, f) for f in os.listdir(work_dir)]

for f in csvs_to_read:
	if f.endswith('confirmed.csv'):
		csvs[0] = get_csv(f)
	elif f.endswith('deaths.csv'):
		csvs[1] = get_csv(f)
	else:
		csvs[2] = get_csv(f)
		
#print(csvs[0])
#print(csvs[1])

#print('Afghanistan' in csvs[0]['Country/Region'].values)  # True 

#print([(x, type(x)) for x in csvs[0]['Province/State'].values]) 

# math.isnan(x) checks if x is a float('nan')

def make_area_key(row) -> str:
	"""
	row: pandas dataframe row of COVID data, with cols 'Province/State' and 'Country/Region'
	
	returns: key as function of province/state and country/region
	"""
	province = row['Province/State']
	if isinstance(province, float): province = ''
	region = row['Country/Region']
	return province + '_' + region

big = pd.concat(csvs)
#print(big)

#print(big.groupby(['Country/Region']).head())
#print(big.groupby(['Province/State']).head())

# Create set of area keys
area_keys = []

for _, row in big.iterrows():
	area_keys.append(make_area_key(row))
	
#print(len(area_keys))
#print(area_keys)



def daterange(start_date, end_date):
	"""
	start_date: start date of range as datetime.date() object
	end_date: end date ""
	
	Is a generator.
	"""
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

date_keys = set()
start_date = date(2020, 1, 22)
end_date = date.today() 

# Includes up to and including yesterday's data
for day in daterange(start_date, end_date):
	date_keys.add(day.strftime("%-m/%d/%y"))
	
""" TODO: Handle cases where data is not up to date. """
# Create dictionary of dictionaries that will be written as json

json_dict = {}

# Create dictionary of prov/state, country/region for each area key for caching
area_lookup = {}
area_id = 0
for area_key in area_keys:
	prov_state, country_reg = area_key.split('_') 
	if len(prov_state) == 0: prov_state = float('nan') 
	""" TODO: check if setting null prov_state to float('nan') makes corresponding json value null """
	""" UPdate: apparently None in python maps to null in json """
	area_lookup[area_key] = (prov_state, country_reg, area_id)
	area_id += 1

# each document has key of date,
# and in each document are [number of areas] keys, each with their info for the day




# trying to join .. 
# first, add column to facilitate joining
for i in range(len(csvs)):
	df = csvs[i]
	# create series to append as column
	new_series = [0]*len(df)
	for idx, row in df.iterrows():
		
		area_key = make_area_key(row)
		_, _, area_id = area_lookup[area_key]
		new_series[idx] = area_id
		
		
		print(area_id, area_key)
	
	# append column 'area_id'
	new_series = pd.DataFrame({'areaid': new_series})
	print(new_series)
	csvs[i] = df.join(new_series)
	
"""
# modify column names
suffix = ['_co', '_de', '_re']

for i in range(len(csvs)):
	df = csvs[i]
	df.columns = [col + suffix[i] for col in df.columns]
	#df.columns.values[0] = 'areaid'
"""
print('============ updated dataframes ===============')
print(csvs[0])
print(csvs[1])
print(csvs[2])



#print(joined)

#joined = joined.join(csvs[2], on='areaid', how='inner', lsuffix='', rsuffix='_re')

print('============ joined dataframes ===============')
joined = csvs[0].merge(csvs[1], on='areaid', how='inner', suffixes=('_co', '_de'))

#joined = csvs[0].join(csvs[1], on='areaid', how='inner')

#joined = pd.concat([csvs[0], csvs[1], csvs[2]], axis=1)

print(joined)

joined = joined.merge(csvs[2], on='areaid', how='inner')

print(joined)

# create dict of area_key to numbers
area_stat_dict = {}
count = 0
for date_key in date_keys:
	if count > 0 and count % 10 == 0: print(count)
	area_stat_dict[date_key] = {"date" : date_key}
	for area_key in area_keys:
		prov_state, country_reg, area_id = area_lookup[area_key]
		area_stat_dict[date_key][area_key] = {}
		area_stat_dict[date_key][area_key]["province/state"] = prov_state
		area_stat_dict[date_key][area_key]["country/region"] = country_reg		
		row = joined.loc[joined['areaid'] == area_id]
		#row = joined.query('areaid=='+str(area_id))
		try:
			area_stat_dict[date_key][area_key]["confirmed"] = int(row[date_key + '_co'].values[0]) # typecast to int to allow json serialization
		except Exception: # keyerror or indexerror for all stats
			area_stat_dict[date_key][area_key]["confirmed"] = float('nan')
			
		try:
			area_stat_dict[date_key][area_key]["deaths"] = int(row[date_key + '_de'].values[0])
		except Exception:
			area_stat_dict[date_key][area_key]["deaths"] = float('nan')
			
		try:
			area_stat_dict[date_key][area_key]["recovered"] = int(row[date_key].values[0])
		except Exception:
			area_stat_dict[date_key][area_key]["recovered"] = float('nan')
			
		try:
			area_stat_dict[date_key][area_key]["latitude"] = float(row['Lat_co'].values[0])
			area_stat_dict[date_key][area_key]["longitude"] = float(row['Long_co'].values[0])
		except Exception:
			area_stat_dict[date_key][area_key]["latitude"] = float('nan')
			area_stat_dict[date_key][area_key]["longitude"] = float('nan')						
			
	count += 1

print('dict generating done')

# dump to json
output_file = os.path.join(os.getcwd(), 'transformed', 'transformed.json')
doc_id = 1
with open(output_file, 'w') as f:
	

	for date_key in date_keys:
		json.dump({"index" : {"_id" : str(doc_id)}}, f)
		f.write('\n')
		json.dump(area_stat_dict[date_key], f)
		f.write('\n')
		doc_id += 1
		
print('json written to ', output_file)
"""
# create dict to convert to json
count = 0
for date_key in date_keys:
	if count > 0 and count % 10 == 0: print(count)	
	json_dict[date_key] = {"date" : date_key}
	
	for area_key in area_keys:
		
		prov_state, country_reg, area_id = area_lookup[area_key]
		json_dict[date_key][area_key] = { "province_state" : prov_state, \
							   "country_region" : country_reg, \
							   "latitude" : area_stat_dict[area_key]["latitude"], \
							   "longitude" :  area_stat_dict[area_key]["longitude"], \
							   "confirmed" : area_stat_dict[area_key]["confirmed"], \
							   "deaths" : area_stat_dict[area_key]["deaths"], \
							   "recovered" : area_stat_dict[area_key]["recovered"]} 
	count += 1
"""
"""
count = 0
# TODO: this is really slow because of the .loc looking for the matching province/state and country/region. improve it
for date_key in date_keys:

	if count > 0 and count % 10 == 0: print(count)
	
	json_dict[date_key] = {"date" : date_key}
	
	for area_key in area_keys:
		
		prov_state, country_reg = area_lookup[area_key]
		
		json_dict[date_key][area_key] = { "province_state" : prov_state, \
							   "country_region" : country_reg, \
							   "latitude" : csvs[0].loc[(csvs[0]['Province/State'] == prov_state) & (csvs[0]['Country/Region'] == country_reg)]['Lat'], \
							   "longitude" :  csvs[0].loc[(csvs[0]['Province/State'] == prov_state) & (csvs[0]['Country/Region'] == country_reg)]['Long']} 
							   
		try:
			json_dict[date_key][area_key]["confirmed"] = csvs[0].loc[(csvs[0]['Province/State'] == prov_state) & (csvs[0]['Country/Region'] == country_reg)][date_key]
		except KeyError:
			json_dict[date_key][area_key]["confirmed"] = float('nan')
			
		try:
			json_dict[date_key][area_key]["deaths"] = csvs[1].loc[(csvs[1]['Province/State'] == prov_state) & (csvs[1]['Country/Region'] == country_reg)][date_key]
		except KeyError:
			json_dict[date_key][area_key]["deaths"] = float('nan')
			
		try:
			json_dict[date_key][area_key]["recovered"] = csvs[2].loc[(csvs[2]['Province/State'] == prov_state) & (csvs[2]['Country/Region'] == country_reg)][date_key]
		except KeyError:
			json_dict[date_key][area_key]["recovered"] = float('nan')
			
	count += 1
	
"""
							   
#a = 2
""" Start interactive shell, ctrl+z resumes execution """
import code
code.interact(local=locals())

""" or do this in a Python shell """
# exec(open("./filename").read())
