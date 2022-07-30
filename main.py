#!/usr/bin/env python3
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from undetected_chromedriver.webelement import WebElement
import urllib.request
import urllib.parse
import json
from tinydb import table, TinyDB, Query
from tinydb.database import Document, Table

options = uc.ChromeOptions()
options.add_argument(
    "--no-first-run --no-service-autorun --password-store=basic")
driver = uc.Chrome(options=options, user_data_dir="/Users/betul/Desktop/libsec-scraper/profile",use_subprocess=True)

# must end with a forward slash (/)
download_path = "/Users/betul/Desktop/libsec-scraper/libs"

keywords_file = open("keywords.txt", "r").readlines()

database = TinyDB('db.json')
table_libraries = database.table('libraries')

class Library:
    def __init__(self) -> None:
        self.artifact_id = ""
        self.group_id = ""
        self.version = ""
        self.repo = ""
        self.usages = 0
        self.date = ""
        self.id = ""

    def __init__(self, row: WebElement) -> None:
        self.artifact_id = ""
        self.group_id = ""

        cols: List[WebElement] = row.find_elements(By.TAG_NAME, "td")

        self.version = str(cols[-5].text)
        self.repo = str(cols[-3].text)
        self.usages = int(cols[-2].text)
        self.date = str(cols[-1].text)
        self.id = str(self.repo+"."+self.group_id+"."+self.artifact_id+"."+self.version)

    def __init__(self, row: WebElement, artifact_id: str, group_id: str) -> None:
        self.artifact_id = artifact_id
        self.group_id = group_id

        cols: List[WebElement] = row.find_elements(By.TAG_NAME, "td")

        self.version = str(cols[-5].text)
        self.repo = str(cols[-3].text)
        self.usages = int(cols[-2].text)
        self.date = str(cols[-1].text)
        self.id = str(self.repo+"."+self.group_id+"."+self.artifact_id+"."+self.version)

    def __str__(self) -> str:
        return (
            f"Artifact id: {self.artifact_id}\n"
            f"Group id: {self.group_id}\n"
            f"Version: {self.version}\n"
            f"Repo: {self.repo}\n"
            f"Usages: {self.usages}\n"
            f"Date: {self.date}\n"
        )



def main() -> None:
    for item in keywords_file:
        for i in range(1, 51):
            extract_page(item.strip(), i)
        driver.quit()
        print("done")


def get_download_base_url(url: str, version: str):
    driver.get(f"{url}/{version}")

    download_link: str = driver.find_element(
        By.XPATH, "//*[text()='View All']"
    ).get_attribute("href")

    return download_link.removesuffix(version)


def save_file(base_url: str, artifact_id: str, version: str, lib: Library) -> None:
    base_url = base_url + version + "/"
    filename = artifact_id + "-" + version + ".aar"
    try:
        urllib.request.urlretrieve(
            base_url + filename, download_path + filename)
        saveLib(lib)
    except:
        try:
            filename = artifact_id + "-" + version + ".jar"
            urllib.request.urlretrieve(
                base_url + filename, download_path + filename)
            saveLib(lib)
        except:
            print("JAR Bulunamadı:", base_url + filename)


def saveLib(lib: Library):
    print(lib.__dict__)
    print(lib.id)
    Libraries = Query()
    database.upsert(table.Document(lib.__dict__, lib.id), Libraries.id == lib.id)
   

def extract_all_versions_of(url: str) -> None:
    driver.get(url)

    tab_anchors: List[WebElement] = driver.find_element(
        By.CLASS_NAME, "tabs").find_elements(By.TAG_NAME, "a")
    tab_links = [str(tab.get_attribute("href")) for tab in tab_anchors]

    for tab in tab_links:
        driver.get(tab)

        artifact_id: str = url.split('/')[-1]
        group_id: str = url.split('/')[-2]
        rows = driver.find_elements(By.XPATH,
                                    '//*[@id="snippets"]/div/div/div/table/tbody/tr')
        libraries = [Library(row, artifact_id, group_id) for row in rows]

  
        base_url: str = None

        for lib in libraries:
            if base_url == None:
                base_url = get_download_base_url(url, lib.version)

            save_file(base_url, lib.artifact_id, lib.version, lib)

            """ Debug code ahead
            print(lib)
            print("-----------------------------------------")

            """


def extract_page(tag: str, n_page: int) -> None:
    base_url = f"https://mvnrepository.com/search?q={tag}&p={n_page}&c=android"
    try:
        driver.get(base_url)
        libraries: List[WebElement] = WebDriverWait(driver, 10).until(
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
            extract_all_versions_of(url)

    except Exception as e:
        print("error", e)
        driver.quit()
        exit(1)



class StringIdClassTable(Table):
    document_id_class = str
        
if __name__ == "__main__":
    TinyDB.table_class = StringIdClassTable
    main()
  
