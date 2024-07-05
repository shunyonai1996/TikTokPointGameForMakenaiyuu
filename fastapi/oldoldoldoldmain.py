from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Create an instance of FastAPI
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

# Create a Pydantic model for request body validation
class Item(BaseModel):
    username: str
    itemCode: str = None
    itemNum: int

# Middleware to add Content-Security-Policy header
async def add_security_headers(request, call_next):
    response = await call_next(request)
    # CSP を設定する
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-eval' 'unsafe-inline' blob: bytedance: data; connect-src *;"
    return response

# Define a POST endpoint to receive JSON data
@app.post("/item")
def create_item(item: Item):
    print(f"Received item: {item}")
    return {"message": "Item received"}

if __name__ == "__main__":
    import uvicorn

    # Run the application with Uvicorn, enabling HTTPS with self-signed certificate
    uvicorn.run(app, host="0.0.0.0", port=8000) 