#!/bin/bash

# input: ~/.kaggle/kaggle.json, API key downloaded from Kaggle account page. Don't forget to run chmod 600 [path to kaggle.json] 
# output: directory data/ with paper subdirectories inside

kaggle datasets download allen-institute-for-ai/CORD-19-research-challenge -p ./data
echo "Dataset downloaded. Unzipping over 50k papers..."
cd data
unzip -q CORD-19-research-challenge.zip
echo "Papers unzipped. Removing unnecessary files..."
rm CORD-19-research-challenge.zip
rm -rf cord_19_embeddings_4_17
rm COVID.DATA.LIC.AGMT.pdf
rm json_schema.txt
rm metadata.csv
rm metadata.readme

echo "========== Extraction complete =========="
