import os
import dotenv
import time
import secrets
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# load env
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# configs
chromedriver_path = os.environ["chromedriverPath"]
account = {
    'id': os.environ["instagramId"],
    'pw': os.environ["instagramPassword"],
}

def get_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # for general
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # for arm64
    # return webdriver.Chrome(chromedriver_path, options=chrome_options)

def get_google_uri(keyword):
    return f"https://www.google.com/search?q={keyword}&tbm=isch"

def write_image(name, data):
    filename = f"datasets/image/{name}.jpg"
    with  open(filename, "wb") as f:
        f.write(data)

def write_text(name, data):
    filename = f"datasets/text/{name}.txt"
    f = open(filename, "wb")
    f.write(data)
    f.close()
    
def write_dataset(image_uri, text):
    name = secrets.token_hex(nbytes=16)

    # image data
    image_data = requests.get(image_uri).content
    write_image(name, image_data)

    # text data
    write_text(name, text.encode('utf-8'))

def main():
    search_keyword = input("input keyword: ")

    driver = get_chrome_driver()
    driver.get(get_google_uri(search_keyword))

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    for i, data_el in enumerate(soup.select('div[data-id]')):
        img_el = data_el.select_one('img[data-src]')
        if not img_el:
            continue

        print(img_el['data-src'])
        print(img_el['alt'])
        print('\n')
        write_dataset(img_el['data-src'], img_el['alt'])
main()
