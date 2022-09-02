#!/usr/bin/env python3
from collections import defaultdict
import json
from pathlib import Path
import sys
from time import sleep
from typing import Dict, Iterable, List, Set, Tuple
from metadata import LibMetadata, Repo, Version
from tinydb import TinyDB
from tinydb.database import Table
from library import Library
from bs4 import BeautifulSoup
import urllib.request
from log import success, error, info1
from threading import Thread


def get_all_libs() -> Set[Library]:
    all_libs: Set[Library] = set()
    db_files = ["db.json", "db2.json", "db3.json", "db4.json",
                "db5.json", "db6.json", "db7.json", "db8.json", "db9.json"]
    #db_files = ["db9.json"]

    for file in db_files:
        for item in TinyDB(file):
            all_libs.add(Library(d=item))

    return all_libs


# "groupid+artifactid" : {repo1, repo2, ...}
def get_all_library_ids_and_repos(all_libs: Set[Library],
                                  all_repos: Dict[str, Repo]) -> Dict[str, Set[Repo]]:
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
        with open(path, "w") as file:
            for line in ls:
                file.write(line + "\n")
    except Exception as e:
        print(e)


def find_versions(id: str, repo: Repo, all_libs: Set[Library]) -> List[Version]:
    xml = download_metadata_xml(id, repo)
    if not xml:
        return None

    versions_names = parse_versions(xml)
    if not versions_names:
        return None

    versions: List[Version] = []
    for name in versions_names:
        v = Version()
        v.version = name
        lib = find_lib(id, all_libs)
        if lib:
            v.date = lib.date
            v.usages = lib.usages
        versions.append(v)

    return versions


def create_repo(id: str, repo: Repo, all_libs: Set[Library], results: List[Repo], i: int):
    versions = find_versions(id, repo, all_libs)
    print(f"r{i+1}/103")
    if versions == None:
        return

    r = Repo()
    r.name = repo.name
    r.base_url = repo.base_url
    r.versions = versions

    results[i] = r


def scrape_all(all_libs: Set[Library], all_repos: Dict[str, Repo]
               ) -> Tuple[List[LibMetadata], Set[str]]:
    lib_ids_and_repos = get_all_library_ids_and_repos(all_libs, all_repos)
    all_metadata: List[LibMetadata] = []
    index = 0
    hits, misses = 0, 0
    not_found: List[str] = []

    for id, original_repos in lib_ids_and_repos.items():
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
        repos = original_repos
        if len(repos) == 0:
            repos = all_repos.values()

        for repo in repos:
            ind2 += 1
            print(f"r{ind2}/{len(repos)}")

            versions = find_versions(id, repo, all_libs)
            if versions == None:
                continue

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

    info1(f"{hits} libs found, {misses} libs not found")
    write_all(not_found, "not_found.txt")

    return all_metadata, set(not_found)


def scrape_from_all_repos(lib_ids: Iterable[str], all_libs: Iterable[Library], all_repos: Dict[str, Repo]) -> List[LibMetadata]:
    all_metadata: List[LibMetadata] = []
    index, hits, misses = 0, 0, 0
    not_found: List[str] = []

    for id in lib_ids:
        index += 1
        print(f"{index}/{len(lib_ids)}")
        info1(id)

        lib = find_lib(id, all_libs)
        metadata = LibMetadata()
        metadata.artifact_id = lib.artifact_id
        metadata.group_id = lib.group_id
        metadata.id = id
        metadata.tag = lib.tag

        threads: List[Thread] = [None] * len(all_repos)
        results = [None] * len(all_repos)

        for i, (_, r) in enumerate(all_repos.items()):
            threads[i] = Thread(target=create_repo,
                                args=(id, r, all_libs, results, i))
            threads[i].start()

        done = False
        for i in range(7):
            sleep(1)
            if any(results):
                done = True
                for t in threads:
                    t.join(0.01)
                break

        if not done:
            for t in threads:
                t.join(3)

        for repo in results:
            if repo != None:
                metadata.repos.append(repo)

        if metadata.repos:
            all_metadata.append(metadata)
            success(id + " added to second db")
            hits += 1
        else:
            error(id + " not found (again)")
            not_found.append(id)
            misses += 1

        info1(f"{hits} libs found, {misses} libs not found in second run")
    write_all(not_found, "not_found2.txt")

    return all_metadata


def save_metadata(metadata: LibMetadata) -> None:
    dest_dir = "./updated-libs/" + metadata.id
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    data = json.dumps(metadata.serialize(), indent=4)
    with open(dest_dir + "/metadata.json", 'w') as file:
        file.write(data)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ["all", "first-only", "second-only"]:
        print("Usage: ./metadata-scraper.py [all | first-only | second-only]")
        exit(1)

    mode = sys.argv[1]

    all_libs = get_all_libs()
    all_repos = get_all_repos()
    not_found = []

    if mode in ["all", "first-only"]:
        all_metadata, not_found = scrape_all(all_libs, all_repos)
        print("Libs: " + str(len(all_metadata)))
        for metadata in all_metadata:
            save_metadata(metadata)

    if mode == "second-only":
        try:
            with open("not_found.txt", "r") as f:
                not_found = [line.strip() for line in f.readlines()]
        except:
            print(
                "There must be a file named not_found.txt in order to run at second-only mode")
            exit(1)

    if mode in ["all", "second-only"]:
        retry = scrape_from_all_repos(not_found, all_libs, all_repos)
        print("Retry libs: " + str(len(retry)))
        for metadata in retry:
            save_metadata(metadata)

    success("done")


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
