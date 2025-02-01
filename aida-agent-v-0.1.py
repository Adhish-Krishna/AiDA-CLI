'''
    AiDA Agent V 0.1

        Overview
            The AiDA Agent V 0.1 is a simple tool-calling agent. It is preferred for simple questions. It can retireve context from uploaded documents, can do web-search if it is not sure about the infromation and even scrap web pages if link is provided.

        Available Features
            - Multi-format Support: Process and analyze PDF, PPTX, DOCX, and Markdown files
            - Intelligent Querying: Ask questions about your documents and get relevant answers
            - RAG Implementation: Utilizes Retrieval Augmented Generation for accurate responses
            - Groq Integration: Powered by Groq's LLM capabilities (**Supported models**: llama-3.  2-11b-vision-preview, llama-3.3-70b-versatile, llama-3.3-70b-specdec, llama-3.2-90b-vision-preview, mixtral-8x7b-32768)
            - Ollama Support for local models: Supports local models (only function calling LLMS supported. Eg qwen2.5:3b) via Ollama
            - Web Search Integration**: Search the web to supplement document-based answers
            - Web Scraping: Give a Web URL and then chat with its content
'''

import os
import re
from dotenv import load_dotenv
from rich import print as rprint
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.live import Live
from rich.console import Console
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_community.chat_message_histories import SQLChatMessageHistory
from utils.chat_util import _process_input, _process_stream_chunk, _save_chat_session, _load_chat_session

# Importing RAG Tool
from tools.RAG.RAG import DocumentRetrieverTool

#Importing WebSearch Tool
from tools.WebSearch.websearchtool import WebSearchTool

#Importing the WebsiteScraper Tool
from tools.WebsiteScraper.website_scraper import WebScraperTool

load_dotenv()
groq_model_name = os.getenv('GROQ_MODEL_NAME')
ollama_model_name = os.getenv('OLLAMA_MODEL_NAME')
default_provider = os.getenv('DEFAULT_PROVIDER')
console = Console()

model = ChatOllama(model=ollama_model_name) if default_provider=='ollama' else ChatGroq(model=groq_model_name)

class AIDAAgent:
    def __init__(self):
        self.llm = model
        #Add Tools here
        self.tools = [
            DocumentRetrieverTool,
            WebSearchTool,
            WebScraperTool
        ]

        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are AiDA - Artificial Intelligence Document Assistant. Follow these rules:
                1. Document Questions:
                - Use DocumentRetrieval ONLY when user provides BOTH:
                a) Explicit file path (e.g., .pdf, .docx)
                b) Specific document-related question
                - Never assume document paths - require explicit user input

                2. General Knowledge:
                - Use built-in knowledge for common questions
                - Acknowledge when unsure

                3. Response Guidelines:
                - For documents: cite exact text excerpts
                - For general questions: keep answers concise
                - Always verify document existence before use

                4. Web Search:
                - For queries needing external or up-to-date data, use the 'WebSearch' tool with a relevant query.
            """),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            max_iterations=3,
            handle_parsing_errors=True
        )

        self.chat_history = SQLChatMessageHistory(
            session_id="aida_session",
            connection="sqlite:///aida_chat_history.db"
        )

        # Create chats directory if not exists
        os.makedirs("chats", exist_ok=True)

    def chat(self):
        rprint("[bold green]AiDA - CLI : AI Document Assistant V 0.1[/bold green]")
        rprint(f"[blue]LLM Provider: {default_provider} \nModel: {ollama_model_name if default_provider == 'ollama' else groq_model_name}[blue]")
        rprint("[italic]Type 'exit' to end conversation, '/save' to save, '/load' to load[/italic]\n")

        while True:
            try:
                user_input = Prompt.ask("[bold yellow]User[/bold yellow] ").strip()

                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    self.chat_history.clear()
                    break
                elif user_input == "/save":
                    _save_chat_session(self.chat_history)
                    continue
                elif user_input == "/load":
                    _load_chat_session(self.chat_history)
                    continue

                # Process normal input
                processed = _process_input(user_input)
                self.chat_history.add_user_message(user_input)

                full_response = []
                markdown_content = ""
                final_output = ""
                rprint("[bold green]AiDA:[/bold green]")

                with Live(Markdown(markdown_content), auto_refresh=False, console=console) as live:
                    for chunk in self.agent_executor.stream({
                        "input": processed["input"],
                        "chat_history": self.chat_history.messages
                    }):
                        chunk_content = _process_stream_chunk(chunk)

                        if chunk_content:
                            full_response.append(chunk_content)
                            markdown_content += chunk_content
                            live.update(Markdown(markdown_content), refresh=True)

                        if isinstance(chunk, dict) and "output" in chunk:
                            final_output = chunk["output"]

                # Update chat history
                if final_output and not full_response:
                    self.chat_history.add_ai_message(final_output)
                    rprint(f"[bold cyan]AiDA:[/bold cyan] {Markdown(final_output)}\n")
                else:
                    self.chat_history.add_ai_message("".join(full_response))

                console.print("\n")

            except KeyboardInterrupt:
                self.chat_history.clear()
                break
            except Exception as e:
                rprint(f"[red]Error: {str(e)}[/red]")

if __name__ == '__main__':
    agent = AIDAAgent()
    agent.chat()