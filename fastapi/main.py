from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from services import calculate_points, save_new_item
from config import total_points


app = FastAPI()

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

global_websockets=[]

# Create a Pydantic model for request body validation
class DonationData(BaseModel):
    userName: str
    itemImgUrl: str
    itemNum: int

# Middleware to add Content-Security-Policy header
async def add_security_headers(request, call_next):
    response = await call_next(request)
    # CSP を設定する
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-eval' 'unsafe-inline' blob: bytedance: data; connect-src *;"
    return response

@app.middleware("http")
async def security_headers_middleware(request, call_next):
    return await add_security_headers(request, call_next)

@app.post("/update_points")
async def update_points(data: DonationData):
    try:
        updated_points = calculate_points(data.itemImgUrl, data.itemNum)
        _global_websockets=global_websockets
        for websocket in _global_websockets:
            try:
                # await websocket.send_text(json.dumps({"total_points": updated_points}))
                await websocket.send_text(json.dumps({"total_points": updated_points, "userName": data.userName, "itemNum": data.itemNum}))
            except Exception as e:
                if websocket in global_websockets:
                    global_websockets.remove(websocket)
        return {"total_points": updated_points}
    except HTTPException as e:
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
            #await websocket.close()

# エンドポイントで現在のポイントを取得する機能（オプション）
@app.get("/current_points")
def current_points():
    return {"total_points": total_points}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)