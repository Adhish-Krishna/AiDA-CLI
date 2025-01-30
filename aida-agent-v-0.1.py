import os
import re
from dotenv import load_dotenv
from rich import print as rprint
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich.live import Live
from rich.console import Console
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, AIMessageChunk, HumanMessage, AIMessage
from langchain_core.tools import StructuredTool
from langchain_community.chat_message_histories import SQLChatMessageHistory
from pydantic import BaseModel, Field
from typing import Dict, Optional, Tuple, Any


# Importing RAG Tool
from tools.RAG.RAG import RAG

#Importing WebSearch Tool
from tools.WebSearch.websearchtool import web_search

#Importing the WebsiteScraper Tool
from tools.WebsiteScraper.website_scraper import scrapWebsite

load_dotenv()
groq_model_name = os.getenv('GROQ_MODEL_NAME')
console = Console()

class DocumentQueryInput(BaseModel):
    filepath: str = Field(..., description="Full path to the document file")
    query: str = Field(..., description="Specific question or task for the document")

class WebSearchInput(BaseModel):
    query: str = Field(..., description="The query to search on the web.")

class ScrapWebsite(BaseModel):
    url : str | list = Field(..., description="a single web url or a python list of web urls" )
    query: str = Field(..., description="Specific question or task about the content of the website")


class AIDAAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model=groq_model_name,
            temperature=0.3
        )
        #Add Tools here
        self.tools = [
            StructuredTool.from_function(
                func=self._rag_wrapper,
                name="DocumentRetrieval",
                description="""ONLY use for questions about SPECIFIC DOCUMENTS.
                Requires both filepath and query. File must exist locally.
                Input format: {{"filepath": "path/to/file", "query": "your question"}}""",
                args_schema=DocumentQueryInput
            ),
            StructuredTool.from_function(
                func=web_search,
                name="WebSearch",
                description="""Use for queries that require up-to-date or external data from the internet.
                Input format: {{"query": "your question"}}""",
                args_schema=WebSearchInput
            ),
            StructuredTool.from_function(
                func=scrapWebsite,
                name="WebsiteScraper",
                description="""ONLY use this tool when the user provides any WEB URLs. This tool scraps the website and gives the context.
                INPUT format: {{"url":"WEB URL", "query":"your question"}}""",
                args_schema=ScrapWebsite
            )
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

    def _detect_document_query(self, input_text: str) -> Optional[Tuple[str, str]]:
        quoted_path_match = re.search(r'"([^"]+\.(pdf|docx|pptx|txt|md))"', input_text)
        if quoted_path_match:
            filepath = quoted_path_match.group(1)
            query = input_text.replace(quoted_path_match.group(0), "").strip()
            return (filepath, query)

        path_match = re.search(r'(\S+\.(pdf|docx|pptx|txt|md))\s+(.+)', input_text)
        if path_match:
            return (path_match.group(1), path_match.group(3))

        return None

    def _rag_wrapper(self, filepath: str, query: str) -> str:
        try:
            if not os.path.exists(filepath):
                return f"Error: File {filepath} not found"
            context = RAG(filepath, query)
            return context if context else "No relevant content found in document"
        except Exception as e:
            return f"Document processing error: {str(e)}"



    def _process_input(self, user_input: str) -> Dict:
        doc_info = self._detect_document_query(user_input)
        if doc_info:
            filepath, query = doc_info
            return {
                "input": f"Document query: {query}",
                "tool_input": {"filepath": filepath, "query": query}
            }
        return {"input": user_input}

    def _process_stream_chunk(self, chunk: Any) -> str:
        """Extract content from different chunk types"""
        if isinstance(chunk, AIMessageChunk):
            return chunk.content
        if isinstance(chunk, dict):
            return chunk.get("output", "")
        return ""

    def _save_chat_session(self):
        """Save current chat session to separate database"""
        name = Prompt.ask("[bold green]Enter the name of the chat to save[/bold green]").strip()
        filename = f"chats/chat_{name}.db"

        # Create new database
        saved_chat = SQLChatMessageHistory(
            session_id="saved_session",
            connection=f"sqlite:///{filename}"
        )

        # Copy messages
        for message in self.chat_history.messages:
            if isinstance(message, HumanMessage):
                saved_chat.add_user_message(message.content)
            elif isinstance(message, AIMessage):
                saved_chat.add_ai_message(message.content)

        rprint(f"[green]Chat saved to {filename}[/green]")

    def _load_chat_session(self):
        """Load chat session from saved database"""
        chat_files = [f for f in os.listdir("chats") if f.endswith(".db")]
        if not chat_files:
            rprint("[red]No saved chats found[/red]")
            return

        rprint("[bold]Available chats:[/bold]")
        for idx, file in enumerate(chat_files, 1):
            rprint(f"{idx}. {file}")

        try:
            selection = IntPrompt.ask("Enter chat number to load", default=1, show_default=False)
            selected_file = chat_files[selection - 1]
        except (ValueError, IndexError):
            rprint("[red]Invalid selection[/red]")
            return

        # Load selected chat
        filepath = os.path.join("chats", selected_file)
        loaded_chat = SQLChatMessageHistory(
            session_id="saved_session",
            connection=f"sqlite:///{filepath}"
        )

        # Clear current history and load messages
        self.chat_history.clear()
        for message in loaded_chat.messages:
            if isinstance(message, HumanMessage):
                self.chat_history.add_user_message(message.content)
            elif isinstance(message, AIMessage):
                self.chat_history.add_ai_message(message.content)

        rprint(f"[green]Loaded chat from {selected_file}[/green]")

    def chat(self):
        rprint("[bold green]AiDA - CLI : AI Document Assistant[/bold green]")
        rprint("[italic]Type 'exit' to end conversation, '/save' to save, '/load' to load[/italic]\n")

        while True:
            try:
                user_input = Prompt.ask("[bold yellow]User[/bold yellow] ").strip()

                # Handle commands
                if user_input.lower() in ['exit', 'quit']:
                    self.chat_history.clear()
                    break
                elif user_input == "/save":
                    self._save_chat_session()
                    continue
                elif user_input == "/load":
                    self._load_chat_session()
                    continue

                # Process normal input
                processed = self._process_input(user_input)
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
                        chunk_content = self._process_stream_chunk(chunk)

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