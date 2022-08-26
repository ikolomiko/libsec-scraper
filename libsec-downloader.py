#!/usr/bin/env python3
import sys
import urllib.request
import urllib.parse
from tinydb import TinyDB
from tinydb.database import Table
import traceback
from pathlib import Path
import shutil
from library import Library
from log import info1, info2, warn, error, success

# This script is intended to be used on the server to download all libraries saved in the database
USAGE = "Usage: python3 libsec-downloader.py <file 1> <file 2> <... file n>"
# <file n>: n-th json database file

# must end with a forward slash (/)
download_path = "./updated-libs/"


# Saves library from the scraped repository
def save_file(lib: Library) -> bool:
    dest_dir = download_path + lib.group_id + "+" + lib.artifact_id + "/"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    filename = lib.artifact_id + "-" + lib.version + ".aar"
    try:
        urllib.request.urlretrieve(
            lib.base_url + lib.version + "/" + filename, dest_dir + lib.version + ".aar")
        return True
    except Exception as e:
        warn("AAR bulunamadı: " + str(e))
        try:
            filename = lib.artifact_id + "-" + lib.version + ".jar"
            urllib.request.urlretrieve(
                lib.base_url + lib.version + "/" + filename, dest_dir + lib.version + ".jar")
            return True
        except Exception as er:
            error("JAR Bulunamadı: " + str(er))
            print(lib.base_url + filename)
            print(lib.repo)
            return False


# Saves library from given repository
def save_file_from_repo(lib: Library, repo_url: str) -> bool:
    dest_dir = download_path + lib.group_id + "+" + lib.artifact_id + "/"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    if repo_url[-1] != "/":
        repo_url = repo_url + "/"

    url = repo_url + lib.id.replace('+', '/') + \
        "/" + lib.artifact_id + "-" + lib.version + ".aar"
    try:
        urllib.request.urlretrieve(url, dest_dir + lib.version + ".aar")
        return True
    except Exception as e:
        warn("AAR bulunamadı: " + str(e))
        try:
            url = url[:-4] + ".jar"
            urllib.request.urlretrieve(url, dest_dir + lib.version + ".jar")
            return True
        except Exception as er:
            error("JAR Bulunamadı: " + str(er))
            print(url)
            print(repo_url)
            return False


def copy_from_cache(lib: Library) -> bool:
    dest_dir = download_path + lib.group_id + "+" + lib.artifact_id + "/"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    if Path(dest_dir + lib.version + ".aar").is_file() or \
            Path(dest_dir + lib.version + ".jar").is_file():
        return True

    cache_lib = Path("./libs/" + lib.id + ".aar")
    if cache_lib.is_file():
        shutil.copy(str(cache_lib), dest_dir + lib.version + ".aar")
        return True
    cache_lib = Path("./libs/" + lib.id + ".jar")
    if cache_lib.is_file():
        shutil.copy(str(cache_lib), dest_dir + lib.version + ".jar")
        return True

    return False


def main() -> None:
    if len(sys.argv) < 2:
        info1(USAGE)
        return

    repos = [line.split(',')[2].strip()
             for line in open("repo_stats.csv", "r").readlines()]

    for db in sys.argv[1:]:
        index = 0
        n_downloaded = 0
        try:
            database = TinyDB(db)
            n_all = len(database.all())
            for lib in database.all():
                index += 1
                try:
                    lib = Library(d=lib)
                    if copy_from_cache(lib):
                        n_downloaded += 1
                        info2("Kütüphane cache'ten kopyalandı: " + lib.id)
                        continue

                    if save_file(lib):
                        n_downloaded += 1
                        success("Kütüphane indirildi: " + lib.id)
                    else:
                        info1(lib.id + " için diğer repolar deneniyor")
                        for repo in repos:
                            if save_file_from_repo(lib, repo):
                                n_downloaded += 1
                                success("Kütüphane indirildi: " + lib.id)
                                break

                except Exception as e:
                    error(e)
                    error(traceback.format_exc())

                info1(f"{index}/{n_all} kütüphane denendi")
                info1(
                    f"{n_downloaded} tanesi indirilebildi, {index-n_downloaded} tanesi hata verdi")
        except Exception as e:
            error(e)
            error(traceback.format_exc())


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
