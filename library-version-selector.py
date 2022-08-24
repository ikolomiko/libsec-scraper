#!/usr/bin/env python3

from collections import defaultdict
from typing import Dict, List, Set
from tinydb import TinyDB, table
from tinydb.database import Table
import sys


class Library:
    def __init__(self, d: dict = None) -> None:
        self.artifact_id = ""
        self.group_id = ""
        self.version = ""
        self.repo = ""
        self.usages = 0
        self.date = ""
        self.id = ""
        self.tag = ""
        self.base_url = ""

        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)

    def __str__(self) -> str:
        return (
            f"Artifact id: {self.artifact_id}\n"
            f"Group id: {self.group_id}\n"
            f"Version: {self.version}\n"
            f"Repo: {self.repo}\n"
            f"Usages: {self.usages}\n"
            f"Date: {self.date}\n"
            f"Tag: {self.tag}\n"
            f"URL: {self.base_url}"
        )

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def __hash__(self) -> int:
        return hash(self.id)


def main() -> None:
    db = sys.argv[1]
    # dbs = ["db.json", "db2.json", "db3.json", "db4.json",
    #       "db5.json", "db6.json", "db7.json", "db8.json", "db9.json"]
    # for db in dbs:
    artifact_versions: Dict[str, List[Library]] = defaultdict(list)
    for item in TinyDB(db).all():
        lib = Library(item)
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
