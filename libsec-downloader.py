#!/usr/bin/env python3
import sys
import urllib.request
import urllib.parse
from tinydb import TinyDB
from tinydb.database import Table
import traceback

# This script is intended to be used on the server to download all libraries saved in the database
USAGE = "Usage: python3 libsec-downloader.py <file 1> <file 2> <... file n>"
# <file n>: n-th json database file

# must end with a forward slash (/)
download_path = "./libs/"


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


def save_file(lib: Library) -> None:
    filename = lib.artifact_id + "-" + lib.version + ".aar"
    try:
        urllib.request.urlretrieve(
            lib.base_url + lib.version + "/" + filename, download_path + lib.id + ".aar")
    except Exception as e:
        print("Error:", e)
        try:
            filename = lib.artifact_id + "-" + lib.version + ".jar"
            urllib.request.urlretrieve(
                lib.base_url + lib.version + "/" + filename, download_path + lib.id + ".jar")
        except:
            print("JAR Bulunamadı:", lib.base_url + filename)


def main() -> None:
    if len(sys.argv) < 2:
        print(USAGE)
        return

    for db in sys.argv[1:]:
        try:
            database = TinyDB(db)
            for lib in database.all():
                try:
                    lib = Library(lib)
                    print(lib)
                    save_file(lib)
                except Exception as e:
                    print(e)
                    print(traceback.format_exc())
        except Exception as e:
            print(e)
            print(traceback.format_exc())


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
