import os
import dotenv
import json
import time
import secrets
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from dataclasses import dataclass
from typing import Dict, List, Any

# load env
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# configs
chromedriver_path = os.environ["chromedriverPath"]
ACCOUNT = {
    'id': os.environ["instagramId"],
    'pw': os.environ["instagramPassword"],
}

# pinterest param info
BASE_URL = "https://www.instagram.com"
MAX = 120

@dataclass
class Section(dict):
    layout_content: List[Any]
    
    
@dataclass
class Sections(dict):
    more_available: bool
    next_max_id: str
    next_media_ids: List[str]
    next_page: int
    sections: Dict['layout_content', List[Section]]
    

@dataclass
class First(dict):
    top: Sections
    recent: Sections


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


def write_image(name, data):
    dir = "datasets/image"
    if not os.path.exists(dir):
        os.makedirs(dir)
        
    filename = f"{dir}/{name}.jpg"
    with  open(filename, "wb") as f:
        f.write(data)


def write_text(name, data):
    dir = "datasets/text"
    if not os.path.exists(dir):
        os.makedirs(dir)
            
    filename = f"{dir}/{name}.txt"
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

    
def get_params(keyword):
    global ONCE_SIZE
    return '{"tag_name":' + keyword + '}'


def fetch_cookies() -> List[Any]:
    global BASE_URL
    global ACCOUNT
    
    driver = get_chrome_driver()
    driver.implicitly_wait(10)

    driver.get(BASE_URL)
    
    time.sleep(1)

    id_inp = driver.find_element('xpath', '//*[@id="loginForm"]/div/div[1]/div/label')
    id_inp.click()
    id_inp.send_keys(ACCOUNT['id'])

    pw_inp = driver.find_element('xpath', '//*[@id="loginForm"]/div/div[2]/div/label')
    pw_inp.click()
    pw_inp.send_keys(ACCOUNT['pw'])

    log_btn = driver.find_element('xpath', '//*[@id="loginForm"]/div/div[3]/button')
    log_btn.click()

    time.sleep(10)

    page_source = driver.page_source
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(page_source)

    cookies = driver.get_cookies()
    
    # get csrf token
    csrf_token_start = page_source.find('{"csrf_token":"') + len('{"csrf_token":"')
    csrf_token_end = page_source.find('","viewerId":"')
    csrf_token = page_source[csrf_token_start:csrf_token_end]

    # get X-IG-App-ID
    ig_app_id_start = page_source.find('{"X-IG-App-ID":"') + len('{"X-IG-App-ID":"')
    ig_app_id_end = page_source.find('","X-IG-D":"www"}')
    ig_app_id = page_source[ig_app_id_start:ig_app_id_end]

    return cookies, ig_app_id
    

def fetch_first(cookies, ig_app_id, keyword: str):
    global BASE_URL
    
    cookies_dict = { cookie['name']: cookie['value'] for cookie in cookies }
    r = requests.get(f"{BASE_URL}/api/v1/tags/web_info/?", headers={ 'x-ig-app-id': ig_app_id }, cookies=cookies_dict, params={ 'tag_name': keyword } )
    json_data = json.loads(r.content)
    
    return json_data['data']

def fetch_data(cookies, ig_app_id, params, keyword: str):
    global BASE_URL
    
    cookies_dict = { cookie['name']: cookie['value'] for cookie in cookies }
    r = requests.post(f"{BASE_URL}/api/v1/tags/{keyword}/sections/", headers={ 'x-ig-app-id': ig_app_id }, cookies=cookies_dict, params=params )
    json_data = json.loads(r.content)
    
    return json_data
    

def parse_sections(sections):
    contents = []
    for s in sections:
        for m in s['layout_content']['medias']:
            if 'image_versions2' in m['media']:
                contents.append({
                    'img': m['media']['image_versions2']['candidates'][0]['url'],
                    'text': m['media']['caption']['text'] if m['media']['caption'] is not None else '',
                    'conments': [c['text'] for c in m['media']['caption']['comments']] if m['media']['caption'] is not None and 'comments' in m['media']['caption'] else [],
                    'predicted': m['accessibility_caption'] if 'accessibility_caption' in m else '',
                })
                
            if 'carousel_media' in m['media']:
                for c in m['media']['carousel_media']:
                    contents.append({
                        'img': c['image_versions2']['candidates'][0]['url'],
                        'text': m['media']['caption']['text'] if m['media']['caption'] is not None else '',
                        'conments': [c['text'] for c in m['media']['caption']['comments']] if m['media']['caption'] is not None and 'comments' in m['media']['caption'] else [],
                        'predicted': m['accessibility_caption'] if 'accessibility_caption' in m else '',
                    })
    return contents
    

def main():
    global BASE_URL

    tab = 'top' # 'top' | 'recent'
    contents = []
    
    search_keyword = input("input keyword: ")
    
    # fetch cookies
    cookies, ig_app_id = fetch_cookies()
    print('login success')
    
    # fetch first content
    first = fetch_first(cookies, ig_app_id, search_keyword)
    
    # merge list
    contents = [*contents, *parse_sections(first[tab]['sections'])]
    print(f"fetch [{MAX if len(contents) > MAX else len(contents)}/{MAX}]")
    
    if not first[tab]['more_available']:
        print(f"{tab} more_available is False")
        
        # save datasets
        i = 0
        for c in contents:
            i += 1
            
            img_url = c['img']
            text = f"{c['text']}\n{c['predicted']}"
            
            write_dataset(img_url, text if text is not None else search_keyword)
            
            print(f"download [{i}/{MAX}]")

        return

    # next param struct
    next_param = {
        'include_persistent': 0,
        'surface': 'grid',
        'tab': tab,
        'page': None,
        'max_id': None,
        'next_media_ids': None,
    }
    
    # set next param
    next_param['page'] = first[tab]['next_page']
    next_param['max_id'] = first[tab]['next_max_id']
    next_param['next_media_ids'] = first[tab]['next_media_ids']

    # fetch datas
    while True:
        if len(contents) > MAX:
            break
        
        # fetch data
        data = fetch_data(cookies, ig_app_id, next_param, search_keyword)
        
        # parse datas
        print(data)
        sections = parse_sections(data['sections'])
        contents = [*contents, *sections]
        print(f"fetch [{MAX if len(contents) > MAX else len(contents)}/{MAX}]")
        
        # set next param
        next_param['page'] = data['next_page']
        next_param['max_id'] = data['next_max_id']
        next_param['next_media_ids'] = data['next_media_ids']
        
    # max length
    contents = contents[:MAX]
    
    # save datasets
    i = 0
    for c in contents:
        i += 1
        
        img_url = c['img']
        text = f"{c['text']}\n{c['predicted']}"
        
        write_dataset(img_url, text if text is not None else search_keyword)
        
        print(f"download [{i}/{MAX}]")

main()
