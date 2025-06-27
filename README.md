# 🎬 Manimator

**Manimator** is an AI-powered tool that converts natural language descriptions into beautiful [Manim](https://www.manim.community/) animations.  
It leverages Google Gemini for code generation and uses an MCP (Model Context Protocol) server to render animations programmatically.

---

## ✨ Features

- **Natural Language to Animation:** Describe your animation in plain English and get a Manim video.
- **Google Gemini Integration:** Uses Gemini LLM to generate clean, executable Manim code.
- **Automated Rendering:** Runs Manim code on a server and saves/opens the resulting video.
- **Interactive CLI:** Friendly command-line interface for iterative animation creation.
- **Extensible Tooling:** Easily add new tools to the MCP server for more advanced workflows.

---

## 🗂️ Project Structure

```
manimator/
├── .gitignore
├── .python-version
├── main.py
├── pyproject.toml
├── README.md
├── uv.lock
├── client/
│   ├── .env
│   └── manim_mcp_client.py
└── manim-mcp-server/
    └── src/
        └── manim_server.py
```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/manimator.git
cd manimator
```

### 2. Install Dependencies

- Python 3.10+ recommended
- [Manim Community Edition](https://docs.manim.community/en/stable/installation.html)
- [Google GenerativeAI Python SDK](https://github.com/google/generative-ai-python)
- MCP Python client/server (https://modelcontextprotocol.io/introduction)

```bash
# Using uv (recommended)
uv pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the `client/` directory:

```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 4. Run the Client

```bash
cd client
uv run manim_mcp_client.py
```

---

## 🧑‍💻 Usage

1. **Start the CLI:**  
   The CLI will automatically launch the MCP server and connect.

2. **Describe Your Animation:**  
   ```
   📝 Describe your animation: Show a red circle moving right and turning into a square
   ```

3. **Watch the Magic:**  
   - The tool will generate Manim code, render the animation, and open the resulting video.
   - Output videos are saved in the server's `media/manim_tmp/` directory.

4. **Other Commands:**  
   - Type `help` for usage tips and examples.
   - Type `exit` or `quit` to leave.

---

## 🛠️ Example Prompts

- "Create a red circle that moves from left to right"
- "Show a sine wave animation with axes"
- "Animate the quadratic formula appearing with fade effect"
- "Draw a mathematical graph of y = x^2"
- "Show text transforming from 'Hello' to 'World'"

---

## 📦 Extending

- **Add new tools** to the MCP server by defining new `@mcp.tool()` functions in `manim_server.py`.
- **Customize prompts** in the client for different animation styles or code templates.

---

## 📝 License

MIT License

---

## 🤝 Acknowledgements

- [Manim Community](https://www.manim.community/)
- [Google Gemini](https://deepmind.google/technologies/gemini/)
- [MCP Protocol](https://github.com/microsoft/mcp)

---

## 💡 Tips

- For best results, be specific in your animation descriptions.
- Check the `media/manim_tmp/` folder for generated videos.
- If you encounter issues, ensure all dependencies are installed and your API key is valid.

---

Happy animating! 🚀
