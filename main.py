from nb_explainify import NotebookProcessor
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

def main():
    # Load environment variables
    load_dotenv()
    
    # Load the notebook
    notebook_path = "./test.ipynb"
    output_path = "./test_explanified.ipynb"
    
    # Initialize and process the notebook
    processor = NotebookProcessor()
    processor.load_notebook(notebook_path)
    
    # Process the notebook with all operations
    processor.explainify_notebook(
        output_path=output_path,
        to_format=True,
        to_comment=True,
        to_optimize=False,
        to_markdown=True,
        to_intro=True,
        to_summary=True
    )
    
    print(f"\nProcessed notebook saved to: {output_path}")

if __name__ == "__main__":
    main()