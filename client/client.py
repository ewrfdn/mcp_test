import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv
import os
from openai import AzureOpenAI
import json

load_dotenv()  # 从 .env 加载环境变量

endpoint = "openai-api-bocchi.openai.azure.com"
deployment_id = "gpt-4o"
api_version = "2025-01-01-preview"
url = "https://openai-api-bocchi.openai.azure.com"


client = AzureOpenAI(
    azure_endpoint=url,
    azure_deployment=deployment_id,
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=api_version,
)

# response = client.chat.completions.create(
#     model=deployment_id,  # model = "deployment_name".
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
#         {
#             "role": "assistant",
#             "content": "Yes, customer managed keys are supported by Azure OpenAI.",
#         },
#         {"role": "user", "content": "Do other Azure AI services support this too?"},
#     ],
# )

# print(response.choices[0].message.content)


class MCPClient:
    def __init__(self):
        # 初始化会话和客户端对象
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = client

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("服务器脚本必须是 .py 或 .js 文件")
        command = "python" if is_python else "node"
        # Create a modified environment to include virtual environment path
        env = os.environ.copy()
        venv_site_packages = os.path.join(sys.prefix, "Lib", "site-packages")
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = f"{venv_site_packages}:{env['PYTHONPATH']}"
        else:
            env["PYTHONPATH"] = venv_site_packages

        server_params = StdioServerParameters(
            command=command, args=[server_script_path], env=env
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # 列出可用工具
        response = await self.session.list_tools()
        tools = response.tools
        print("\n已连接到服务器，可用工具：", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        messages = [{"role": "user", "content": query}]

        response = await self.session.list_tools()
        available_tools = [
            {
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                },
                "type": "function",
            }
            for tool in response.tools
        ]

        response = self.openai.chat.completions.create(
            model=deployment_id,
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        tool_results = []
        final_text = []

        for content in response.choices:
            if content.finish_reason == "stop":
                final_text.append(content.content)
            elif content.finish_reason == "tool_calls":
                tool_calls = content.message.tool_calls
                if not tool_calls:
                    continue
                for call in tool_calls:
     
                    tool_name = call.function.name
                    tool_args = json.loads(call.function.arguments)

                    # 执行工具调用
                    result = await self.session.call_tool(tool_name, tool_args)
                    tool_results.append({"call": tool_name, "result": result})
                    final_text.append(f"[调用工具 {tool_name}，参数 {tool_args}]")

                    if hasattr(content, "text") and content.text:
                        messages.append({"role": "assistant", "content": content.text})
                    messages.append({"role": "user", "content": result.content})

                response = self.openai.chat.completions.create(
                    model=deployment_id,
                    max_tokens=1000,
                    messages=messages,
                )

                final_text.append(response.choices[0].message.content)

        return "\n".join(final_text)

    async def chat_loop(self):
        print("\nMCP 客户端已启动！")
        print("输入你的问题或输入 'quit' 退出。")

        while True:
            try:
                query = input("\n问题：").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\n错误：{str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()


async def main():

    client = MCPClient()
    try:
        await client.connect_to_server("D:/DEV/MCP_ICM/src/app.py")
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
