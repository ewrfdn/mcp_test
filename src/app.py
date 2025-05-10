from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化FastMCP服务器
mcp = FastMCP("ICM")

@mcp.tool()
async def get_date() -> str:
    return "2023-10-01"

@mcp.tool()
async def get_weather() -> str:
    return "Sunny"


if __name__ == "__main__":
    mcp.run(transport='stdio')