# This file produces a mapping between oncotree types and all their subtypes from a tab delimited oncotree file...
# just make sure ONCOTREE_TXT_FILE_PATH is set in your env and points to the desired TSV file
import csv
import os
from collections import defaultdict

ONCOTREE_TXT_FILE_PATH = "C:\HKU\Matchminer\oncotree_file.txt"
#os.getenv("ONCOTREE_TXT_FILE_PATH", None)
#console.log(ONCOTREE_TXT_FILE_PATH)
with open(ONCOTREE_TXT_FILE_PATH) as f:
    r = csv.DictReader(f, delimiter='\t')
    rows = [row for row in r]
mapping = defaultdict(set)
for row in rows:
    level_1 = row['level_1'].split('(')[0].strip()
    level_2 = row['level_2'].split('(')[0].strip()
    level_3 = row['level_3'].split('(')[0].strip()
    level_4 = row['level_4'].split('(')[0].strip()
    level_5 = row['level_5'].split('(')[0].strip()
    level_6 = row['level_6'].split('(')[0].strip()
    level_7 = row['level_7'].split('(')[0].strip()
    mapping[level_1].update({level_1, level_2, level_3, level_4, level_5, level_6, level_7})
    mapping[level_2].update({level_2, level_3, level_4, level_5, level_6, level_7})
    mapping[level_3].update({level_3, level_4, level_5, level_6, level_7})
    mapping[level_4].update({level_4, level_5, level_6, level_7})
    mapping[level_5].update({level_5, level_6, level_7})
    mapping[level_6].update({level_6, level_7})
    mapping[level_7].update({level_7})

del mapping['']
for s in mapping.values():
    if '' in s:
        s.remove('')
mapping['_LIQUID_'] = mapping['Lymph'] | mapping['Blood']
for k in list(mapping.keys()):
    if k not in mapping['_LIQUID_']:
        mapping['_SOLID_'].add(k)

for k in mapping.keys():#
    mapping[k] = list(mapping[k])

import json

with open('oncotree_mapping.json', 'w') as f:
    json.dump(mapping, f, sort_keys=True, indent=2)
