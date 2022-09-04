from typing import List
from undetected_chromedriver.webelement import WebElement
from selenium.webdriver.common.by import By
from metadata import LibMetadata, Repo, Version


class Library():
    def __init__(self, row: WebElement = None, artifact_id: str = "", group_id: str = "", tag: str = "", url: str = "", d: dict = None) -> None:
        if row != None:
            self.artifact_id = artifact_id
            self.group_id = group_id
            self.tag = tag

            cols: List[WebElement] = row.find_elements(By.TAG_NAME, "td")

            self.version = str(cols[-5].text)
            self.repo = str(cols[-3].text)
            self.usages = int(cols[-2].text)
            self.date = str(cols[-1].text)
            self.id = str(self.group_id + "+" +
                          self.artifact_id + "+" + self.version)
            self.base_url = url

        else:
            self.artifact_id = ""
            self.group_id = ""
            self.version = ""
            self.repo = ""
            self.usages = 0
            self.date = ""
            self.id = ""
            self.tag = ""
            self.base_url = ""

            if d != None:
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
        return isinstance(__o, Library) and self.id == __o.id

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def __hash__(self) -> int:
        return hash(self.id)


class MultiRepoLibrary:
    def __init__(self, libmetadata: LibMetadata, repo: Repo, version: Version) -> None:
        self.artifact_id = libmetadata.artifact_id
        self.group_id = libmetadata.group_id
        self.version = version.version
        self.date = version.version
        self.usages = version.usages
        self.tag = libmetadata.tag
        self.id = libmetadata.id + "+" + version.version
        self.repos: List[Repo] = [repo]

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, MultiRepoLibrary) and self.id == __o.id

    def __ne__(self, __o: object) -> bool:
        return not self.__eq__(__o)

    def __hash__(self) -> int:
        return hash(self.id)
