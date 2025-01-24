# AiDA-CLI: AI Document Assistant

<div style="display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 20px;">
  <img src="Design/logo.png" alt="AiDA-CLI Logo" width="100"/>
  <h1 style="font-family: 'Poppins', sans-serif;">AiDA - CLI</h1>
</div>

## Overview

AiDA-CLI is a powerful command-line interface tool that enables users to interact with and query documents intelligently. It serves as an AI-powered document assistant capable of handling various document formats including PDF, PPTX, DOCX, TXT, and Markdown files.

## Features

- **Multi-format Support**: Process and analyze PDF, PPTX, DOCX, TXT, and Markdown files
- **Intelligent Querying**: Ask questions about your documents and get relevant answers
- **Web Search Integration**: Search the web to supplement document-based answers
- **Code Execution**: Generate and run Python code for data visualization and analysis
- **Content Generation**: Create and save learning materials based on document content
- **RAG Implementation**: Utilizes Retrieval Augmented Generation for accurate responses
- **Groq Integration**: Powered by Groq's LLM capabilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Adhish-Krishna/AiDA-CLI.git
cd AiDA-CLI
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your Groq API key to the `.env` file:
```
GROQ_API_KEY = your_api_key_here
```

## Usage

Run AiDA-CLI using:
```bash
python aida-cli.py
```

## Configuration

The system uses the following key components:
- Groq LLM (llama-3.3-70b-versatile model by default. Model can be changed)
- HuggingFace Embeddings
- ChromaDB for vector storage
- Rich for console output formatting



For more information or support, please open an issue in the repository.