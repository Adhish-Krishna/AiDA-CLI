# <center>AiDA-CLI: AI Document Assistant</center>

<div style="display: flex; flex-direction: row; align-items: center; justify-content: center; gap: 20px;">
  <img src="./Design/Logo.png" alt="AiDA-CLI Logo" width="100"/>
  <h1 style="font-family: 'Poppins', sans-serif;">AiDA - CLI</h1>
</div>

## Overview

AiDA-CLI is a powerful command-line interface tool that enables users to interact with and query documents intelligently. It serves as an AI-powered document assistant capable of handling various document formats including PDF, PPTX, DOCX, TXT, and Markdown files.

## AiDA Agent V 0.1
  ### Overview
  - The **AiDA Agent V 0.1** is a simple tool-calling agent. It is preferred for simple questions. It can retireve context from uploaded documents, can do web-search if it is not sure about the infromation and even scrap web pages if link is provided.
  ### Available Features
  - **Multi-format Support**: Process and analyze PDF, PPTX, DOCX, and Markdown files
  - **Intelligent Querying**: Ask questions about your documents and get relevant answers
  - **RAG Implementation**: Utilizes Retrieval Augmented Generation for accurate responses
  - **Groq Integration**: Powered by Groq's LLM capabilities (**Supported models**: llama-3.2-11b-vision-preview, llama-3.3-70b-versatile, llama-3.3-70b-specdec, llama-3.2-90b-vision-preview, mixtral-8x7b-32768)
  - **Web Search Integration**: Search the web to supplement document-based answers
  - **Web Scraping**: Give a Web URL and then chat with its content

  ### Upcoming Features
  - **Extended Document Support**: Support for xlxs, txt and image documents for document chat.

  ### Demo
  [Watch Demo](https://drive.google.com/file/d/187NGwRyUe1kw6DRC3sTpC4rvIFU9IKYr/view?usp=sharing)

## AiDA Agent V 0.2
  - Coming Soon

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
- Add your Groq API key to the `.env` file
- Add your Tavily API Key for Web Search
```
GROQ_API_KEY =<your groq api key>
GROQ_MODEL_NAME = llama-3.3-70b-versatile (model can be changed. But not all groq models are suppoted. See supported models for details)
TAVILY_API_KEY = <your tavily api key>
```

## Usage

Run AiDA Agent V 0.1 using:
```bash
python aida-agent-v-0.1.py
```

## Configuration

The system uses the following key components:
- Groq LLM (llama-3.3-70b-versatile model by default. Model can be changed)
- HuggingFace Embeddings
- ChromaDB for vector storage
- Rich for console output formatting



For more information or support, please open an issue in the repository.