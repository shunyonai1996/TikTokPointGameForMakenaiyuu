from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from services import calculate_points
from config import current_points
import json
import uvicorn
from urllib.parse import urlparse

app = FastAPI()

# Define CORS settings
origins = ["*"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

global_websockets = []

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create a Pydantic model for request body validation
class DonationData(BaseModel):
    userName: str
    userImgUrl: str
    itemCode: str
    itemNum: int

@app.post("/update_points")
async def update_points(data: DonationData, request: Request):
    print("🛜🛜🛜 Req 🛜🛜🛜：", data)

    parsed_url = urlparse(data.userImgUrl) # userImgUrl からドメイン名を抽出
    img_domain = parsed_url.netloc
    print("🖊️🖊️🖊️ img_domain 🖊️🖊️🖊️:", img_domain)

    try:
        updated_points = calculate_points(data.itemCode, data.itemNum)
        _global_websockets = global_websockets[:]
        for websocket in _global_websockets:
            try:
                await websocket.send_text(json.dumps({
                    "current_points": updated_points,
                    "userImgUrl": data.userImgUrl,
                    "userName": data.userName,
                    "itemNum": data.itemNum,
                    "itemCode": data.itemCode
                }))
            except Exception as e:
                if websocket in global_websockets:
                    global_websockets.remove(websocket)

        # 動的に CSP を設定
        response = {
            "current_points": updated_points,
            "userImgUrl": data.userImgUrl,
            "userName": data.userName,
            "itemNum": data.itemNum,
            "itemCode": data.itemCode
        }

        headers = {
            "Content-Security-Policy": (
                f"default-src 'self'; "
                f"img-src 'self' bytedance tiktokcdn.com {img_domain} data:; "
                "style-src 'self' 'unsafe-inline'; "
                "script-src 'self' 'unsafe-inline';"
            )
        }

        return JSONResponse(content=response, headers=headers)
    except HTTPException as e:
        print("❌❌❌ Validation error ❌❌❌:", e.detail)
        raise e

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        global_websockets.append(websocket)
        while True:
            await websocket.receive_text()
    except Exception as e:
        if websocket in global_websockets:
            global_websockets.remove(websocket)
            await websocket.close()

# エンドポイントで現在のポイントを取得する機能（オプション）
@app.get("/current_points")
def current_points():
    return {"current_points": current_points}

# ファビコンを提供するエンドポイント
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)  # No Content

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)