#!/bin/bash

./etl_extract.sh
python etl_transform.py
num_papers=$(ls -l trimmed_papers | wc -l)
num_papers=$((num_papers - 1))
go run etl_load.go -count=$num_papers -index_name="paragraphs"
echo "========== ETL routine complete =========="
