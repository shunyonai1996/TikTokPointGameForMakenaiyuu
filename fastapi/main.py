import json
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services import calculate_points
from config import total_points

app = FastAPI()

# Define CORS settings
origins = [
    "*",
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
    username: str
    itemImgUrl: str
    itemNum: int

# WebSocket管理クラス
# class ConnectionManager:
#     def __init__(self):
#         self.active_connections: List[WebSocket] = []

#     async def connect(self, websocket: WebSocket):
#         await websocket.accept() 
#         self.active_connections.append(websocket)

#     def disconnect(self, websocket: WebSocket):
#         self.active_connections.remove(websocket)

#     async def broadcast(self, message: str):
#         for connection in self.active_connections:
#             await connection.send_text(message)

# manager = ConnectionManager()

# Middleware to add Content-Security-Policy header
async def add_security_headers(request, call_next):
    response = await call_next(request)
    # CSP を設定する
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-eval' 'unsafe-inline' blob: bytedance: data; connect-src *;"
    return response

@app.middleware("http")
async def security_headers_middleware(request, call_next):
    return await add_security_headers(request, call_next)

# seleniumからのPOSTリクエスト検知
@app.post("/update_points")
async def update_points(data: DonationData):
    # try:
    if True:
        updated_points = None
        
        if len(global_websockets)>0:
            updated_points = calculate_points(data.itemImgUrl, data.itemNum)
        for websocket in global_websockets:
            try:
                if True:
                    await websocket.send_text(json.dumps({"total_points": updated_points}))
            except Exception as e:
                global_websockets=list(filter(lambda w:w != websocket), global_websockets)
                await websocket.close()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            global_websockets.append(websocket)
            await websocket.receive_text()
    except Exception as e:
        global_websockets=list(filter(lambda w:w != websocket), global_websockets)
        await websocket.close()

# エンドポイントで現在のポイントを取得する機能（オプション）
@app.get("/current_points")
def current_points():
    return {"total_points": total_points}

if __name__ == "__main__":
    import uvicorn

    # Run the application with Uvicorn, enabling HTTPS with self-signed certificate
    uvicorn.run(app, host="0.0.0.0", port=8000)
