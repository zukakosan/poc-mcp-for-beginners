from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# llm
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential  # Azure認証用
import json

# Stdioでサーバと接続する前提のパラメータ
server_params = StdioServerParameters(
    command="mcp",
    args=["run", "server.py"],
    env=None
)

def call_llm(prompt, functions):
    endpoint = os.environ.get("AOAI_ENDPOINT")
    api_key = os.environ.get("AOAI_API_KEY")
    model_name = "gpt-4.1"

    # AOAI Client initialization with AzureKeyCredential
    client = ChatCompletionsClient(
        endpoint="https://aoai-scus.openai.azure.com/openai/deployments/gpt-4.1",
        credential=AzureKeyCredential(api_key),
        # 2024-06-01 以降のバージョンを使用しないとツールの使用を強制できないため固定する
        api_version="2024-10-01-preview" 
    )
        
    print("CALLING LLM")
    # LLMへのリクエストを作成
    response = client.complete(
        messages = [
            {
            "role": "system",
            "content": "Always You have to think of using tools instead of thinking by yourself."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model=model_name,
        # 利用可能な tools として functions[] を与えている
        tools=functions,
        # LLM は簡単な問題は自分で解決してしまい検証にならないためツールの使用を強制
        tool_choice="required",
        temperature=1.0,
        max_tokens=1000,
        top_p=1.0
    )
    # LLMからの応答を取得
    # tools を与えると、レスポンスに tool_calls フィールドが含まれる
    # if LLM response contains tool_calls field, it doesn't provide a direct answer
    # 使用するべき tool と、その arguments として何を与えるべきか(プロンプトから判断したもの)を返す
    response_message = response.choices[0].message
    # いったんレスポンスの内容を表示
    print("response choices:", response.choices)
    
    print("response message: ", response_message)
    
    # 使用するべきツールの情報を抽出
    functions_to_call = []
    if response_message.tool_calls:
        for tool_call in response_message.tool_calls:
            print("Tool: ", tool_call)
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            functions_to_call.append({"name": name, "args": args})
        print("Functions to call:", functions_to_call)
    return functions_to_call

# MCP Server から得られた (list_tools) のツールの情報を ChatCompletionsClient の 引数に合うように変換
# ex. 
def convert_to_llm_tool(tool):
    tool_scheme = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"]
            }
        }
    }
    return tool_scheme

async def run():
    async with stdio_client(server_params) as (read, write):
        # 以下の内容を１セッションとして実行する
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            resources = await session.list_resources()
            print("Available resources:")
            for resource in resources:
                print("Resource:", resource)
            
            tools = await session.list_tools()
            print("Available tools:", tools)
            # ex: Available tools: meta=None nextCursor=None tools=[Tool(name='add', description='Add two numbers.', inputSchema={'properties': {'a': {'title': 'A', 'type': 'integer'}, 'b': {'title': 'B', 'type': 'integer'}}, 'required': ['a', 'b'], 'title': 'addArguments', 'type': 'object'}, annotations=None), Tool(name='cancat_str', description='concatenate two strings.', inputSchema={'properties': {'str1': {'title': 'Str1', 'type': 'string'}, 'str2': {'title': 'Str2', 'type': 'string'}}, 'required': ['str1', 'str2'], 'title': 'cancat_strArguments', 'type': 'object'}, annotations=None)]

            # The array to input tool details 
            functions = []

            for tool in tools:
                print("Tool:", tool)
                if not isinstance(tool, tuple) and hasattr(tool, 'inputSchema'):
                    print("Tool properties:", tool.inputSchema["properties"])
                    functions.append(convert_to_llm_tool(tool))

            prompt = "Add 2 to 20"
            
            functions_to_call = call_llm(prompt, functions)
            
            # functions_to_call は LLM からの応答で、呼び出すべき tool の [{名前}、{引数}] を表す配列
            # 順番に tool を呼び出していく
            # ex. [{'name': 'Add', 'arguments': {'a': 2, 'b': 20}}]
            for f in functions_to_call:
                result = await session.call_tool(f["name"], arguments=f["args"])
                print("Tools result: ", result.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())

