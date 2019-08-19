#!/bin/bash

INDEX="data"

echo "Dropping index $INDEX"
curl -XDELETE ${AUTH} "http://localhost:9200/${INDEX}?pretty"
echo "Creating index $INDEX"
curl -XPUT ${AUTH} "http://localhost:9200/${INDEX}?pretty"
curl -XGET ${AUTH} "http://localhost:9200/${INDEX}?pretty"

echo "Loading data..."
pv elastic_data_full.json | esbulk -index ${INDEX} -type cluster

