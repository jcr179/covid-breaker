import json
import os
from tqdm import tqdm

# input: cord-19 dataset in directory ./data/
# output: each paper as its own json, trimmed and ready to upload to elasticsearch in ./trimmed_papers/

def get_fields(data: dict) -> dict:
	keep = {}
	
	for key, val in data.items():
		if key == 'abstract':
			if isinstance(val, list) and len(val) and 'text' in val[0]:
				keep['abstract'] = val[0]['text']
			
		elif key == 'body_text':
			text_len = len(val)
			keep['body_text'] = ''
			for i in range(text_len):
				keep['body_text'] += val[i]['text']
				
		elif key == 'metadata':
			keep['title'] = val['title']
			keep['authors'] = ''
			for author in val['authors']:
				keep['authors'] += author['first'] + ' ' + author['last'] + ' '				
			
		elif key == 'paper_id':
			keep['paper_id'] = val
			
		elif key == 'ref_entries':
			keep['captions'] = ''
			for k in val.keys():
				keep['captions'] += val[k]['text']
				
	return keep
	
try: 
	os.makedirs('./trimmed_papers/')
except FileExistsError:
	pass

dd = 'data' # data directory

directories = [os.path.join(dd, 'biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/'), \
			   os.path.join(dd,'comm_use_subset/comm_use_subset/pdf_json/'), \
			   os.path.join(dd,'comm_use_subset/comm_use_subset/pmc_json/'), \
			   os.path.join(dd,'custom_license/custom_license/pdf_json/'), \
			   os.path.join(dd,'custom_license/custom_license/pmc_json/'), \
			   os.path.join(dd,'noncomm_use_subset/noncomm_use_subset/pdf_json/'),\
			   os.path.join(dd,'noncomm_use_subset/noncomm_use_subset/pmc_json/')]

for directory in directories:
	
	print('Directory: ', directory)
	
	paper_files = [paper for paper in os.listdir(directory)]
	
	num_paper_files = len(paper_files)
	
	papers_written_this_dir = 0
	
	for paper_file in tqdm(range(num_paper_files)):
		
		paper = os.path.join(directory, paper_files[paper_file])
		
		with open(paper) as f:
			data = json.load(f)
			
		keep = get_fields(data)
					
		""" for now, leave out original input directory in output file """
		output_file = os.path.join(os.getcwd(), 'trimmed_papers', paper_files[paper_file])
		
		with open(output_file, 'w') as f:
			json.dump(keep, f)

		papers_written_this_dir += 1
	print('Papers written to ', directory, ':', papers_written_this_dir)

print('========== Transformation complete ==========')

