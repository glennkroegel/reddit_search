"""
created_by: Glenn Kroegel
Date: 17 August 2019

description: Format reddit data into line sepd json for upload into elastic. Only append records with images in link.
"""

import json
import pandas as pd

DATA_FILE = 'safe_links_all'
ELASTIC_DATA = 'elastic_data_full.json'

skipped = []

with open(DATA_FILE, 'r') as infile:
    with open(ELASTIC_DATA, 'w+') as outfile:
        i = 0
        while True:
            i += 1
            line = infile.readline()
            if not line:
                break
            try:
                record = json.loads(line)
                if not record[2]:
                    continue
                link = record[2]
                if '.jpg' in link or '.png' in link:
                    subreddit = record[0]
                    title = record[1]
                    outfile.write(json.dumps({'subreddit': subreddit, 'title': title}) + '\n')
                if i % 1000000 == 0:
                    print('Processed ', i, ' skipped', len(skipped))
            except:
                skipped.append(line)

print(len(skipped))