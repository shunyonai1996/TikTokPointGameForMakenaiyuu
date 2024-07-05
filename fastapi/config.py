import json

CURRENT_POINTS_FILE_PATH = "data/current_points.json"
ITEM_POINTS_FILE_PATH = "data/item_points.json"

# 初期ポイントの設定
initial_points = 100000

# アイテムURLとポイントのマッピングリストを定義
try:
    with open(ITEM_POINTS_FILE_PATH, 'r') as f:
        item_points = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    item_points = {}

# JSONファイルに初期ポイントを保存する（初回のみ実行）
try:
    with open(CURRENT_POINTS_FILE_PATH, 'r') as f:
        current_points = json.load(f)['current_points']
except (FileNotFoundError, json.JSONDecodeError):
    with open(CURRENT_POINTS_FILE_PATH, 'w') as f:
        json.dump({'current_points': initial_points}, f)
    current_points = initial_points