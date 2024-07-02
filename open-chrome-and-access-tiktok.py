# coding:utf-8
import json
import requests
import time
import sys
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
        response.raise_for_status()  # HTTPエラーをチェック
        return response.json()  # JSONレスポンスを期待
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
    # 不要な部分を取り除く
    item_code = url.replace("https://p16-webcast.tiktokcdn.com/img/maliva/webcast-va/", "").replace("~tplv-obj.png", "")
    return item_code

def item_observer(driver):
    chat_room = driver.find_elements(By.CSS_SELECTOR, '[data-e2e^="chat-room"]')[0]
    messages = chat_room.find_elements(By.XPATH, './div[1]/div[1]/div')
    item_messages = [message for message in messages if len(message.get_attribute('class')) < 15]
    for message in item_messages:
        items = message.text.split("\n")
        item_img_url = message.find_element(By.XPATH, './div[2]/div/img').get_attribute('src')
        item_code = replace_img_url_to_img_code(item_img_url)
        user_name = items[0]
        item_num = items[2].replace("x", "")
        data = {"username": user_name, "itemImgUrl": item_code, "itemNum": item_num}

        # クラス名を追加
        driver.execute_script("arguments[0].classList.add('item-checked');", message)
        # message.classList.add("item-checked")

        # APIを呼び出す
        print(data)
        send_item_data(data)

# ChromeDriverのパスを指定
chrome_service = Service(executable_path='/usr/local/bin/chromedriver')  # 正しいパスを指定

# ブラウザを開く
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=chrome_service, options=options)


# ウィンドウをフルスクリーンに設定
driver.maximize_window()

# TikTokの特定のサイトを開く
# driver.get("https://www.tiktok.com/@makenaiyuuu/live")
driver.get("https://www.tiktok.com/@yuuchimu0820/live")

try:
    # 無限ループで常時起動
    while True:
        try:
            # data = {"username": "user_name", "itemImgUrl": "item_img_url", "itemNum": 0.0}
            # send_item_data(data)
            item_observer(driver)
        except:
            print('投げ銭なし')
        time.sleep(3)
        # pass
except KeyboardInterrupt:
    # Ctrl+Cが押されたときに終了する
    print("Exiting...")
finally:
    # ブラウザを終了する
    # driver.quit()
    pass

