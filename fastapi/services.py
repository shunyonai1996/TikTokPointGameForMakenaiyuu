import json
from fastapi import HTTPException

# JSONファイルからポイントを読み込む関数
def load_points() -> int:
    with open(CURRENT_POINTS_FILE_PATH, 'r') as f:
        data = json.load(f)
    return data['current_points']

# JSONファイルにポイントを保存する関数
def save_points(points: int):
    with open(CURRENT_POINTS_FILE_PATH, 'w') as f:
        json.dump({'current_points': points}, f)

# 新しいアイテムURLを保存する関数
def save_new_item(url: str):
    # 新しいアイテムの投げ銭があった場合、新規にcurrent_points.jsonに書き込む
    if url not in item_points:
        item_points[url] = 50
        with open(ITEM_POINTS_FILE_PATH, 'w') as f:
            json.dump(item_points, f, indent=4)

# ポイントの計算処理を行う関数
def calculate_points(itemCode: str, itemNum: int) -> int:
    current_points = load_points()
    # アイテムURLがマッピングリストにあるか確認
    if itemCode in item_points:
        # ポイント計算
        points_change = item_points[itemCode] * itemNum
        current_points += points_change
        save_points(current_points)
        return current_points
    else:
        # 新しいアイテムURLを保存
        save_new_item(itemCode)
        raise HTTPException(status_code=404, detail="Item URL not found")