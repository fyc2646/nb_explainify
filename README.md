# nb-explainify 🚀

Transform your Jupyter notebooks from plain to extraordinary! nb-explainify is your AI-powered companion that turns basic notebooks into clear documentation that your colleagues will admire and future-you will thank you for.

## Why nb-explainify? ✨

Ever found yourself:
- Staring at notebooks you created months ago, wondering what it does? 
- Rushing to meet deadlines and skipping proper documentation?
- Wanting to share your notebooks but feeling they need more polish?

Say goodbye to these problems! nb-explainify leverages the power of OpenAI's GPT models to automatically:
- Generate crystal-clear explanations that actually make sense
- Optimize your code while preserving its functionality
- Add professional-grade comments that future readers will appreciate
- Create engaging introductions that set the perfect context
- Provide insightful summaries with practical next steps

Think of it as having a professional technical writer, code reviewer, and documentation expert working for you 24/7!

## Features 🎯

- **Smart Markdown Generation**: Get concise, context-aware explanations that focus on what matters. No more generic comments!
- **Intelligent Code Optimization**: Automatically improve your code's readability and efficiency while maintaining its purpose
- **Professional Documentation**: Add clear, detailed comments that explain not just what the code does, but why it does it
- **Engaging Introductions**: Create compelling notebook introductions that perfectly set up your work's context and goals
- **Insightful Summaries**: Generate comprehensive summaries with practical suggestions for future improvements
- **Code Beautification**: Ensure your code follows consistent style guidelines automatically

Best of all? It takes just a few lines of code to transform your notebook from basic to brilliant!

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/nb-explainify.git
cd nb-explainify
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key in a `.env` file:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

Basic usage:
```python
from nb_explainify import NotebookProcessor

# Load and process a notebook
processor = NotebookProcessor()
processor.load_notebook("your_notebook.ipynb")
processor.explainify_notebook(output_path="enhanced_notebook.ipynb")
```

Customize processing options:
```python
processor.explainify_notebook(
    output_path="custom_notebook.ipynb",
    to_format=True,      # Format code cells
    to_comment=True,     # Add code comments
    to_optimize=True,    # Optimize code
    to_markdown=True,    # Add markdown explanations
    to_intro=True,       # Add introduction
    to_summary=True      # Add summary
)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.