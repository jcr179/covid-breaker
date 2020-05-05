import json
import os
from tqdm import tqdm
from copy import deepcopy
from bert_serving.client import BertClient
import sys

# TODO: handle if BertClient couldn't be instantiated 
bc = BertClient(ip='localhost', output_fmt='list')

def get_bert_encoding(text: str) -> list:
	return bc.encode([text])[0]
	

	
if len(sys.argv) < 2:
	# Usage: get_embeddings.sh [query string]
	sys.exit(1)
	
stripped = [x.strip() for x in sys.argv[1:]]

#print('Stripped: ', stripped)

query = ' '.join(stripped)
	
#print('Query text: ', query)

#query = sys.argv[1].strip()

emb = get_bert_encoding(query)

bc.close()

print(emb)
