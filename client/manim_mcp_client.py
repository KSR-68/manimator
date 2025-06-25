import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, List
from contextlib import AsyncExitStack

from google import genai
from google.genai import types
from google.genai.types import Tool

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_schema(schema):
    if isinstance(schema, dict):
        schema.pop("title", None)
        if "properties" in schema:
            for k, v in schema["properties"].items():
                schema["properties"][k] = clean_schema(v)
    return schema


def convert_mcp_tools_to_gemini(mcp_tools):
    gemini_tools = []
    for tool in mcp_tools:
        params = clean_schema(tool.inputSchema)
        function_decl = types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=params
        )
        gemini_tools.append(Tool(function_declarations=[function_decl]))
    return gemini_tools


class ManimatorClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found.")

        self.genai_client = genai.Client(api_key=gemini_api_key)
        self.function_declarations: List[types.Tool] = []

    async def connect_to_server(self, server_script_path: str):
        logger.info(f"Starting MCP server: {server_script_path}")
        command = "python" if server_script_path.endswith('.py') else "node"
        server_params = StdioServerParameters(command=command, args=[server_script_path])

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport

        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        await self.session.initialize()

        response = await self.session.list_tools()
        mcp_tools = response.tools
        self.function_declarations = convert_mcp_tools_to_gemini(mcp_tools)

        tool_names = [tool.name for tool in mcp_tools]
        logger.info(f"Connected. Tools: {tool_names}")
        return tool_names

    async def generate_and_execute(self, description: str) -> Optional[str]:
        """Uses Gemini to generate Manim code and execute it via the tool."""
        print("🧠 Step 1: Generating Manim code...")
        prompt = f"""
        You are an expert in Manim.
        Generate Python code for the following animation:
        - The code must start with `from manim import *`
        - Define exactly one Scene subclass
        - No explanation, no markdown, just clean executable code.
        Description: {description}
        """
        response = self.genai_client.models.generate_content(
            model='gemini-2.5-flash-preview-04-17',
            contents=[types.Content(role='user', parts=[types.Part(text=prompt)])],
            config=types.GenerateContentConfig(tools=self.function_declarations)
        )

        manim_code = response.text.strip()
        if manim_code.startswith("```python"):
            manim_code = manim_code[9:]
        if manim_code.endswith("```"):
            manim_code = manim_code[:-3]
        print("✅ Code generated.")

        print("🔥 Step 2: Executing animation...")
        result = await self.session.call_tool("execute_manim_code", {"manim_code": manim_code})
        output = result.content[0].text if isinstance(result.content, list) else str(result.content)

        if not output.startswith("Success:"):
            print("❌ Rendering failed.")
            print(output)
            return None

        path = output.split("Success:", 1)[-1].strip()
        print(f"✅ Animation saved at: {path}")

        # Auto-open video on Windows
        if os.name == "nt" and path.endswith(".mp4"):
            print("▶️ Opening video...")
            os.startfile(path)

        return path

    async def run_cli(self):
        print("🎬 Manimator - Natural Language to Manim Animations")
        print("=" * 60)

        server_script = Path(__file__).parent.parent / "manim-mcp-server" / "src" / "manim_server.py"
        try:
            tools = await self.connect_to_server(str(server_script))
            print(f"✅ Connected! Tools: {tools}")
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return

        print("\n🎯 Ready to create animations! Type 'exit' to quit.")
        while True:
            try:
                prompt = input("\n📝 Describe your animation: ").strip()
                if prompt.lower() in {"exit", "quit"}:
                    break
                if not prompt:
                    continue
                await self.generate_and_execute(prompt)

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                logger.error("Unexpected error in CLI", exc_info=True)
                print(f"❌ Unexpected error: {e}")

        print("\n👋 Goodbye!")

    async def cleanup(self):
        logger.info("Cleaning up async resources...")
        await self.exit_stack.aclose()


async def main():
    client = ManimatorClient()
    try:
        await client.run_cli()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
