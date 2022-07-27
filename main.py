#!/usr/bin/env python3
from time import sleep
from selenium import webdriver

def main() -> None:
    driver = webdriver.Firefox()
    tag = "ads"
    n_page = 2
    driver.get(f"https://mvnrepository.com/search?q={tag}&p={n_page}&c=android")
    sleep(5)
    driver.close()

if __name__ == '__main__':
    main()