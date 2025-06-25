from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import (
    TextContent
)
import asyncio
import uvicorn
import os

mcp = FastMCP("Stream Notification Server")

app = FastAPI()

@app.get("/",response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

async def event_stream(message: str):
    for i in range(1,10):
        yield f"Processing item {i}/10 \n\n"
        await asyncio.sleep(1)
    yield "Done!: {message} \n\n"

@app.get("/stream")
async def stream(message: str="hello"):
    """stream a massage"""
    return StreamingResponse(event_stream(message), media_type="text/plain")

@mcp.tool(description="A tool that simulates file processing and sends notifications.")
async def process_files(message: str, ctx: Context) -> TextContent:
    """Simulate file processing and send notifications."""
    files = [f"file_{i}.txt" for i in range(1,10)]
    # enumerate() は何をするか
    # files の要素を一つずつ取り出し、インデックスとともに処理する
    # ここでは、ファイル名を表示し、1秒待機する
    for idx, file in enumerate(files):
        # len(files) の長さのうち、idx + 1 番目のファイルを処理していることを示すメッセージを送信
        await ctx.info(f"processing {file} ({idx + 1}/{len(files)})")
        await asyncio.sleep(1)
    await ctx.info("All files processed successfully!")
    return TextContent(text=f"All files processed successfully! {message}", type="text/plain")


if __name__ == "__main__":
    import sys
    # LLM を介して、呼び出す場合は、Tool を使えるので、mcp を使う
    if "mcp" in sys.argv:
        print("Running with MCP")
        mcp.run(transport="streamable-http")
    else:
        # シンプルに FastAPI サーバとして StreamingResponse を使う場合
        print("Starting FastAPI server")
        uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)