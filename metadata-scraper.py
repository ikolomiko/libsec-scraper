#!/usr/bin/env python3
from collections import defaultdict
from typing import Dict, Iterable, List, Set
from metadata import LibMetadata, Repo, Version
from tinydb import TinyDB, table
from tinydb.database import Table
from library import Library
from bs4 import BeautifulSoup
import urllib.request
from log import success, error, info1


def get_all_libs() -> Set[Library]:
    all_libs: Set[Library] = set()
    db_files = ["db.json", "db2.json", "db3.json", "db4.json",
                "db5.json", "db6.json", "db7.json", "db8.json", "db9.json"]

    for file in db_files:
        for item in TinyDB(file):
            all_libs.add(Library(d=item))

    return all_libs


# "groupid+artifactid" : {repo1, repo2, ...}
def get_all_library_ids_and_repos(all_libs: Set[Library], all_repos: Dict[str, Repo]) -> Dict[str, Set[Repo]]:
    ids: Dict[str, Set[Repo]] = defaultdict(set)

    for lib in all_libs:
        id = lib.group_id + "+" + lib.artifact_id
        if lib.repo in all_repos.keys():
            ids[id].add(all_repos[lib.repo])

    print("Lib ids:", len(ids))
    return ids


def get_all_repos() -> Dict[str, Repo]:
    repos: Dict[Repo] = dict()
    with open("repo_stats.csv") as file:
        for line in file.readlines():
            (name, _, url) = line.strip().split(",")
            repo = Repo()
            repo.name = name
            repo.base_url = url
            repos[name] = repo

    print("Repos:", len(repos))
    return repos


def download_metadata_xml(lib_id: str, repo: Repo) -> str:
    url = repo.base_url + \
        lib_id.replace("+", "/").replace(".", "/") + "/maven-metadata.xml"
    try:
        response = urllib.request.urlopen(url, timeout=10)
        result = str(response.read().decode('utf-8'))
        return result
    except:
        return None


def parse_versions(xml: str) -> List[str]:
    try:
        soup = BeautifulSoup(xml, features="xml")
        return [v.text for v in soup.find_all("version") if v and v.text]
    except:
        return None


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


def write_all(ls: List[str], path: str) -> None:
    try:
        with open(path, "a") as file:
            for line in ls:
                file.write(line + "\n")
    except Exception as e:
        print(e)


def scrape_all() -> List[LibMetadata]:
    all_libs = get_all_libs()
    all_repos = get_all_repos()
    lib_ids_and_repos = get_all_library_ids_and_repos(all_libs, all_repos)
    all_metadata: List[LibMetadata] = []
    index = 0
    hits, misses = 0, 0
    not_found: List[str] = []

    for id, repos in lib_ids_and_repos.items():
        index += 1
        print(f"{index}/{len(lib_ids_and_repos)}")
        info1(id)

        tag = find_tag(id, all_libs)
        group_id, artifact_id = id.split("+")

        metadata = LibMetadata()
        metadata.id = id
        metadata.artifact_id = artifact_id
        metadata.group_id = group_id
        metadata.tag = tag

        ind2 = 0
        reposs = repos
        if len(reposs) == 0:
            reposs = all_repos.values()

        for repo in reposs:
            ind2 += 1
            print(f"r{ind2}/{len(reposs)}")
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
            success(id + " added to db")
            hits += 1
        else:
            error(id + " not found")
            not_found.append(id)
            misses += 1

    info1(f"{hits} libs found, {misses} libs cannot found")
    write_all(not_found, "not_found.txt")

    return all_metadata


def main() -> None:
    all_metadata = scrape_all()
    print("Libs: " + str(len(all_metadata)))

    db = TinyDB("unified-metadata.json")
    for metadata in all_metadata:
        db.upsert(table.Document(vars(metadata), metadata.id))

    success("done")


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
