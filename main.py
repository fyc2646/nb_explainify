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
    processor = NotebookProcessor()
    processor.load_notebook(notebook_path)
    
    # Process the notebook with all operations
    output_path = "./test_processed.ipynb"
    processor.explainify_notebook(
        output_path=output_path,
        to_format=True,
        to_comment=True,
        to_optimize=True,
        to_markdown=True,
        to_intro=True,
        to_summary=True
    )
    
    print("\nProcessed notebook:")
    for i, cell in enumerate(processor.notebook.cells):
        print(f"\n{cell.cell_type.capitalize()} Cell {i + 1}:")
        print(cell.source)
    
    print(f"\nSaved processed notebook to: {output_path}")

if __name__ == "__main__":
    main()