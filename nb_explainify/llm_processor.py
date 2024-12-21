from typing import Optional, List, Tuple
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

class LLMProcessor:
    """A class to process code using OpenAI's LLM models."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize the LLM processor.
        
        Args:
            model (str): OpenAI model to use. Defaults to gpt-4-turbo-preview
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set in .env file")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    def add_comments_to_code(self, code: str) -> str:
        """Add explanatory comments to the provided code.
        
        Args:
            code (str): The code to add comments to
            
        Returns:
            str: The code with added comments
        """
        # Clean and normalize the code
        code = code.strip()
        if not code:
            return code
            
        prompt = f"""Please add clear and concise comments to explain this Python code. 
        Keep the original code exactly as is, just add appropriate comments.
        Focus on explaining:
        1. What the code does
        2. Any important parameters or return values
        3. Key algorithmic steps
        
        Here's the code:
        
        {code}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python code commenter. Add clear and concise comments to explain the code while keeping the code exactly as is."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
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
    
    def optimize_code(self, code: str, context: Optional[List[str]] = None) -> str:
        """Optimize the provided code for better performance and readability.
        
        Args:
            code (str): The code to optimize
            context (Optional[List[str]]): List of code strings from previous cells for context
            
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
        
        prompt = f"""Optimize this Python code for better performance and readability.
        Focus on:
        1. Algorithmic efficiency
        2. Python best practices and idioms
        3. Code organization and clarity
        4. Memory usage optimization where applicable
        
        {context_str}Code to optimize:
        
        {code}
        
        IMPORTANT: Your response must contain ONLY the optimized Python code.
        Do NOT include any explanations, markdown formatting, or comments about optimizations.
        Do NOT redefine functions that are already defined in the context.
        Only include comments within the code itself.
        If the code only uses functions defined in the context, return ONLY the optimized version of the input code.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a Python code optimizer. You MUST respond with ONLY the optimized Python code, without any additional text or explanations. Include any necessary comments within the code itself. DO NOT redefine functions that are already defined in the context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=1000
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
            
    def generate_markdown_explanation(self, code: str, existing_markdown: Optional[str] = None, context: Optional[List[str]] = None) -> str:
        """Generate or enhance markdown explanation for a code cell.
        
        Args:
            code (str): The code to explain
            existing_markdown (Optional[str]): Existing markdown text to enhance, if any
            context (Optional[List[str]]): List of code strings from previous cells for context
            
        Returns:
            str: The generated or enhanced markdown explanation
        """
        code = code.strip()
        if not code:
            return existing_markdown or ""
            
        context_str = ""
        if context:
            context_str = "Previous code cells:\n\n"
            for i, ctx in enumerate(context, 1):
                clean_ctx = ctx.strip()
                if clean_ctx:
                    context_str += f"Cell {i}:\n```python\n{clean_ctx}\n```\n\n"
            
        if existing_markdown:
            prompt = f"""Enhance this markdown explanation for the code below.
            Be very concise - use at most 2 short paragraphs.
            Focus only on what the code does and any crucial parameters.
            Remove any implementation details or examples unless absolutely necessary.
            Consider the context from previous cells when explaining this code.
            
            Current Markdown:
            {existing_markdown}
            
            {context_str}Code to explain:
            ```python
            {code}
            ```
            """
        else:
            prompt = f"""Write a very concise markdown explanation for this code in a Jupyter notebook.
            Use at most 2 short paragraphs.
            Focus only on what the code does and any crucial parameters.
            Do not include implementation details or examples.
            Do not mention where functions are defined.
            Consider how this code relates to any previous cells when explaining its purpose.
            
            {context_str}Code to explain:
            ```python
            {code}
            ```
            """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical writer creating very concise markdown documentation. Focus on what the code does, not how it does it. Consider the context from previous cells when explaining the code's purpose."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            markdown = response.choices[0].message.content.strip()
            return markdown
            
        except Exception as e:
            raise Exception(f"Error generating markdown explanation: {str(e)}")

    def generate_notebook_intro(self, notebook_cells: List[Tuple[str, str]]) -> str:
        """Generate an introduction for the notebook.
        
        Args:
            notebook_cells (List[Tuple[str, str]]): List of (cell_type, content) tuples
            
        Returns:
            str: The generated introduction markdown
        """
        cell_content = "\n\n".join(
            f"{cell_type.capitalize()} Cell:\n```{cell_type}\n{content}\n```" 
            for cell_type, content in notebook_cells
        )
        
        prompt = f"""Write a concise introduction for this Jupyter notebook.
        Start with a descriptive title as a level 1 header (# Title).
        Then write 1-2 short paragraphs explaining what this notebook demonstrates.
        Focus on the high-level purpose and key concepts, not implementation details.
        Consider both the code and existing markdown when writing the introduction.
        
        Here are all the cells in the notebook:
        {cell_content}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical writer creating clear notebook introductions. Focus on explaining what the notebook demonstrates and its practical applications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            intro = response.choices[0].message.content.strip()
            return intro
            
        except Exception as e:
            raise Exception(f"Error generating notebook introduction: {str(e)}")
            
    def generate_notebook_summary(self, notebook_cells: List[Tuple[str, str]]) -> str:
        """Generate a summary for the notebook.
        
        Args:
            notebook_cells (List[Tuple[str, str]]): List of (cell_type, content) tuples
            
        Returns:
            str: The generated summary markdown
        """
        cell_content = "\n\n".join(
            f"{cell_type.capitalize()} Cell:\n```{cell_type}\n{content}\n```" 
            for cell_type, content in notebook_cells
        )
        
        prompt = f"""Write a concise summary for this Jupyter notebook.
        Start with a level 2 header (## Summary).
        Include the following sections:
        1. Brief recap of what was accomplished
        2. Key concepts demonstrated
        3. Potential improvements and extensions (with level 3 header ### Future Improvements)
        
        Focus on practical applications and learning opportunities.
        Be specific about potential improvements and extensions.
        Consider both the code implementations and explanations in markdown cells.
        
        Here are all the cells in the notebook:
        {cell_content}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical writer creating insightful notebook summaries. Focus on what was learned and future opportunities for enhancement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            raise Exception(f"Error generating notebook summary: {str(e)}")
