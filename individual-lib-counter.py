#!/usr/bin/env python3
from typing import Set
from tinydb import TinyDB
from tinydb.database import Table

def main():
    dbs = ["db.json", "db2.json", "db3.json", "db4.json", "db5.json", "db6.json", "db7.json"]
    all = [] 
    for db in dbs:
        all.extend(TinyDB(db).all())
    
    unique_ids: Set[str] = {
        f"{item['group_id']}+{item['artifact_id']}" for item in all}
    print("No of all libs (all versions included):",len(all))
    print("No of individual libs:",len(unique_ids))


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
