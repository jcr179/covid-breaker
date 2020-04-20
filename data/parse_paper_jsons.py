import json
import os
from tqdm import tqdm

# input: cord-19 dataset
# output: jsons trimmed and ready to upload to elasticsearch

directories = ['biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/', \
			   'comm_use_subset/comm_use_subset/pdf_json/', \
			   'comm_use_subset/comm_use_subset/pmc_json/', \
			   'custom_license/custom_license/pdf_json/', \
			   'custom_license/custom_license/pmc_json/', \
			   'noncomm_use_subset/noncomm_use_subset/pdf_json/',\
			   'noncomm_use_subset/noncomm_use_subset/pmc_json/']

for directory in directories:
	
	print('Directory: ', directory)
	
	paper_files = [paper for paper in os.listdir(directory)]
	
	num_paper_files = len(paper_files)
	
	papers_written_this_dir = 0
	
	for paper_file in tqdm(range(num_paper_files)):
		
		paper = os.path.join(directory, paper_files[paper_file])
		
		with open(paper) as f:
			data = json.load(f)
			
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
				# process authors
				#authors_raw = val['authors'][0]
				#organizations = []
				keep['authors'] = ''
				for author in val['authors']:
					keep['authors'] += author['first'] + ' ' + author['last'] + ' '
				
				
				
			elif key == 'paper_id':
				keep['paper_id'] = val
				
			elif key == 'ref_entries':
				keep['captions'] = ''
				for k in val.keys():
					keep['captions'] += val[k]['text']
					
			""" for now, leave out original input directory in output file """
			output_file = os.path.join(os.getcwd(), 'trimmed_papers', paper_files[paper_file])
			#doc_id = 2
			with open(output_file, 'w') as f:
				#json.dump({"index" : {"_id" : str(doc_id)}}, f)	# this indexing line is needed if indexing in bulk
				#f.write('\n')
				json.dump(keep, f)
				#f.write('\n')

		#print('json written to ', output_file)
		papers_written_this_dir += 1
	print('Papers written to ', directory, ':', papers_written_this_dir)


"""

print('json written to ', output_file)


with open('biorxiv_medrxiv/biorxiv_medrxiv/pdf_json/402041df2d9812dbcdae08153d0350eee170eea9.json') as f:
	data = json.load(f)
	
#print(json.dumps(data, indent = 4))

#level 1 keys
key1 = {}


for key, val in data.items():
	key1[key] = val

#print('=== level 1 ===')
#print(key1.keys())


#for key, val in data.items():
#	if key == 'ref_entries': # if key == 'abstract' you can extract purely the abstract 
#		
#		for k in val.keys():
#			print(val[k]['text'])
		#for k, v in val.items():
		#	print(k)

#print('==============================')

keep = {}

for key, val in data.items():
	if key == 'abstract':
		keep['abstract'] = val[0]['text']
		
	elif key == 'body_text':
		text_len = len(val)
		keep['body_text'] = ''
		for i in range(text_len):
			keep['body_text'] += val[i]['text']
			
	elif key == 'metadata':
		keep['title'] = val['title']
		# process authors
		#authors_raw = val['authors'][0]
		#organizations = []
		keep['authors'] = ''
		for author in val['authors']:
			keep['authors'] += author['first'] + ' ' + author['last'] + ' '
		
		
		
	elif key == 'paper_id':
		keep['paper_id'] = val
		
	elif key == 'ref_entries':
		keep['captions'] = ''
		for k in val.keys():
			keep['captions'] += val[k]['text']
		
			
for k, v in keep.items():
	print(k)
	print(v)
	print('========')

output_file = os.path.join(os.getcwd(), 'paper.json')
doc_id = 2
with open(output_file, 'w') as f:
	json.dump({"index" : {"_id" : str(doc_id)}}, f)	# this indexing line is needed if indexing in bulk
	f.write('\n')
	json.dump(keep, f)
	f.write('\n')


print('json written to ', output_file)

"""

# index it:
# curl -H "Content-Type: application/json" -XPOST "localhost:9200/papers/_bulk?pretty&refresh" --data-binary "@paper.json"

# search for it;
"""
curl -X GET "localhost:9200/papers/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "query": { "match_phrase": { "body_text": "interleaved" } }
}
'
"""
