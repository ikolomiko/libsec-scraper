#!/usr/bin/env python3
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from undetected_chromedriver.webelement import WebElement
import urllib.request
import urllib.parse

options = uc.ChromeOptions()
options.add_argument(
    "--no-first-run --no-service-autorun --password-store=basic")
driver = uc.Chrome(options=options, user_data_dir="/tmp/uc/profile")
# must end with a forward slash (/)
download_path = "/home/ikolomiko/libsec/new_libs/"


def main() -> None:
    tag = "ads"
    for i in range(1, 3):
        extract_page(tag, i)
    driver.quit()
    print("done")


def save_file(url: str, package_name: str, version: str) -> None:
    driver.get(url)
    download_link: str = driver.find_element(
        By.XPATH, '//*[@id="maincontent"]/table/tbody/tr[4]/td/a[3]'
    ).get_attribute("href")

    driver.get(download_link)
    filename = package_name + "-" + version + ".aar"
    try:
        urllib.request.urlretrieve(
            download_link + "/" + filename, download_path + filename)
    except:
        try:
            filename = package_name + "-" + version + ".jar"
            urllib.request.urlretrieve(
                download_link + "/" + filename, download_path + filename)
        except:
            print("JAR Bulunamadı:", download_link + "/" + filename)


def extract_all_versions_of(url: str) -> None:
    driver.get(url)
    versions = driver.find_elements(By.CLASS_NAME, "vbtn")
    package_name: str = url.split('/')[-1]

    for version in versions:
        save_file(f"{url}/{version}", package_name, version)


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


if __name__ == "__main__":
    main()
