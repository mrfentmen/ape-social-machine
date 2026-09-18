#!/usr/bin/env python3
"""Call one Postiz MCP tool with a JSON payload. Read-only discipline:
this helper does whatever tool+args you give it, so only call posting
tools after explicit human approval on the exact content.

Usage:
  python3 postiz_call.py <toolName> '<json-args>'
  python3 postiz_call.py integrationSchema '{"isPremium": false, "platform": "x"}'
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from postiz_mcp import MCP_URL, get_token  # noqa: E402


async def call(tool_name: str, args: dict):
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    access_token = get_token()
    async with streamablehttp_client(
        MCP_URL, headers={"Authorization": f"Bearer {access_token}"}
    ) as (read, write, _sid):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=args)
            for item in result.content:
                if getattr(item, "type", "") == "text":
                    print(item.text)
                else:
                    print(f"[non-text content: {getattr(item, 'type', '?')}]")
            if getattr(result, "isError", False):
                sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    asyncio.run(call(tool, args))


if __name__ == "__main__":
    main()
