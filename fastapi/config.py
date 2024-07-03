import json

POINTS_FILE_PATH = "data/points.json"
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
    with open(POINTS_FILE_PATH, 'r') as f:
        total_points = json.load(f)['total_points']
except (FileNotFoundError, json.JSONDecodeError):
    with open(POINTS_FILE_PATH, 'w') as f:
        json.dump({'total_points': initial_points}, f)
    total_points = initial_points
