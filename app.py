import streamlit as st
from nb_explainify import NotebookProcessor, LLMProcessor
from nb_explainify.llm_processor import DefaultPrompts
import os
from pathlib import Path
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Notebook Explainify",
    page_icon="📚",
    layout="wide"
)

# Custom CSS to improve aesthetics
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Improve header appearance */
    .main-header {
        color: #1E88E5;
        font-size: 2.5rem !important;
        font-weight: 600;
        margin-bottom: 1rem !important;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }
    
    /* Style the description */
    .app-description {
        font-size: 1.1rem;
        color: #424242;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    /* Style the file uploader */
    .stFileUploader {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px dashed #ccc;
        margin: 2rem 0;
    }
    
    /* Remove extra spacing from upload text */
    .stFileUploader > div:first-child {
        margin-bottom: 0;
    }
    
    /* Style the upload text */
    .stFileUploader > div > div > div {
        gap: 0.5rem;
    }
    
    /* Style the processing options */
    .processing-header {
        color: #1E88E5;
        font-size: 1.5rem !important;
        font-weight: 500;
        margin: 2rem 0 1rem 0 !important;
    }
    
    /* Style the checkboxes */
    .stCheckbox {
        margin: 1rem 0;
    }
    
    /* Style the download button */
    .stDownloadButton {
        margin-top: 2rem;
        padding: 0.75rem 1.5rem;
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        text-decoration: none;
        font-weight: 500;
    }
    
    .stDownloadButton:hover {
        background-color: #1976D2;
    }
    
    /* Style the expanders */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    
    /* Style the text areas */
    .stTextArea {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stTextArea>div>div>textarea {
        font-family: monospace;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1em;
    }
    .streamlit-expanderHeader {
        font-weight: normal;
        color: #666;
    }
    </style>
""", unsafe_allow_html=True)

# Add custom CSS to ensure download button text is always visible
st.markdown("""
    <style>
        /* Custom button styling */
        .stDownloadButton button {
            background-color: #007bff;
            color: white !important;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 4px;
        }
        .stDownloadButton button:hover {
            background-color: #0056b3;
            border: none;
        }
        .stDownloadButton button p {
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for prompts
if 'custom_prompts' not in st.session_state:
    st.session_state.custom_prompts = {
        'notebook_intro': DefaultPrompts.NOTEBOOK_INTRO,
        'code_optimization': DefaultPrompts.CODE_OPTIMIZATION,
        'code_comments': DefaultPrompts.CODE_COMMENTS,
        'markdown_explanation': DefaultPrompts.MARKDOWN_EXPLANATION,
        'notebook_summary': DefaultPrompts.NOTEBOOK_SUMMARY
    }

# Title and description with custom classes
st.markdown('<h1 class="main-header">🔍 Notebook Explainify</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="app-description">Transform your Jupyter notebooks with AI-powered explanations, formatting, and documentation. '
    'Upload your notebook and customize the processing options below.</p>',
    unsafe_allow_html=True
)

# File uploader
uploaded_file = st.file_uploader(
    "Choose a Jupyter notebook file",
    type=["ipynb"],
    help="Maximum file size: 200MB",
    label_visibility="collapsed"
)

# Check file size
if uploaded_file is not None:
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
    if file_size > 200:
        st.error("File size exceeds 200MB limit. Please upload a smaller file.")
    else:
        # Processing Options section with custom class
        st.markdown('<h2 class="processing-header">Processing Options</h2>', unsafe_allow_html=True)
        
        # Add Introduction
        add_intro = st.checkbox(
            "**📝 Add Introduction**",
            value=True,
            help="Add an introduction at the beginning"
        )
        if add_intro:
            with st.expander("🔧 Fine-tune Introduction Prompt"):
                st.session_state.custom_prompts['notebook_intro'] = st.text_area(
                    "Customize Introduction Prompt",
                    value=st.session_state.custom_prompts['notebook_intro'],
                    height=200,
                    key="intro_prompt"
                )
        
        # Add Comments
        add_comments = st.checkbox(
            "**💭 Add Comments**",
            value=True,
            help="Add explanatory comments to code cells"
        )
        if add_comments:
            with st.expander("🔧 Fine-tune Comments Prompt"):
                st.session_state.custom_prompts['code_comments'] = st.text_area(
                    "Customize Comments Prompt",
                    value=st.session_state.custom_prompts['code_comments'],
                    height=200,
                    key="comments_prompt"
                )
        
        # Add Markdown
        add_markdown = st.checkbox(
            "**📖 Add Markdown**",
            value=True,
            help="Add explanatory markdown cells"
        )
        if add_markdown:
            with st.expander("🔧 Fine-tune Markdown Prompt"):
                st.session_state.custom_prompts['markdown_explanation'] = st.text_area(
                    "Customize Markdown Prompt",
                    value=st.session_state.custom_prompts['markdown_explanation'],
                    height=200,
                    key="markdown_prompt"
                )
        
        # Add Summary
        add_summary = st.checkbox(
            "**📋 Add Summary**",
            value=False,
            help="Add a summary at the end"
        )
        if add_summary:
            with st.expander("🔧 Fine-tune Summary Prompt"):
                st.session_state.custom_prompts['notebook_summary'] = st.text_area(
                    "Customize Summary Prompt",
                    value=st.session_state.custom_prompts['notebook_summary'],
                    height=200,
                    key="summary_prompt"
                )
        
        # Optimize Code
        optimize_code = st.checkbox(
            "**⚡ Optimize Code**",
            value=False,
            help="Suggest code optimizations"
        )
        if optimize_code:
            with st.expander("🔧 Fine-tune Optimization Prompt"):
                st.session_state.custom_prompts['code_optimization'] = st.text_area(
                    "Customize Optimization Prompt",
                    value=st.session_state.custom_prompts['code_optimization'],
                    height=200,
                    key="optimize_prompt"
                )
        
        # Format Code
        format_code = st.checkbox(
            "**🎨 Format Code**",
            value=True,
            help="Format code cells using Black"
        )
        
        # Process button
        if st.button("🚀 Process Notebook", use_container_width=True):
            with st.spinner("Processing your notebook..."):
                try:
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.ipynb') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        input_path = tmp_file.name
                    
                    # Create output path
                    output_path = os.path.join(tempfile.gettempdir(), "processed_notebook.ipynb")
                    
                    # Initialize processors with custom prompts
                    llm = LLMProcessor(prompts=st.session_state.custom_prompts)
                    processor = NotebookProcessor(llm_processor=llm)
                    processor.load_notebook(input_path)
                    
                    # Process the notebook with selected options
                    processor.explainify_notebook(
                        output_path=output_path,
                        to_format=format_code,
                        to_comment=add_comments,
                        to_optimize=optimize_code,
                        to_markdown=add_markdown,
                        to_intro=add_intro,
                        to_summary=add_summary
                    )
                    
                    # Read the processed file
                    with open(output_path, 'rb') as file:
                        processed_notebook = file.read()
                    
                    # Clean up temporary files
                    os.unlink(input_path)
                    os.unlink(output_path)
                    
                    # Success message with custom styling
                    st.markdown("""
                        <div style="padding: 1rem; background-color: #e8f5e9; border-radius: 5px; margin: 1rem 0;">
                            <h3 style="color: #2e7d32; margin: 0;">✅ Processing Complete!</h3>
                            <p style="color: #1b5e20; margin: 0.5rem 0 0 0;">Your notebook has been successfully processed.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Download button with custom styling
                    col1, col2, col3 = st.columns([2, 1, 2])
                    with col2:
                        st.download_button(
                            label="Download notebook",
                            data=processed_notebook,
                            file_name=f"explainified_{uploaded_file.name}",
                            mime="application/x-ipynb+json",
                            type="primary",
                        )
                
                except Exception as e:
                    # Error message with custom styling
                    st.markdown(f"""
                        <div style="padding: 1rem; background-color: #ffebee; border-radius: 5px; margin: 1rem 0;">
                            <h3 style="color: #c62828; margin: 0;">❌ Processing Error</h3>
                            <p style="color: #b71c1c; margin: 0.5rem 0 0 0;">An error occurred while processing your notebook: {str(e)}</p>
                        </div>
                    """, unsafe_allow_html=True)

# Add footer with information
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ using Streamlit</p>
    </div>
""", unsafe_allow_html=True)
