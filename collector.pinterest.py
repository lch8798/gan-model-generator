import os
import json
import dotenv
import secrets
import requests

# load env
dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

# configs
chromedriver_path = os.environ["chromedriverPath"]
account = {
    'id': os.environ["instagramId"],
    'pw': os.environ["instagramPassword"],
}

# pinterest param info
BASE_URL = "https://www.pinterest.co.kr/resource/BaseSearchResource/get/?"
MAX = 60
ONCE_SIZE = 20 # max 250 (2023-03-21)

def get_uri(keyword):
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
    
def get_params(keyword, bookmark):
    global ONCE_SIZE
    return '{"options":{"page_size":' + str(ONCE_SIZE) + ',"query":"' + keyword + '","scope":"pins","bookmarks":["' + bookmark + '"],"field_set_key":"unauth_react","no_fetch_context_on_resource":false},"context":{}}'.strip()


def main():
    global BASE_URL
    bookmark = "" # page
    
    search_keyword = input("input keyword: ")
    
    for i in range((MAX / ONCE_SIZE).__ceil__()):
        r = requests.get(BASE_URL, params={ "data": get_params(search_keyword, bookmark) })
        json_data = json.loads(r.content)
        resource_response = json_data["resource_response"]
        data = resource_response["data"]
        bookmark = resource_response["bookmark"]
        results = data["results"]
        for v in results:
            img_url = v["images"]["orig"]["url"]
            name = v["title"] or search_keyword
            
            print(name)
            print(img_url)
            print('\n')
            write_dataset(img_url, name)

main()
