#!/usr/bin/env python3

from collections import defaultdict
from typing import Dict, List, Set
from tinydb import TinyDB, table
from tinydb.database import Table
import sys
from library import Library


def main() -> None:
    db = sys.argv[1]
    # dbs = ["db.json", "db2.json", "db3.json", "db4.json",
    #       "db5.json", "db6.json", "db7.json", "db8.json", "db9.json"]
    # for db in dbs:
    artifact_versions: Dict[str, List[Library]] = defaultdict(list)
    for item in TinyDB(db).all():
        lib = Library(d=item)
        artifact_versions[lib.group_id + "+" + lib.artifact_id].append(lib)

    for versions in artifact_versions.values():
        items: Set[Library] = set()
        items.add(sorted(versions, key=lambda x: x.usages)[-1])
        items |= set(sorted(versions, key=lambda x: x.version)[:2])
        items |= set(sorted(versions, key=lambda x: x.version)[-2:])
        newdb = TinyDB("processed-dbs/" + db)
        for item in items:
            try:
                newdb.insert(table.Document(vars(item), item.id))
            except Exception as e:
                print(e)


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
