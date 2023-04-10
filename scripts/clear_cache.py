import os
import dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# load env
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# configs
chromedriver_path = os.environ["chromedriverPath"]

# instagram param info
BASE_URL = "https://www.instagram.com"


def get_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    if bool(chromedriver_path):
        # for arm64
        return webdriver.Chrome(chromedriver_path, options=chrome_options)
    else:
        # for general
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def main():
    global BASE_URL

    driver = get_chrome_driver()
    driver.implicitly_wait(10)

    driver.get(BASE_URL)
    
    # delete all cookie
    driver.delete_all_cookies()

    # delete all cache
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")

    driver.quit()

    print('success delete_all_cookies')


main()