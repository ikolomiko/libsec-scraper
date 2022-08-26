#!/usr/bin/env python3
from nntplib import ArticleInfo
from typing import Iterable, List, Set
from metadata import LibMetadata, Repo, Version
from tinydb import TinyDB, table
from tinydb.database import Table
from library import Library
import json
from bs4 import BeautifulSoup
import urllib.request


def get_all_libs() -> Set[Library]:
    all_libs: Set[Library] = set()
    db_files = ["db.json", "db2.json", "db3.json", "db4.json",
                "db5.json", "db6.json", "db7.json", "db8.json", "db9.json"]

    for file in db_files:
        for item in TinyDB(file):
            all_libs.add(Library(d=item))

    return all_libs


# "groupid+artifactid"
def get_all_library_ids(all_libs: Set[Library]) -> Set[str]:
    ids: Set[str] = set()

    for lib in all_libs:
        ids.add(lib.group_id+"+"+lib.artifact_id)

    print("Lib ids:", len(ids))
    return ids


def get_all_repos() -> List[Repo]:
    repos: List[Repo] = []
    with open("repo_stats.csv") as file:
        for line in file.readlines():
            (name, _, url) = line.strip().split(",")
            repo = Repo()
            repo.name = name
            repo.base_url = url
            repos.append(repo)

    print("Repos:", len(repos))
    return repos


def download_metadata_xml(lib_id: str, repo: Repo) -> str:
    url = repo.base_url + lib_id.replace("+", "/") + "/maven-metadata.xml"
    try:
        response = urllib.request.urlopen(url, timeout=10)
        result = str(response.read().decode('utf-8'))
        return result
    except:
        return None


def parse_versions(xml: str) -> List[str]:
    soup = BeautifulSoup(xml, features="xml")
    return [v.text for v in soup.versioning.versions if v and v.text]


def find_lib(id: str, all_libs: Iterable[Library]) -> Library:
    lib = None

    for item in all_libs:
        if item.group_id + "+" + item.artifact_id == id:
            lib = item
            break

    return lib

def find_tag(id: str, all_libs: Iterable[Library]) -> str:
    lib = find_lib(id, all_libs)
    if lib:
        return lib.tag

    return "not found"

def is_from_pentaho(id: str, all_libs: Iterable[Library]):
    for lib in all_libs:
        if lib.group_id + "+" + lib.artifact_id == id:
            if lib.repo == "PentahoOmni":
                return True


def scrape_all() -> List[LibMetadata]:
    all_libs = get_all_libs()
    lib_ids = get_all_library_ids(all_libs)
    repos = get_all_repos()
    all_metadata: List[LibMetadata] = []
    index = 0

    repo_pentaho = Repo()
    repo_pentaho.base_url = "https://nexus.pentaho.org/content/groups/omni/"
    repo_pentaho.name = "PentahoOmni"

    for id in lib_ids:
        index += 1
        print(f"{index}/{len(lib_ids)}")

        tag = find_tag(id, all_libs)
        group_id, artifact_id = id.split("+")

        metadata = LibMetadata()
        metadata.id = id
        metadata.artifact_id = artifact_id
        metadata.group_id = group_id
        metadata.tag = tag

        ind2 = 0
        additional = [repo_pentaho] if is_from_pentaho(id, all_libs) else []
        for repo in additional + repos:
            ind2 += 1
            print(f"r{ind2}/{len(repos) + len(additional)}")
            xml = download_metadata_xml(id, repo)
            if not xml:
                continue

            versions_names = parse_versions(xml)
            if not versions_names:
                continue

            versions: List[Version] = []
            for name in versions_names:
                v = Version()
                v.version = name

                lib = find_lib(id, all_libs)
                if lib:
                    v.date = lib.date
                    v.usages = lib.usages

                versions.append(v)

            r = Repo()
            r.name = repo.name
            r.base_url = repo.base_url
            r.versions = versions
            metadata.repos.append(r)

        if metadata.repos:
            all_metadata.append(metadata)

    return all_metadata


def main() -> None:
    all_metadata = scrape_all()
    print("Libs: " + len(all_metadata))
    
    db = TinyDB("unified-metadata.json")
    for metadata in all_metadata:
        db.upsert(table.Document(vars(metadata), metadata.id))


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
