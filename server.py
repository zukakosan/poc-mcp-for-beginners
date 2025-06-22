from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Test-MCP")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

@mcp.tool()
def cancat_str(str1: str, str2: str) -> str:
    """concatenate two strings."""
    return str1 + str2

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a greeting message."""
    return f"Hello, {name}!"
