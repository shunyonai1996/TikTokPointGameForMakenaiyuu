import json

STOCK_ITEM_DATA = "stock_item_data.json"

# アイテムURLのマッピングリストを定義
try:
    with open(STOCK_ITEM_DATA, 'r') as f:
        item_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    item_data = []
