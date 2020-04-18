# Extract .csv data from:
# Can try pulling data directly from automatically updating repo at (updates around 7 est daily)
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv


import requests 
import os
import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger('extract')
		
def extract_csv(url: str, output_dir: str, data_type: str) -> bool:
	"""
	url: url of raw csv data to download
	output_dir: absolute path to download file to
	data_type: functions as suffix of filename, e.g. 'confirmed', 'deaths'
	
	returns: True if extraction successful, False otherwise
	"""
	
	if not os.path.exists(output_dir):
		log.error("Specified output directory is invalid")
		return False
	
	try:
		data = requests.get(url)
		log.info("Data extracted from url")
		output_file_dir = os.path.join(output_dir, data_type + '.csv')
		open(output_file_dir, 'wb').write(data.content)
		log.info("Output written to " + output_file_dir)
		return True
		
	except Exception as e:
		""" TODO: Use fallback data if can't access remote data repo """
		log.error(e)
		return False
