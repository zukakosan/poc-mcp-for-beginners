from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time
import uvicorn

app = FastAPI()

async def event_stream():
    for i in range(1,10):
        yield f"data: Message {i}\n\n" # 開業を二つにすることで、yield が一行をイベントとして判定
        time.sleep(1)  # Simulate a delay for demonstration
        
@app.get("/stream")
def stream():
    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)