from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Stdioでサーバと接続する前提のパラメータ
server_params = StdioServerParameters(
    command="mcp",
    args=["run", "server.py"],
    env=None
)

async def run():
    async with stdio_client(server_params) as (read, write):
        # 以下の内容を１セッションとして実行する
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            resources = await session.list_resources()
            print("Available resources:")
            for r in resources:
                print("Resource:", r)
            
            tools = await session.list_tools()
            print("Available tools:")
            for t in tools:
                print("Tool:", t)

            print("READ RESOURCES")
            content, mime_type = await session.read_resource("greeting://Alice")

            print("CALL TOOLS")
            result = await session.call_tool("add", arguments={"a": 1, "b": 8})
            print("Result of add:", result.content[0].text)

            result2 = await session.call_tool("cancat_str", arguments={"str1": "Hello, ", "str2": "World!"})
            print("Result of cancat_str:", result2.content[0].text)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())

