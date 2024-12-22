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
            
    def generate_markdown_explanation(self, code: str, context: list = None) -> str:
        """Generate a markdown explanation for a code cell.
        
        Args:
            code (str): The code to explain
            context (list, optional): Previous code cells for context
            
        Returns:
            str: Generated markdown explanation
        """
        prompt = f"""Write a clear, educational explanation of what we are doing in this section, focusing on the concepts and purpose.
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
        {context if context else 'No previous context'}
        
        Write your educational explanation:"""
        
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
        prompt = f"""Enhance this explanation to be more educational and concept-focused while maintaining its key points.
        Write as if you are teaching a student, using natural language without showing any code.
        Don't use phrases like "this code does" or "in this code". Instead, use active voice like "we" and focus on what we're accomplishing.
        Only add information that is missing or could be explained better. Don't repeat information that is already well explained.
        
        Existing explanation:
        {existing_markdown}
        
        Code being explained (don't include this in your explanation, just understand what it does):
        {code}
        
        Previous context (don't mention this directly):
        {context if context else 'No previous context'}
        
        Write your enhanced educational explanation:"""
        
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
