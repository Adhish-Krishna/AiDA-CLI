# <center>AiDA-CLI: AI Document Assistant</center>
<center><img src="./Design/Logo.png" alt="AiDA-CLI Logo" width="100"/></center>

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
  - **Ollama Support for local models**: Supports local models (only function calling LLMS supported. Eg qwen2.5:3b) via Ollama
  - **Web Search Integration**: Search the web to supplement document-based answers
  - **Web Scraping**: Give a Web URL and then chat with its content

  ### Upcoming Features
  - **Extended Document Support**: Support for xlxs, txt and image documents for document chat.

  ### Demo
  [AiDA Agent V 0.1](https://drive.google.com/file/d/1g9o8G1SVEvMtIKhjdWpr5IR5ueAh1weO/view?usp=sharing)

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
- Add your Groq API key for llm usage
- Add your Tavily API Key for Web Search
```
GROQ_API_KEY =<your groq api key>
GROQ_MODEL_NAME = llama-3.3-70b-versatile (cange this as your wish. But note only function calling llms supported)
OLLAMA_MODEL_NAME = qwen2.5:3b (cange this as your wish. But note only function calling llms supported)
DEFAULT_PROVIDER = groq
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
- Ollama (for local llm usage)
- Tavily for Web Search and Website Scraping
- HuggingFace Embeddings
- ChromaDB for vector storage
- Rich for console output formatting



For more information or support, please open an issue in the repository.