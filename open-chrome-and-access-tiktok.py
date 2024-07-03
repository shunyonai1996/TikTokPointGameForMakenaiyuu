# coding:utf-8
import json
import requests
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def post_data(url, data={}):
    try:
        response = requests.post(
            url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data),
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print('Fetch error:', e)
        raise

def send_item_data(data):
    url = 'http://192.168.1.84/update_points'
    try:
        response = post_data(url, data)
        return response
    except Exception as e:
        print('ERROR:', e)

def replace_img_url_to_img_code(url):
    # 正規表現パターンで不要な部分を取り除く
    # 32文字のハッシュコード、resource/ディレクトリ内の32文字のハッシュコード、特定のファイル名を抽出
    match = re.search(r'(?:resource/)?([a-f0-9]{32})(?:\.png)?|([\w-]+~tplv-obj\.image)', url)
    if match:
        if match.group(1):
            cleaned_code = match.group(1)
        elif match.group(2):
            cleaned_code = match.group(2)
        return cleaned_code
    return url  # パターンに一致しない場合はそのままのURLを返す

def item_observer(driver):
    chat_room = driver.find_elements(By.CSS_SELECTOR, '[data-e2e^="chat-room"]')[0]
    messages = chat_room.find_elements(By.XPATH, './div[1]/div[1]/div')
    item_messages = [message for message in messages if len(message.get_attribute('class')) < 15]
    for message in item_messages:
        print('message:', message)
        items = message.text.split("\n")
        print('items:', items)
        item_img_url = message.find_element(By.XPATH, './div[2]/div/img').get_attribute('src')
        item_code = replace_img_url_to_img_code(item_img_url)
        if item_code:  # item_codeがNoneでないことを確認
            user_name = items[0]
            item_num = items[2].replace("x", "")
            data = {"userName": user_name, "itemImgUrl": item_code, "itemNum": item_num}
            # クラス名を追加
            driver.execute_script("arguments[0].classList.add('item-checked');", message)
            # APIを呼び出す
            print(data)
            send_item_data(data)
        else:
            print(f"想定外のItemImgUrl: {item_img_url}")

# ChromeDriverのパスを指定
chrome_service = Service(executable_path='/usr/local/bin/chromedriver')

# ブラウザを開く
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=chrome_service, options=options)

# ウィンドウをフルスクリーンに設定
driver.maximize_window()

# TikTokの特定のサイトを開く
# driver.get("https://www.tiktok.com/@makenaiyuuu/live")
driver.get("https://www.tiktok.com/@valeria.viral/live")

try:
    # 無限ループで常時起動
    while True:
        try:
            item_observer(driver)
        except:
            print('投げ銭なし')
        time.sleep(3)
except KeyboardInterrupt:
    # Ctrl+Cが押されたときに終了する
    print("Exiting...")
finally:
    pass