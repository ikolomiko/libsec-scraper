#!/usr/bin/env python3
import json
import os
import socket
from threading import Thread
from time import sleep
from typing import Callable, Iterable, List, Set
import urllib.request
import urllib.parse
from pathlib import Path
import shutil
from metadata import LibMetadata
from library import Library
from log import info1, info2, warn, error, success, log
from packaging.version import parse as parse_version

socket.setdefaulttimeout(15)

# must end with a forward slash (/)
download_path = "./updated-libs/"


# Downloads library from the scraped repository
# Return value: "aar"|"jar" if download is successful, otherwise None
def download_file(lib: Library) -> str:
    dest_dir = download_path + lib.group_id + "+" + lib.artifact_id + "/"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    filename = lib.artifact_id + "-" + lib.version + ".aar"
    url = lib.base_url + lib.group_id.replace(".", "/") + "/" + \
        lib.artifact_id.replace(".", "/") + "/" + lib.version + "/" + filename

    # For backwards compatibility with the data in db.json files
    if f"{lib.group_id}/{lib.artifact_id}".replace(".", "/") in lib.base_url:
        url = lib.base_url + lib.version + "/" + filename

    try:
        urllib.request.urlretrieve(url, dest_dir + lib.version + ".aar")
        success(f"{lib.id} successfully downloaded as aar")
        return "aar"
    except Exception as e:
        warn("AAR not found: " + str(e))
        try:
            url = url[:-4] + ".jar"
            urllib.request.urlretrieve(url, dest_dir + lib.version + ".jar")
            success(f"{lib.id} successfully downloaded as jar")
            return "jar"
        except Exception as er:
            error("JAR not found: " + str(er))
            error(url)
            error(lib.repo)
            return None


# Return value: "aar"|"jar" if file exists, otherwise None
def copy_from_cache(lib: Library) -> str:
    dest_dir = download_path + lib.group_id + "+" + lib.artifact_id + "/"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    if Path(dest_dir + lib.version + ".aar").is_file():
        success(f"{lib.id} already exists as aar")
        return "aar"
    if Path(dest_dir + lib.version + ".jar").is_file():
        success(f"{lib.id} already exists as jar")
        return "jar"

    cache_lib = Path("./libs/" + lib.id + ".aar")
    if cache_lib.is_file():
        shutil.copy(str(cache_lib), dest_dir + lib.version + ".aar")
        success(f"{lib.id} was copied from cache as aar")
        return "aar"
    cache_lib = Path("./libs/" + lib.id + ".jar")
    if cache_lib.is_file():
        shutil.copy(str(cache_lib), dest_dir + lib.version + ".jar")
        success(f"{lib.id} was copied from cache as jar")
        return "jar"

    return None


# Default key for downloading libs: most used one + first 2 versions + last 2 versions
def default_key(all_versions: Iterable[Library]) -> Set[Library]:
    result: Set[Library] = set()
    result.add(sorted(all_versions, key=lambda x: x.usages)[-1])
    result |= set(
        sorted(all_versions, key=lambda x: parse_version(x.version))[:2])
    result |= set(
        sorted(all_versions, key=lambda x: parse_version(x.version))[-2:])
    return result


def download_versions(lib: LibMetadata,
                      key: Callable[[List[Library]], Set[Library]] = default_key) -> None:

    all_versions: Set[Library] = set()
    for repo in lib.repos:
        for v in repo.versions:
            l = Library(d={
                "artifact_id": lib.artifact_id,
                "group_id": lib.group_id,
                "version": v.version,
                "repo": repo.name,
                "usages": v.usages,
                "date": v.date,
                "id": lib.id + "+" + v.version,
                "tag": lib.tag,
                "base_url": repo.base_url
            })
            all_versions.add(l)

    selected = key(all_versions)
    for item in selected:
        ext = copy_from_cache(item)
        if ext == None:
            ext = download_file(item)

        v = lib.get_repo(item.repo).get_version(item.version)
        if ext == None:
            v.downloaded = False
            v.filetype = "error"
        else:
            v.downloaded = True
            v.filetype = ext


def save_library(metadata_dir: str) -> None:
    try:
        if metadata_dir[-1] != "/":
            metadata_dir += "/"

        metadata: LibMetadata = None
        with open(metadata_dir + "metadata.json", "r") as file:
            data = json.loads(file.read())
            metadata = LibMetadata(data)

        download_versions(metadata, key=default_key)

        out = json.dumps(metadata.serialize(), indent=4)
        with open(metadata_dir + "metadata.json", 'w') as file:
            file.write(out)
        info2(f"{metadata.id} completed")
    except Exception as e:
        error("Error at " + metadata_dir)
        error(str(e))


def save_all_libraries() -> None:
    metadata_root_dir = "./libdata/"
    subdirs = next(os.walk(metadata_root_dir))[1]

    threads: List[Thread] = [None] * len(subdirs)

    def any_alive(i: int) -> bool:
        for t in threads[i-5:i]:
            if t != None and t.is_alive():
                return True
        return False

    for i, subdir in enumerate(subdirs):
        threads[i] = Thread(target=save_library,
                            args=(metadata_root_dir+subdir,))
        threads[i].start()
        log(f"Thread {i+1}/{len(subdirs)} is running")

        if i != 0 and i % 5 == 0:
            while any_alive(i):
                info1(
                    "There are still some threads running. Sleeping for 5 more seconds")
                sleep(5)

    for t in threads:
        t.join(10)


def main() -> None:
    try:
        info1("----------STARTING----------")
        save_all_libraries()
        success("----------DONE----------")
    except Exception as e:
        error(str(e))


if __name__ == "__main__":
    main()
