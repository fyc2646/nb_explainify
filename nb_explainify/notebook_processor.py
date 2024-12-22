import nbformat
import black
from typing import Optional, List
from .llm_processor import LLMProcessor


class NotebookProcessor:
    """A class to process Jupyter notebooks."""

    def __init__(self, notebook_path: Optional[str] = None, llm_processor: Optional[LLMProcessor] = None):
        """Initialize the NotebookProcessor.

        Args:
            notebook_path (Optional[str]): Path to the notebook file. If provided, loads the notebook.
            llm_processor (Optional[LLMProcessor]): LLM processor instance to use. If not provided, creates a new one.
        """
        self.notebook = None
        self.notebook_path = notebook_path
        self.llm_processor = llm_processor or LLMProcessor()
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

    def _validate_notebook(self) -> None:
        """Validate that notebook is loaded."""
        if self.notebook is None:
            raise ValueError("Notebook has not been loaded")

    def get_code_cells(self) -> List[nbformat.NotebookNode]:
        """Get all code cells from the notebook."""
        self._validate_notebook()
        return [cell for cell in self.notebook.cells if cell.cell_type == 'code']

    def get_markdown_cells(self) -> List[nbformat.NotebookNode]:
        """Get all markdown cells from the notebook."""
        self._validate_notebook()
        return [cell for cell in self.notebook.cells if cell.cell_type == 'markdown']

    def format_code_cells(self) -> None:
        """Format all code cells in the notebook using black."""
        self._validate_notebook()
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

    def add_comments_to_code_cells(self) -> None:
        """Add explanatory comments to all code cells using LLM."""
        self._validate_notebook()
        code_cells = self.get_code_cells()
        previous_code_cells = []
        
        for i, cell in enumerate(code_cells):
            try:
                cell.source = self.llm_processor.add_comments_to_code(
                    cell.source,
                    context=previous_code_cells
                )
                previous_code_cells.append(cell.source)
            except Exception as e:
                print(f"Warning: Could not add comments to cell {i}: {str(e)}")

    def optimize_code_cells(self) -> None:
        """Optimize all code cells in the notebook for better performance and readability."""
        self._validate_notebook()
        for i, cell in enumerate(self.get_code_cells()):
            try:
                cell.source = self.llm_processor.optimize_code(cell.source)
            except Exception as e:
                print(f"Warning: Could not optimize cell {i}: {str(e)}")

    def add_markdown_explanations(self) -> None:
        """Add or enhance markdown explanations for code cells."""
        self._validate_notebook()
        cells = self.notebook.cells
        added_cells = 0
        previous_code_cells = []

        for i in range(len(cells)):
            adjusted_i = i + added_cells
            cell = cells[adjusted_i]

            if cell.cell_type != 'code':
                continue

            try:
                explanation = self.llm_processor.generate_markdown_explanation(
                    cell.source,
                    context=previous_code_cells
                )
                previous_code_cells.append(cell.source)
                markdown_cell = nbformat.v4.new_markdown_cell(explanation)
                cells.insert(adjusted_i, markdown_cell)
                added_cells += 1
            except Exception as e:
                print(f"Warning: Could not add markdown explanation for cell {i}: {str(e)}")

    def add_intro(self) -> None:
        """Add an introductory markdown cell at the beginning of the notebook."""
        self._validate_notebook()
        notebook_cells = [(cell.cell_type, cell.source) for cell in self.notebook.cells]
        try:
            intro = self.llm_processor.generate_notebook_intro(notebook_cells)
            intro_cell = nbformat.v4.new_markdown_cell(intro)
            self.notebook.cells.insert(0, intro_cell)
        except Exception as e:
            print(f"Warning: Could not generate notebook introduction: {str(e)}")

    def add_summary(self) -> None:
        """Add a summary markdown cell at the end of the notebook."""
        self._validate_notebook()
        notebook_cells = [(cell.cell_type, cell.source) for cell in self.notebook.cells]
        try:
            summary = self.llm_processor.generate_notebook_summary(notebook_cells)
            summary_cell = nbformat.v4.new_markdown_cell(summary)
            self.notebook.cells.append(summary_cell)
        except Exception as e:
            print(f"Warning: Could not generate notebook summary: {str(e)}")

    def explainify_notebook(self, output_path: str = "explainified_notebook.ipynb",
                          to_format: bool = True, to_comment: bool = True,
                          to_optimize: bool = True, to_markdown: bool = True,
                          to_intro: bool = True, to_summary: bool = True) -> None:
        """Process the notebook with selected operations and save the result."""
        self._validate_notebook()

        operations = [
            (to_intro, self.add_intro, "introduction"),
            (to_markdown, self.add_markdown_explanations, "markdown explanations"),
            (to_optimize, self.optimize_code_cells, "code optimization"),
            (to_comment, self.add_comments_to_code_cells, "code comments"),
            (to_summary, self.add_summary, "summary"),
            (to_format, self.format_code_cells, "code formatting")
        ]

        for enabled, operation, desc in operations:
            if enabled:
                try:
                    operation()
                except Exception as e:
                    print(f"Warning: Could not add {desc}: {str(e)}")

        try:
            self.save_notebook(output_path)
        except Exception as e:
            print(f"Warning: Could not save notebook: {str(e)}")

    def save_notebook(self, output_path: Optional[str] = None) -> None:
        """Save the notebook to a file."""
        self._validate_notebook()
        save_path = output_path or self.notebook_path

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                nbformat.write(self.notebook, f)
        except Exception as e:
            raise Exception(f"Error saving notebook: {str(e)}")