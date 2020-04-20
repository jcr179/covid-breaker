import json
import os
from tqdm import tqdm

# input: trimmed papers as jsons
# output: single json file ready for bulk elasticsearch index 

trim_dir = os.path.join(os.getcwd(), 'trimmed_papers')

trimmed_files = [f for f in os.listdir(trim_dir)]

num_trimmed_files = len(trimmed_files)

output_file = 'bulk_index.json'

doc_id = 1

with open(output_file, 'w') as f:
	
	for i in tqdm(range(num_trimmed_files)):
	
		json.dump({"index" : {"_id" : str(doc_id)}}, f)
		f.write('\n')
		
		trimmed_file_fp = open(os.path.join(trim_dir, trimmed_files[i]))
		
		trimmed_file = json.load(trimmed_file_fp)
		
		trimmed_file_fp.close()
		
		json.dump(trimmed_file, f)
		f.write('\n')
		
		doc_id += 1

""" TODO: consolidate the parsing script and this script into one,
so that there's no need to store all the extra space for the 
intermediate operation. """ 
