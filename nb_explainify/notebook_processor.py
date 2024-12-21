import nbformat
import black
from typing import Optional, Dict, Any, List
from .llm_processor import LLMProcessor


class NotebookProcessor:
    """A class to process Jupyter notebooks."""
    
    def __init__(self, notebook_path: Optional[str] = None):
        """Initialize the NotebookProcessor.
        
        Args:
            notebook_path (Optional[str]): Path to the notebook file. If provided, loads the notebook.
        """
        self.notebook = None
        if notebook_path:
            self.load_notebook(notebook_path)
    
    def load_notebook(self, notebook_path: str) -> None:
        """Load the notebook from the specified path using nbformat."""
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                self.notebook = nbformat.read(f, as_version=4)
        except FileNotFoundError:
            raise FileNotFoundError(f"Notebook file not found: {notebook_path}")
        except Exception as e:
            raise Exception(f"Error loading notebook: {str(e)}")

    def get_code_cells(self) -> list:
        """Get all code cells from the notebook.
        
        Returns:
            list: A list of code cells from the notebook
        """
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
        
        return [cell for cell in self.notebook.cells if cell.cell_type == 'code']

    def get_markdown_cells(self) -> list:
        """Get all markdown cells from the notebook.
        
        Returns:
            list: A list of markdown cells from the notebook
        """
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
        
        return [cell for cell in self.notebook.cells if cell.cell_type == 'markdown']

    def format_code_cells(self) -> None:
        """Format all code cells in the notebook using black."""
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
        
        mode = black.Mode(
            target_versions={black.TargetVersion.PY39},
            line_length=88,
            string_normalization=True,
            is_pyi=False,
        )
        
        for cell in self.get_code_cells():
            try:
                cell.source = black.format_str(cell.source, mode=mode)
            except Exception as e:
                print(f"Warning: Could not format cell: {str(e)}")
                continue

    def add_comments_to_code_cells(self) -> None:
        """Add explanatory comments to all code cells using LLM."""
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")

        llm = LLMProcessor()
        code_cells = self.get_code_cells()
        
        # Update each code cell with comments
        cell_index = 0
        for i, cell in enumerate(self.notebook.cells):
            if cell.cell_type == 'code':
                try:
                    cell.source = llm.add_comments_to_code(cell.source)
                except Exception as e:
                    print(f"Warning: Could not add comments to cell {cell_index + 1}: {str(e)}")
                cell_index += 1

    def optimize_code_cells(self) -> None:
        """Optimize all code cells in the notebook for better performance and readability."""
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
        
        llm = LLMProcessor()
        code_cells = self.get_code_cells()
        
        # Keep track of code context
        context = []
        
        # Update each code cell with optimized version
        cell_index = 0
        for i, cell in enumerate(self.notebook.cells):
            if cell.cell_type == 'code':
                try:
                    cell.source = llm.optimize_code(cell.source, context)
                    context.append(cell.source)
                except Exception as e:
                    print(f"Warning: Could not optimize cell {cell_index + 1}: {str(e)}")
                cell_index += 1

    def add_markdown_explanations(self) -> None:
        """Add or enhance markdown explanations for code cells."""
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
        
        llm = LLMProcessor()
        new_cells = []
        context = []  # Keep track of previous code cells
        
        for cell in self.notebook.cells:
            if cell.cell_type == 'code':
                # Generate markdown explanation with context
                try:
                    markdown = llm.generate_markdown_explanation(cell.source, context=context)
                    new_cells.append(nbformat.v4.new_markdown_cell(markdown))
                except Exception as e:
                    print(f"Warning: Could not generate markdown for cell: {str(e)}")
                context.append(cell.source)  # Add current cell to context for next iteration
            new_cells.append(cell)
        
        self.notebook.cells = new_cells

    def add_intro(self) -> None:
        """Add an introductory markdown cell at the beginning of the notebook."""
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
            
        llm = LLMProcessor()
        notebook_cells = [(cell.cell_type, cell.source) for cell in self.notebook.cells]
        
        try:
            intro = llm.generate_notebook_intro(notebook_cells)
            intro_cell = nbformat.v4.new_markdown_cell(intro)
            self.notebook.cells.insert(0, intro_cell)
        except Exception as e:
            print(f"Warning: Could not generate notebook introduction: {str(e)}")

    def add_summary(self) -> None:
        """Add a summary markdown cell at the end of the notebook."""
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
            
        llm = LLMProcessor()
        notebook_cells = [(cell.cell_type, cell.source) for cell in self.notebook.cells]
        
        try:
            summary = llm.generate_notebook_summary(notebook_cells)
            summary_cell = nbformat.v4.new_markdown_cell(summary)
            self.notebook.cells.append(summary_cell)
        except Exception as e:
            print(f"Warning: Could not generate notebook summary: {str(e)}")

    def explainify_notebook(self, output_path: str = "explainified_notebook.ipynb", 
                          to_format: bool = True, to_comment: bool = True, 
                          to_optimize: bool = True, to_markdown: bool = True,
                          to_intro: bool = True, to_summary: bool = True) -> None:
        """Process the notebook with selected operations and save the result.
        
        Args:
            output_path (str): Path to save the processed notebook
            to_format (bool): Whether to format code cells
            to_comment (bool): Whether to add comments to code cells
            to_optimize (bool): Whether to optimize code cells
            to_markdown (bool): Whether to add markdown explanations
            to_intro (bool): Whether to add introduction
            to_summary (bool): Whether to add summary
        """
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
            
        # Add introduction first if requested
        if to_intro:
            try:
                self.add_intro()
            except Exception as e:
                print(f"Warning: Could not add introduction: {str(e)}")
        
        # Format code cells if requested
        if to_format:
            self.format_code_cells()
            
        # Add markdown explanations if requested
        if to_markdown:
            try:
                self.add_markdown_explanations()
            except Exception as e:
                print(f"Warning: Could not add markdown explanations: {str(e)}")
                
        # Optimize code if requested
        if to_optimize:
            try:
                self.optimize_code_cells()
            except Exception as e:
                print(f"Warning: Could not optimize code: {str(e)}")
                
        # Add comments if requested
        if to_comment:
            try:
                self.add_comments_to_code_cells()
            except Exception as e:
                print(f"Warning: Could not add comments: {str(e)}")
                
        # Add summary at the end if requested
        if to_summary:
            try:
                self.add_summary()
            except Exception as e:
                print(f"Warning: Could not add summary: {str(e)}")
                
        # Save the processed notebook
        try:
            self.save_notebook(output_path)
        except Exception as e:
            print(f"Warning: Could not save notebook: {str(e)}")

    def save_notebook(self, output_path: Optional[str] = None) -> None:
        """Save the notebook to a file.
        
        Args:
            output_path (Optional[str]): Path where to save the notebook.
                If None, overwrites the original file.
        
        Raises:
            ValueError: If notebook hasn't been loaded
            Exception: If there's an error saving the notebook
        """
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")
        
        save_path = output_path or self.notebook_path
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                nbformat.write(self.notebook, f)
        except Exception as e:
            raise Exception(f"Error saving notebook: {str(e)}")