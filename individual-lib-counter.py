#!/usr/bin/env python3
from typing import Set
from tinydb import TinyDB
from tinydb.database import Table

def main():
    all = TinyDB('db.json').all()
    for item in TinyDB('db2.json').all():
        all.append(item)
    
    unique_ids: Set[str] = {
        f"{item['group_id']}+{item['artifact_id']}" for item in all}
    print("No of all libs (all versions included):",len(all))
    print("No of individual libs:",len(unique_ids))


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
