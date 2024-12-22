from typing import Optional, List, Tuple
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

class DefaultPrompts:
    """Default prompts for LLM processing."""
    
    NOTEBOOK_SUMMARY = """Analyze this Jupyter notebook and provide a comprehensive summary.
    Focus on the main objectives, key findings, and methodologies used.
    Include suggestions for potential improvements or future work.
    Keep the summary clear and concise.
    
    Notebook cells:
    {cells}
    """
    
    NOTEBOOK_INTRO = """Create a comprehensive introduction for this Jupyter notebook.
    Explain the purpose, methodology, and expected outcomes.
    Make it engaging and informative for readers.
    
    Notebook cells:
    {cells}
    """
    
    CODE_OPTIMIZATION = """Optimize this Python code to improve readability and efficiency.
    Maintain the exact same functionality and output.
    Focus on:
    - Better variable names
    - Code structure
    - Performance improvements
    - Following PEP 8 style guidelines
    
    Original code:
    {code}
    
    Previous context:
    {context}
    
    Return only the optimized code without explanations.
    """
    
    CODE_COMMENTS = """Add clear and concise comments to this Python code.
    Focus on explaining:
    - The purpose of each code block
    - Important variables and their roles
    - Complex logic or algorithms
    - Any assumptions or limitations
    
    Keep comments professional and informative.
    Add comments only where they add value.
    Return the code with added comments.
    
    Code to comment:
    {code}
    """
    
    MARKDOWN_EXPLANATION = """Write a clear, educational explanation of what we are doing in this section, focusing on the concepts and purpose.
    Write as if you are teaching a student, using natural language without showing any code.
    Don't use phrases like "this code does" or "in this code". Instead, use active voice like "we" and focus on what we're accomplishing.
    Explain the underlying concepts and why they're important.

    For example, instead of:
    "This code defines a variable x = 5 and uses it to calculate..."
    
    Write:
    "Let's define our initial position value. We'll use this as the starting point for our calculations..."

    Code to explain (don't include this in your explanation, just understand what it does):
    {code}
    
    Previous context (don't mention this directly):
    {context}
    
    Write your educational explanation:"""
    
    ENHANCE_MARKDOWN = """Enhance this explanation to be more educational and concept-focused while maintaining its key points.
    Write as if you are teaching a student, using natural language without showing any code.
    Don't use phrases like "this code does" or "in this code". Instead, use active voice like "we" and focus on what we're accomplishing.
    Only add information that is missing or could be explained better. Don't repeat information that is already well explained.
    
    Existing explanation:
    {existing_markdown}
    
    Code being explained (don't include this in your explanation, just understand what it does):
    {code}
    
    Previous context (don't mention this directly):
    {context}
    
    Write your enhanced educational explanation:"""

class LLMProcessor:
    """A class to process code using OpenAI's LLM models."""
    
    def __init__(self, model: str = "gpt-4o-mini", prompts: Optional[dict] = None):
        """Initialize the LLM processor.
        
        Args:
            model (str): OpenAI model to use
            prompts (Optional[dict]): Custom prompts to override defaults
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set in .env file")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.prompts = {
            'notebook_summary': DefaultPrompts.NOTEBOOK_SUMMARY,
            'notebook_intro': DefaultPrompts.NOTEBOOK_INTRO,
            'code_optimization': DefaultPrompts.CODE_OPTIMIZATION,
            'code_comments': DefaultPrompts.CODE_COMMENTS,
            'markdown_explanation': DefaultPrompts.MARKDOWN_EXPLANATION,
            'enhance_markdown': DefaultPrompts.ENHANCE_MARKDOWN
        }
        if prompts:
            self.prompts.update(prompts)
    
    def add_comments_to_code(self, code: str) -> str:
        """Add explanatory comments to the provided code.
        
        Args:
            code (str): The code to add comments to
            
        Returns:
            str: The code with added comments
        """
        prompt = self.prompts['code_comments'].format(code=code)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python expert adding clear and helpful comments to code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            commented_code = response.choices[0].message.content.strip()
            
            # Remove markdown code block formatting if present
            if commented_code.startswith('```python'):
                commented_code = commented_code[len('```python'):].strip()
            if commented_code.startswith('```'):
                commented_code = commented_code[3:].strip()
            if commented_code.endswith('```'):
                commented_code = commented_code[:-3].strip()
                
            return commented_code
        except Exception as e:
            raise Exception(f"Error generating comments: {str(e)}")
    
    def optimize_code(self, code: str, context: list = None) -> str:
        """Optimize the provided code for better performance and readability.
        
        Args:
            code (str): The code to optimize
            context (list, optional): Previous code cells for context
            
        Returns:
            str: The optimized code
        """
        # Clean and normalize the code
        code = code.strip()
        if not code:
            return code
            
        context_str = ""
        if context:
            context_str = "Previously defined code:\n\n"
            for i, ctx in enumerate(context, 1):
                clean_ctx = ctx.strip()
                if clean_ctx:
                    context_str += f"Cell {i}:\n{clean_ctx}\n\n"
        
        prompt = self.prompts['code_optimization'].format(
            code=code,
            context=context_str if context else 'No previous context'
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python expert optimizing code while maintaining functionality."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            optimized_code = response.choices[0].message.content.strip()
            
            # Remove markdown code block formatting if present
            if optimized_code.startswith('```python'):
                optimized_code = optimized_code[len('```python'):].strip()
            if optimized_code.startswith('```'):
                optimized_code = optimized_code[3:].strip()
            if optimized_code.endswith('```'):
                optimized_code = optimized_code[:-3].strip()
            
            # Remove any text before or after the actual code
            # by looking for the first def, class, or import statement
            # Only do this if we're not dealing with a simple code snippet
            if 'def ' in code or 'class ' in code or 'import ' in code:
                code_markers = ['def ', 'class ', 'import ', 'from ', '#']
                start_index = len(optimized_code)
                for marker in code_markers:
                    pos = optimized_code.find(marker)
                    if pos != -1 and pos < start_index:
                        start_index = pos
                optimized_code = optimized_code[start_index:].strip()
            
            return optimized_code
        except Exception as e:
            raise Exception(f"Error optimizing code: {str(e)}")
            
    def generate_markdown_explanation(self, code: str, context: list = None) -> str:
        """Generate a markdown explanation for a code cell.
        
        Args:
            code (str): The code to explain
            context (list, optional): Previous code cells for context
            
        Returns:
            str: Generated markdown explanation
        """
        prompt = self.prompts['markdown_explanation'].format(
            code=code,
            context=context if context else 'No previous context'
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert teacher explaining complex concepts in clear, natural language. Focus on teaching the concepts and their importance, not on the code implementation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating markdown explanation: {str(e)}")

    def enhance_markdown_explanation(self, existing_markdown: str, code: str, context: list = None) -> str:
        """Enhance an existing markdown explanation for a code cell.
        
        Args:
            existing_markdown (str): The existing markdown explanation
            code (str): The code to explain
            context (list, optional): Previous code cells for context
            
        Returns:
            str: Enhanced markdown explanation
        """
        prompt = self.prompts['enhance_markdown'].format(
            existing_markdown=existing_markdown,
            code=code,
            context=context if context else 'No previous context'
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert teacher enhancing explanations to be more educational and concept-focused. Focus on teaching the concepts and their importance, not on the code implementation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Warning: Could not enhance markdown explanation: {str(e)}")
            return existing_markdown

    def generate_notebook_intro(self, notebook_cells: List[Tuple[str, str]]) -> str:
        """Generate an introduction for the notebook.
        
        Args:
            notebook_cells (List[Tuple[str, str]]): List of (cell_type, content) tuples
            
        Returns:
            str: Generated introduction
        """
        cells_str = ""
        for i, (cell_type, content) in enumerate(notebook_cells, 1):
            cells_str += f"Cell {i} ({cell_type}):\n{content}\n\n"
            
        prompt = self.prompts['notebook_intro'].format(cells=cells_str)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical writer creating engaging notebook introductions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating notebook introduction: {str(e)}")
    
    def generate_notebook_summary(self, notebook_cells: List[Tuple[str, str]]) -> str:
        """Generate a summary for the notebook.
        
        Args:
            notebook_cells (List[Tuple[str, str]]): List of (cell_type, content) tuples
            
        Returns:
            str: Generated summary
        """
        cells_str = ""
        for i, (cell_type, content) in enumerate(notebook_cells, 1):
            cells_str += f"Cell {i} ({cell_type}):\n{content}\n\n"
            
        prompt = self.prompts['notebook_summary'].format(cells=cells_str)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data scientist writing clear notebook summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating notebook summary: {str(e)}")
