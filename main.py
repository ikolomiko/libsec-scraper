#!/usr/bin/env python3
from typing import List, Set
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from undetected_chromedriver.webelement import WebElement
from tinydb import table, TinyDB
from tinydb.database import Table
import traceback
import re

options = uc.ChromeOptions()
options.add_argument(
    "--no-first-run --no-service-autorun --password-store=basic")
driver = uc.Chrome(
    options=options, user_data_dir="./profile", use_subprocess=True)

# must end with a forward slash (/)
download_path = "./libs/"

old_dbs = ["db.json", "db2.json", "db3.json", "db4.json"]
database = TinyDB('db5.json')
all_ids: Set[str] = set()


class Library:
    def __init__(self) -> None:
        self.artifact_id = ""
        self.group_id = ""
        self.version = ""
        self.repo = ""
        self.usages = 0
        self.date = ""
        self.id = ""
        self.tag = ""
        self.base_url = ""

    def __init__(self, row: WebElement, tag: str, url: str = "") -> None:
        self.artifact_id = ""
        self.group_id = ""
        self.tag = tag

        cols: List[WebElement] = row.find_elements(By.TAG_NAME, "td")

        self.version = str(cols[-5].text)
        self.repo = str(cols[-3].text)
        self.usages = int(cols[-2].text)
        self.date = str(cols[-1].text)
        self.id = str(self.group_id + "+" +
                      self.artifact_id + "+" + self.version)
        self.base_url = url

    def __init__(self, row: WebElement, artifact_id: str, group_id: str, tag: str, url: str = "") -> None:
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

    def __str__(self) -> str:
        return (
            f"Artifact id: {self.artifact_id}\n"
            f"Group id: {self.group_id}\n"
            f"Version: {self.version}\n"
            f"Repo: {self.repo}\n"
            f"Usages: {self.usages}\n"
            f"Date: {self.date}\n"
            f"URL: {self.base_url}"
        )


def remove_suffix(text: str, suffix: str):
    if suffix and text.endswith(suffix):
        return text[:-len(suffix)]
    return text


def extract_num(text: str) -> int:
    r = re.search("\((\d+)\)", text)
    return int(r.group()[1:-1])


def main() -> None:
    keywords_file = open("keywords.txt", "r").readlines()

    for db in old_dbs:
        for item in TinyDB(db).all():
            all_ids.add(str(item['id']))
    for item in database.all():
        all_ids.add(str(item['id']))

    for item in keywords_file:
        print(item)
        if item.startswith("#"):
            continue

        try:
            for i in range(1, 51):
                print(f"Page: {i}")
                extract_page(item.strip(), i)
        except:
            print(traceback.format_exc())

    driver.quit()
    print("done")


def get_download_base_url(url: str, version: str):
    driver.get(f"{url}/{version}")

    download_link: str = driver.find_element(
        By.XPATH, "//*[text()='View All']"
    ).get_attribute("href")

    return remove_suffix(download_link, version)


def save_to_db(lib: Library):
    print(vars(lib))
    print(lib.id)
    all_ids.add(lib.id)
    database.insert(table.Document(vars(lib), lib.id))


def save_to_db_multi(libs: List[table.Document]):
    database.insert_multiple(libs)


def extract_all_versions_of(url: str, tag: str) -> None:
    driver.get(url)

    tab_anchors: List[WebElement] = driver.find_element(
        By.CLASS_NAME, "tabs").find_elements(By.TAG_NAME, "a")
    tab_links = [str(tab.get_attribute("href")) for tab in tab_anchors]

    artifact_id: str = url.split('/')[-1]
    group_id: str = url.split('/')[-2]

    n_versions = sum([extract_num(tab.text) for tab in tab_anchors])
    n_matches = 0
    for id in all_ids:
        if id.startswith(f"{group_id}+{artifact_id}+"):
            n_matches += 1

    print(n_versions, n_matches)

    if n_versions == n_matches:
        return

    n_versions = 0

    for tab in tab_links:
        driver.get(tab)

        rows = driver.find_elements(By.XPATH,
                                    '//*[@id="snippets"]/div/div/div/table/tbody/tr')

        n_versions += len(rows)
        if n_versions == n_matches:
            print("Quick return")
            return

        libraries = [Library(row, artifact_id, group_id, tag) for row in rows]
        base_url: str = None

        items_to_save: List[table.Document] = []

        for lib in libraries:
            if lib.id in all_ids:
                continue

            if base_url == None:
                base_url = get_download_base_url(url, lib.version)

            lib.base_url = base_url
            print(lib.id, lib.tag, sep="\t")
            all_ids.add(lib.id)
            items_to_save.append(table.Document(vars(lib), lib.id))

        try:
            save_to_db_multi(items_to_save)
        except Exception as e:
            print("Couldn't save to db", e)
            print(traceback.format_exc())


def extract_page(tag: str, n_page: int) -> None:
    base_url = f"https://mvnrepository.com/search?q={tag}&p={n_page}&c=android"
    driver.get(base_url)
    libraries: List[WebElement] = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "im-title"))
    )
    driver.execute_script("window.stop();")
    urls: List[str] = []
    for lib in libraries:
        lib_link: WebElement = lib.find_elements(By.TAG_NAME, "a")[0]
        url: str = lib_link.get_attribute("href")
        urls.append(url)
    for url in urls:
        print(url)
        extract_all_versions_of(url, tag)


class StringIdClassTable(Table):
    document_id_class = str


if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
