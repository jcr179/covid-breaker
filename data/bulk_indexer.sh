#!/bin/bash

echo "Bulk indexing starting..."

curl -H "Content-Type: application/json" -XPOST "localhost:9200/papers4/_bulk?pretty&refresh" --data-binary "@paper.json"

curl "localhost:9200/_cat/indices?v"

echo "Bulk indexing complete."
