import json
import os
from tqdm import tqdm
from copy import deepcopy

# input: cord-19 dataset in directory ./data/
# output: each paper as its own json, trimmed and ready to upload to elasticsearch in ./trimmed_papers/

def write_json(output_file: str, data: dict, counter: int) -> int:
	with open(output_file, 'w') as f:
		json.dump(data, f) 
	return counter + 1

def handle_file(data: dict, p_num_offset: int):
	
	keep = {}
	
	keys = data.keys()
	
	p_num = p_num_offset
	
	if 'abstract' in keys:
		val = data['abstract']
		if isinstance(val, list) and len(val) and 'text' in val[0]:
			
			keep['abstract'] = data['abstract'][0]['text']
	
	if 'paper_id' in keys:
		keep['paper_id'] = data['paper_id']
		
	if 'metadata' in keys:
		keep['title'] = data['metadata']['title']
		keep['authors'] = ''
		for author in data['metadata']['authors']:
			keep['authors'] += author['first'] + ' ' + author['last'] + ' , '	
		
	# Do for every paragraph in body_text and ref_entries
	if 'body_text' in keys:
		
		for paragraph in data['body_text']:
			

			keep_clone = deepcopy(keep)
			
			keep_clone['text'] = paragraph['text']
			

			output_file = os.path.join(os.getcwd(), 'trimmed_papers', str(p_num) + '.json')
			
			p_num = write_json(output_file, keep_clone, p_num)
			
	return p_num
		
		

	
try: 
	os.makedirs('./trimmed_papers/')
except FileExistsError:
	pass

dd = 'data' # data directory

""" # Full dataset
directories = [os.path.join(dd, 'biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/'), \
			   os.path.join(dd,'comm_use_subset/comm_use_subset/pdf_json/'), \
			   os.path.join(dd,'comm_use_subset/comm_use_subset/pmc_json/'), \
			   os.path.join(dd,'custom_license/custom_license/pdf_json/'), \
			   os.path.join(dd,'custom_license/custom_license/pmc_json/'), \
			   os.path.join(dd,'noncomm_use_subset/noncomm_use_subset/pdf_json/'),\
			   os.path.join(dd,'noncomm_use_subset/noncomm_use_subset/pmc_json/')]
"""
directories = [os.path.join(dd, 'biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/'), \
			   os.path.join(dd,'noncomm_use_subset/noncomm_use_subset/pdf_json/')]

p_num_offset = 0

try:
	for directory in directories:
		
		last = p_num_offset
		
		print('Directory: ', directory)
		
		paper_files = [paper for paper in os.listdir(directory)]
		
		num_paper_files = len(paper_files)
		
		papers_written_this_dir = 0
		
		for paper_file in tqdm(range(num_paper_files)):
			
			paper = os.path.join(directory, paper_files[paper_file])
						
			with open(paper) as f:
				data = json.load(f)
				
			# new rouine here

			p_num_offset = handle_file(data, p_num_offset)
			
				
			#keep = get_fields(data)
						
			""" for now, leave out original input directory in output file """
			#output_file = os.path.join(os.getcwd(), 'trimmed_papers', paper_files[paper_file])
			
			#with open(output_file, 'w') as f:
			#	json.dump(keep, f)
				
			# stop removing old code here

			papers_written_this_dir += 1
			
		print('Papers/paragraphs written from ', directory, ':', papers_written_this_dir, '/', p_num_offset-last)
		
		cmd = 'rm -r ' + directory
		os.system(cmd)
		
	# Get rid of the original data on success, to save space
	cmd = 'rm -r ./data/'
	os.system(cmd)
	
except Exception as e:
	print(e)

print('========== Transformation complete ==========')

