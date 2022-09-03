#!/usr/bin/env python3
import json
from metadata import LibMetadata
from pathlib import Path
from log import success

def main():
    for ind, dir in enumerate(Path("./libdata/").iterdir()):
        if dir.is_file():
            continue

        for file in dir.iterdir():
            if file.name != "metadata.json":
                continue

            try:
                data = json.loads(file.open(mode="r").read())
                m = LibMetadata(data)
                for repo in m.repos:
                    repo.versions = sorted(list(set(repo.versions)), key=lambda x: x.version)

                Path("./libdata2/" + m.id).mkdir(parents=True, exist_ok=True)
                out = json.dumps(m.serialize(), indent=4)
                with open("./libdata2/" + m.id + "/metadata.json", 'w') as o:
                    o.write(out)
            except Exception as e:
                print(file)
                print(e)
                exit()

        success(f"{ind}/22199")

if __name__ == "__main__":
    main()