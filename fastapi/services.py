import json
from fastapi import HTTPException
from config import item_points, POINTS_FILE_PATH, ITEM_POINTS_FILE_PATH

# JSONファイルからポイントを読み込む関数
def load_points() -> int:
    with open(POINTS_FILE_PATH, 'r') as f:
        data = json.load(f)
    return data['total_points']

# JSONファイルにポイントを保存する関数
def save_points(points: int):
    with open(POINTS_FILE_PATH, 'w') as f:
        json.dump({'total_points': points}, f)

# 新しいアイテムURLを保存する関数
def save_new_item(url: str):
    # 新しいアイテムの投げ銭があった場合、新規にitem_points.jsonに書き込む
    if url not in item_points:
        item_points[url] = 50
        with open(ITEM_POINTS_FILE_PATH, 'w') as f:
            json.dump(item_points, f, indent=4)

# ポイントの計算処理を行う関数
def calculate_points(itemImgUrl: str, itemNum: int) -> int:
    total_points = load_points()
    # アイテムURLがマッピングリストにあるか確認
    if itemImgUrl in item_points:
        # ポイント計算
        points_change = item_points[itemImgUrl] * itemNum
        total_points += points_change
        save_points(total_points)
        return total_points
    else:
        # 新しいアイテムURLを保存
        save_new_item(itemImgUrl)
        raise HTTPException(status_code=404, detail="Item URL not found")
