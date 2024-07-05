from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from services import calculate_points
from config import current_points
import json
import uvicorn

app = FastAPI()

# 静的ファイル表示
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define CORS settings
origins = [
  "*"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

global_websockets = []

# Create a Pydantic model for request body validation
class DonationData(BaseModel):
    userName: str
    userImgUrl: str
    itemCode: str
    itemNum: int

# Middleware to add Content-Security-Policy header
async def add_security_headers(request, call_next):
    response = await call_next(request)
    # CSP を設定する
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' bytedance tiktokcdn.com data:; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline';"
    )
    return response

@app.middleware("http")
async def security_headers_middleware(request, call_next):
    return await add_security_headers(request, call_next)

@app.post("/update_points")
async def update_points(data: DonationData):
    print("received data:", data)
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
        return {"current_points": updated_points}
    except HTTPException as e:
        print("Validation error:", e.json())
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