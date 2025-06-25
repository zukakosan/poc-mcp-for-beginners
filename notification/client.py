# client.py
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
import asyncio
import mcp.types as types
from mcp.shared.session import RequestResponder
import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('mcp_client')

class LoggingCollector:
    def __init__(self):
        self.log_messages: list[types.LoggingMessageNotificationParams] = []
    async def __call__(self, params: types.LoggingMessageNotificationParams) -> None:
        self.log_messages.append(params)
        logger.info("MCP Log: %s - %s", params.level, params.data)

logging_collector = LoggingCollector()
port = 8000

async def message_handler(
    message: RequestResponder[types.ServerRequest, types.ClientResult]
    | types.ServerNotification
    | Exception,
) -> None:
    logger.info("Received message: %s", message)
    if isinstance(message, Exception):
        logger.error("Exeption occurred")
        raise message
    elif isinstance(message, types.ServerNotification):
        logger.info("Received notification: %s", message)
    elif isinstance(message, RequestResponder):
        logger.info("Request Responder: %s", message)
    else:
        logger.info("Server Message: %s", message)
    
async def main():
    logger.info("Starting MCP client")
    async with streamablehttp_client(f"http://localhost:{port}/mcp") as (
        read_stream,
        write_stream,
        session_callback,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
            logging_callback=logging_collector,
            message_handler=message_handler,
        ) as session:
            id_before = session_callback()
            logger.info("Session ID before init %s", id_before)
            logger.info("MCP client session started")
            await session.initialize()
            id_after = session_callback()
            logger.info("Session ID after init %s", id_after)
            logger.info("Session initialized, ready to call tools.")
            # ここでツールを呼び出す（ここが肝）
            # MCP Server 側に "process_file" というツールが定義されていること、その存在を知っていることが前提
            # クライアント側に LLM がある場合は、MCP Server のツールを List Tools で取得して、ツール名を知ることができ、動的にツールを呼び出せるが、この憲章では決め打ち
            tool_result = await session.call_tool("process_files", {"message": "hello from client"})
            logger.info("Tool result: %s", tool_result)
            if logging_collector.log_messages:
                logger.info("Collected log messages:")
                for log in logging_collector.log_messages:
                    logger.info("Log: %s", log)

# mcp サーバを使わない場合に呼び出す
def stream_progress(message="hello", url="http://localhost:8000/stream"):
    """Stream progress from the server."""
    try:
        with requests.get(url, params={"message": message}, stream=True) as r:
            r.raise_for_status()
            logger.info("Streaming in Progress")
        for line in r.iter_lines():
                if line:
                # Decode the line and print it
                    decoded_line = line.decode('utf-8').strip()
                    print(line.decode('utf-8'))
                    logger.info("Received line: %s", decoded_line)
        logger.info("Streaming completed successfully.")
    except requests.RequestException as e:
        logger.error("Error during streaming: %s", e)
        
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        # MCP client mode
        logger.info("Running MCP client...")
        asyncio.run(main())
    else:
        # Classic HTTP streaming client mode
        logger.info("Running classic HTTP streaming client...")
        stream_progress()