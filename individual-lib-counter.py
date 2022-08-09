#!/usr/bin/env python3
from typing import Set
from tinydb import TinyDB
from tinydb.database import Table

database = TinyDB('db.json')


def main():
    all = database.all()
    unique_ids: Set[str] = {
        f"{item['group_id']}+{item['artifact_id']}" for item in all}
    print("No of all libs (all versions included):",len(all))
    print("No of individual libs:",len(unique_ids))


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
