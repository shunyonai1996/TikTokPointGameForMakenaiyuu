import json
from fastapi import HTTPException
from config import item_points, CURRENT_POINTS_FILE_PATH, ITEM_POINTS_FILE_PATH

def load_points_from_json() -> int:
    with open(CURRENT_POINTS_FILE_PATH, 'r') as f:
        data = json.load(f)
    return data['current_points']

def save_points_from_json(points: int):
    with open(CURRENT_POINTS_FILE_PATH, 'w') as f:
        json.dump({'current_points': points}, f)

def save_new_item(url: str):
    # 新しいアイテムの投げ銭があった場合current_points.jsonに書き込む
    if url not in item_points:
        item_points[url] = 50 #デフォルトは50に設定
        with open(ITEM_POINTS_FILE_PATH, 'w') as f:
            json.dump(item_points, f, indent=4)

def calculate_points(itemCode: str, itemNum: int) -> int:
    current_points = load_points_from_json()
    if itemCode in item_points: # アイテムURLがマッピングリストにあるか確認
        after_calc_point = item_points[itemCode] * itemNum
        current_points += after_calc_point
        save_points_from_json(current_points)
        return current_points
    else:
        save_new_item(itemCode)
        raise HTTPException(status_code=404, detail="Item URL not found")