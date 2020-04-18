import extract
import os

cd = os.getcwd()

urls = {'confirmed': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv', \
		'deaths': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv', \
		'recovered': 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'}
		
# def extract_csv(url: str, output_dir: str, data_type: str) -> bool



def test_extract_full():
	results = []
	
	for url in urls:
		result = extract.extract_csv(urls[url], os.path.join(cd, 'test_extract_dir'), url)
		results.append(result)
		
	assert all(results) == True
