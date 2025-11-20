# Context Studio

## 🚀 Context Studio: The Visual LLM Context Builder

Context Studio is a cross-platform (designed for Windows first) desktop application built with Python and PySide6. It is designed for software developers who use Browser-based Large Language Models (LLMs) like GPT-4, Claude, or Llama for coding assistance.

Instead of manually copying and pasting files or managing complex CLI commands, Context Studio provides an **interactive file tree** to visually select the exact code files needed for a given LLM prompt. It automatically formats the content into a single, structured Markdown block, ready for context injection.

### ✨ Features

*   **Interactive File Tree:** Visually browse your project and select files using checkboxes.
*   **Smart Selection:** Tri-state checkboxes for easy recursive selection of folders.
*   **Real-Time Preview:** See the exact concatenated Markdown output as you select files.
*   **Token Estimation:** Get a live, approximate count of tokens to manage LLM context windows efficiently.
*   **Smart Filtering:** Automatically ignores standard noise directories (`.git`, `node_modules`, `venv`, etc.).
*   **Clipboard Integration:** One-click copy of the entire context to your clipboard.
*   **Windows Compatible:** Optimized for path and encoding handling on Windows environments.

### 🛠 Installation

**(Placeholder for future instructions)**

1.  Clone the repository: `git clone [REPO_URL]`
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the application: `python src/main.py`

### 🏗 Architecture

Context Studio follows a separation of concerns approach:

*   **FileScanner:** Handles file system navigation and content reading.
*   **ContextFormatter:** Structures the selected content into the final Markdown output.
*   **MainWindow (View):** The PySide6 GUI for visualization and interaction.

### 📝 Usage

1.  Open your project's root folder in Context Studio.
2.  Select the relevant files for your current task using the file tree (e.g., the service file and the model it depends on).
3.  Review the Markdown output and the token count.
4.  Click "Copy to Clipboard."
5.  Paste the content into your LLM prompt, followed by your request.

---
*Developed by Fernando Stefanovic and a whole lot of water*
