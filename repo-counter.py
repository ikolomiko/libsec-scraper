#!/usr/bin/env python3
from tinydb import TinyDB
from tinydb.database import Table
from collections import defaultdict

class StringIdClassTable(Table):
    document_id_class = str

def extract_baseurl(s: str, group_id: str) -> str:
    return s[:s.rfind(group_id.replace('.','/'))]


TinyDB.table_class = StringIdClassTable

dc = defaultdict(lambda: ["", 0]) # URL: (NAME, USAGE)
for db in ["db.json", "db2.json", "db3.json", "db4.json", "db5.json", "db6.json", "db7.json", "db8.json", "db9.json"]:
    database = TinyDB(db)
    for item in database.all():
        url = extract_baseurl(item['base_url'], item['group_id'])
        name = item['repo']
        dc[url][0] = name
        dc[url][1] += 1

with open("repo_stats.csv", 'w', encoding = 'utf-8') as f:
    for k, v in sorted(dc.items(), key=lambda item: item[1][1], reverse=True):
        f.write(f"{v[0]},{v[1]},{k}\n")
