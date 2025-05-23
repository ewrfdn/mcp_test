import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from dotenv import load_dotenv
import os
from openai import AzureOpenAI
import json

load_dotenv()  # Load environment variables from .env

deployment_id = os.getenv("AZURE_OPENAI_DEPLOYMENT_ID", "gpt-4o")
api_version =os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = AzureOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=deployment_id,
            api_key=api_key,
            api_version=api_version,
        )

    async def connect_to_server(self, server_script_path: str):
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
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
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server, available tools:", [tool.name for tool in tools])

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

                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    tool_results.append({"call": tool_name, "result": result})
                    final_text.append(f"[Tool call {tool_name}, parameters {tool_args}]")

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
        print("\nMCP client started.")
        print("Enter your question or type 'quit' to exit.")

        while True:
            try:
                query = input("\nQuestion: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():

    client = MCPClient()
    try:
        await client.connect_to_server("./src/app.py")
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys

    asyncio.run(main())
