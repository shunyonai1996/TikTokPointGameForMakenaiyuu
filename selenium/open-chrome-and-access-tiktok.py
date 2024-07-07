# coding:utf-8
import json
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config import item_data, STOCK_ITEM_DATA


def send_item_data(data):
    url = 'http://192.168.1.84/update_points'
    try:
        response = post_data(url, data)
        return response
    except Exception as e:
        print('ERROR:', e)

# def post_data(url, data):
#     try:
#         response = requests.post(
#             url,
#             headers={'Content-Type': 'application/json'},
#             data=json.dumps(data),
#             timeout=10
#         )
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print('Fetch error:', e)
#         raise

def post_data(url, data):
    try:
        # Ensure data is properly encoded as JSON
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json; charset=utf-8'},
            data=json.dumps(data, ensure_ascii=False).encode('utf-8'),  # Ensure ASCII characters are not escaped
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print('Fetch error:', e)
        raise

def replace_img_url_to_img_code(url):
    match = re.search(r'(?:(?:resource/)?([a-f0-9]{32})|(?:[\w-]+/)([\w-]+)(?:\.\w+)?~tplv-obj(?:\.\w+)?|([\w-]+)~tplv-obj\.\w+)', url)
    if match:
        if match.group(1):
            cleaned_code = match.group(1)
        elif match.group(2):
            cleaned_code = match.group(2)
        return cleaned_code
    return url

# 新しいアイテムURLを保存する関数
def save_new_item(url: str):
    if url not in item_data:
        item_data.append(url)
        with open(STOCK_ITEM_DATA, 'w') as f:
            json.dump(item_data, f, indent=4)

def item_observer(driver):
    chat_room = driver.find_elements(By.CSS_SELECTOR, '[data-e2e^="chat-room"]')[0]
    messages = chat_room.find_elements(By.XPATH, './div[1]/div[1]/div')
    item_messages = [message for message in messages if len(message.get_attribute('class')) < 15]
    for message in item_messages:
        items = message.text.split("\n")
        user_img_url = message.find_element(By.XPATH, './div[1]/img').get_attribute('src')
        item_img_url = message.find_element(By.XPATH, './div[2]/div/img').get_attribute('src')
        item_code = replace_img_url_to_img_code(item_img_url)
        user_name = items[0]
        item_num = int(items[2].replace("x", ""))
        data = {
            "userName": user_name,
            "userImgUrl": user_img_url,
            "itemCode": item_code,
            "itemNum": item_num
        }

        driver.execute_script("arguments[0].classList.add('item-checked');", message)
        print("🛜🛜🛜 RequestData 🛜🛜🛜：", data)
        print("🎱🎱🎱 item_code 🎱🎱🎱：", item_code)
        send_item_data(data)
        save_new_item(item_img_url) # 新しいアイテムURLを保存

# ChromeDriverのパスを指定
chrome_service = Service(executable_path='/usr/local/bin/chromedriver')

# ブラウザを開く
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=chrome_service, options=options)
driver.maximize_window() # windowをfull screenに設定

# TikTokの特定のサイトを開く
# driver.get("https://www.tiktok.com/@makenaiyuuu/live")
driver.get("https://www.tiktok.com/@masyumaro0516/live")

try:
    # 無限ループで常時起動
    while True:
        try:
            item_observer(driver)
        except:
            print('⚠️⚠️⚠️⚠️⚠️ 投げ銭なし ⚠️⚠️⚠️⚠️⚠️')
        time.sleep(5)
except KeyboardInterrupt:
    # Ctrl+Cが押されたときに終了する
    print("Exiting...")
finally:
    pass
