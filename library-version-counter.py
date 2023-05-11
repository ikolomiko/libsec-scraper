#!/usr/bin/env python3
import json
from metadata import LibMetadata
from pathlib import Path
import operator

def main():
    nversions = dict()
    for ind, dir in enumerate(Path("./libdata/").iterdir()):
        if dir.is_file():
            continue

        for file in dir.iterdir():
            if file.name != "metadata.json":
                continue

            try:
                data = json.loads(file.open(mode="r").read())
                m = LibMetadata(data)
                versions = set()
                for repo in m.repos:
                    for ver in repo.versions:
                        versions.add(ver.version)

                nversions[m.id] = len(versions)


            except Exception as e:
                print(file)
                print(e)
                exit()

        print(f"\r{ind+1}/22200", end="")

    print("\n")

    sorted_vers = sorted(nversions.items(), key=operator.itemgetter(1), reverse=True)
    total_vers = 0
    with open("library-versions.csv", mode="w") as file:
        for (name, nvers) in sorted_vers:
            total_vers += nvers
            file.write(f'"{name}", {nvers}\n')

    median = sorted_vers[11100][1]
    average = total_vers / 22200
    max_vers = sorted_vers[0][1]

    print(f"{total_vers = }")
    print(f"{max_vers   = }")
    print(f"{average    = :.2f}")
    print(f"{median     = }")

    

if __name__ == "__main__":
    main()