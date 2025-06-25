from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MCP-SSE")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# Starlette は ASGI アプリケーションを提供するためのフレームワーク
# ASGI App の Mount を使用して、MCP の SSE アプリケーションをルーティングする
app = Starlette(
    routes=[
        Mount('/',app=mcp.sse_app())
    ]
)
