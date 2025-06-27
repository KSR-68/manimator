import os
import re
import shutil
import importlib.util
import logging
from mcp.server.fastmcp import FastMCP
from manim import config, tempconfig

mcp = FastMCP()
logger = logging.getLogger(__name__)
# configure logging

MANIM_MEDIA_SUBDIR = "media/manim_tmp"

@mcp.tool()
def execute_manim_code(manim_code: str) -> str:
    """
    Write out the code, import it, configure Manim, render the scene, 
    and return the path to the .mp4
    """
    try:
        # 1) Prepare directories
        base = os.path.dirname(os.path.abspath(__file__))
        tmpdir = os.path.join(base, MANIM_MEDIA_SUBDIR)
        if os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)
        os.makedirs(tmpdir, exist_ok=True)

        script_path = os.path.join(tmpdir, "scene.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(manim_code)

        logger.info("Wrote scene script to %s", script_path)

        # 2) Extract the Scene subclass name
        m = re.search(r"class\s+(\w+)\s*\(\s*[A-Za-z0-9_]*Scene\s*\)\s*:", manim_code)
        if not m:
            return "Failed: no Scene subclass found."
        cls_name = m.group(1)

        # 3) Dynamically import the module
        spec = importlib.util.spec_from_file_location("scene_mod", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SceneClass = getattr(module, cls_name)

        # 4) Temporarily override Manim config for output dir and quality
        cfg = {
            "media_dir": tmpdir,
            "format": "mp4",
            "quality": "low_quality",    # or "medium"/"high" as you like
            "renderer": "opengl", # or "cairo if you don't have GPU"
        }
        with tempconfig(cfg):
            scene = SceneClass()
            scene.render()

        # 5) Find the rendered .mp4
        for root, _, files in os.walk(tmpdir):
            for fn in files:
                if fn.endswith(".mp4"):
                    path = os.path.join(root, fn)
                    logger.info("Rendered video at %s", path)
                    return f"Success:{path}"

        return f"Success:{tmpdir} (no mp4 found)"

    except Exception as e:
        logger.exception("Error in execute_manim_code")
        return f"Failed: {e}"

@mcp.tool()
def cleanup_manim_temp_dir(directory: str) -> str:
    """Clean up the specified Manim temporary directory after execution."""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            logger.info("Cleaned up directory: %s", directory)
            return f"Cleanup successful for directory: {directory}"
        else:
            logger.warning("Directory not found: %s", directory)
            return f"Directory not found: {directory}"
    except Exception as e:
        logger.exception("Error during cleanup of %s", directory)
        return f"Failed to clean up directory: {directory}. Error: {str(e)}"

if __name__ == "__main__":
    logger.info("Starting MCP server...")
    mcp.run(transport="stdio")
