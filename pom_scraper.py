#!/usr/bin/env python3

import json
import os
from pathlib import Path
from metadata import LibMetadata, Repo, Version
import urllib.request
import urllib.parse
from log import info1, info2, warn, error, success, log
from xml.etree import ElementTree as ET
from metadata_scraper import get_all_repos


def download_pom(base_url: str, body_url: str, path: str) -> bool:
    path = path + "pom.xml"

    if base_url[-1] != '/':
        base_url = base_url + "/"

    try:
        urllib.request.urlretrieve(base_url+body_url, path)
        data = Path(path).read_text()
        if len(data.strip()) == 0:
            raise Exception("Empty file")

        ET.fromstringlist(data)

        success(f"{path} successfully downloaded", False)
        return True
    except Exception as e:
        try:
            os.remove(path)
        except:
            pass
        return False


def main() -> None:
    l = sum([1 for x in Path("./libdata/").iterdir()])
    all_repos = get_all_repos().values()
    for ind, dir in enumerate(Path("./libdata/").iterdir()):
        info1(f"{ind}/{l}", False)
        if dir.is_file():
            continue

        for file in dir.iterdir():
            if file.name != "metadata.json":
                continue

            try:
                data = json.loads(file.open(mode="r").read())
                m = LibMetadata(data)
                for repo in m.repos:
                    for version in repo.versions:
                        if not version.downloaded:
                            continue

                        pom_path = f"./poms/{m.group_id}/{m.artifact_id}/{version.version}/"
                        if Path(pom_path + "pom.xml").is_file():
                            continue

                        Path(pom_path).mkdir(parents=True, exist_ok=True)
                        body_url = f"{m.group_id.replace('.','/')}/{m.artifact_id}/{version.version}/{m.artifact_id}-{version.version}.pom"
                        base_url = repo.base_url

                        if not download_pom(base_url, body_url, pom_path):
                            flag = False
                            for repo in all_repos:
                                if download_pom(repo.base_url, body_url, pom_path):
                                    flag = True
                                    break

                            if not flag:
                                error(f"Could not get {pom_path=}")

            except Exception as e:
                print(file)
                print(e)
                exit()


if __name__ == '__main__':
    main()
