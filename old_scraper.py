import cloudscraper
from bs4 import BeautifulSoup
import urllib.request, urllib.parse

scraper = cloudscraper.create_scraper()

download_path: str = "" # must end with a /

link = ""


def extract_page(tag: str, n_page: int) -> None:
    tag = urllib.parse.quote(tag.strip().lower())
    link = f"https://mvnrepository.com/search?q={tag}&p={n_page}&c=android"
    page_content = scraper.get(link)
    print(str(n_page) + ": " + str(page_content.status_code))
    soup = BeautifulSoup(page_content.text, 'lxml')
    mydivs = soup.find_all("div", {"class": "im"})
    print(page_content.text)

    
    for div in mydivs:
        link = "https://mvnrepository.com" + div.find('a')['href']
        soup = BeautifulSoup(scraper.get(link).text, 'lxml')
        htmltable = soup.find('table', {'class': 'grid versions'})
        versions = htmltable.findAll('a', {'class': 'vbtn release'})
        for item in versions:
            version = item["href"].split("/")[-1]
            soup = BeautifulSoup(scraper.get(link+"/"+version).text, 'lxml')
            result = soup.find_all("a", string="View All")
            last_url = result[0]["href"]
            last_url_splited = last_url.split("/")

            try:
                last_url = last_url + "/" + \
                    last_url_splited[-2]+"-" + last_url_splited[-1] + ".aar"
                print(last_url)
                file: str = last_url_splited[-2]+"-" + last_url_splited[-1] + ".aar"
                urllib.request.urlretrieve(last_url, filename=download_path + file)
            except:
                try:
                    print("AAR Bulunamadı.")
                    last_url = result[0]["href"]
                    last_url = last_url + "/" + \
                        last_url_splited[-2]+"-" + last_url_splited[-1] + ".jar"
                    print(last_url)
                    file: str = last_url_splited[-2]+"-" + last_url_splited[-1] + ".jar"
                    urllib.request.urlretrieve(last_url, filename=download_path + file)
                except:
                    print("JAR Bulunamadı.")
                    last_url = result[0]["href"]
                    last_url = last_url + "/" + \
                        last_url_splited[-2]+"-" + last_url_splited[-1]
                    print("error: " + last_url)
                    



for i in range(1, 2):
    extract_page("ads", i)

# https://mvnrepository.com/artifact/com.google.android.gms/play-services-adsplay-services-ads/21.0.0

# https://mvnrepository.com/artifact/com.google.android.gms/play-services-ads/21.0.0

# https://maven.google.com/com/google/android/gms/play-services-ads/21.0.0/play-services-ads-21.0.0.aar

# https://repo.spring.io/plugins-release/com/amazon/android/mobile-ads/5.8.1.1/mobile-ads-5.8.1.1.jar
