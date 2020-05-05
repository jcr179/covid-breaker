#!/bin/bash

# Run this to setup the BERT server to both generate encodings
# for the database, and to handle client requests

# Check for dependencies
# TODO
# Need bert-serving-server, bert-serving-client, tensorflow 1.15.2 (use 'pip install tensorflow==1.15.2')

# Get BERT model 
echo "Downloading BERT model..."
wget https://storage.googleapis.com/bert_models/2018_10_18/cased_L-12_H-768_A-12.zip
unzip cased_L-12_H-768_A-12.zip
rm cased_L-12_H-768_A-12.zip

# Start BERT server
echo "Starting BERT server..."
bert-serving-start -num_worker=1 -model_dir cased_L-12_H-768_A-12/ -max_seq_len=NONE

# Done: Now you can run scripts/etl.sh 
# "BERT setup and server startup complete." 
# "To foreground BERT server, use 'jobs' and then 'fg %[num of BERT process]'"
# "Remember to start 2 elasticsearch nodes before running etl_load.go"
