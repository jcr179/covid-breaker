#!/bin/bash

# input: ~/.kaggle/kaggle.json, API key downloaded from Kaggle account page. Don't forget to run chmod 600 [path to kaggle.json] 
# output: directory data/ with paper subdirectories inside

kaggle datasets download allen-institute-for-ai/CORD-19-research-challenge -p ./data

echo "========== Extraction complete =========="
