'''
    AiDA Agent V 0.1.1

        Overview
            The AiDA Agent V 0.1.1 is an updated version of the AiDA Agent V 0.1. Now the AiDA Agent V 0.1.1 uses langgraph. It is also a tool calling agent but it can call multiple tools sequentially or parallely based on the query. It can retireve context from uploaded documents, can do web-search if it is not sure about the infromation and even scrap web pages if link is provided.

        Available Features
            - Multi-format Support: Process and analyze PDF, PPTX, DOCX, and Markdown files
            - Intelligent Querying: Ask questions about your documents and get relevant answers
            - RAG Implementation: Utilizes Retrieval Augmented Generation for accurate responses
            - Groq Integration: Powered by Groq's LLM capabilities (**Supported models**: llama-3.  2-11b-vision-preview, llama-3.3-70b-versatile, llama-3.3-70b-specdec, llama-3.2-90b-vision-preview, mixtral-8x7b-32768)
            - Ollama Support for local models: Supports local models (only function calling LLMS supported. Eg qwen2.5:3b, qwen2.5:latest) via Ollama
            - Web Search Integration: Search the web to supplement document-based answers
            - Web Scraping: Give a Web URL and then chat with its content
            - Save Content: Saves the generated content to the file system
'''

'''
Features need to add:
  - To support token streaming
  - To use Graph RAG Technique for advanced document retrieval
  - To support multi-modal inputs (like image inputs)
  - To enhance chat history for the modal
'''

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from tools import DocumentRetrieverTool, WebSearchTool, WebScraperTool, SaveContentTool
import operator
from langchain_community.chat_message_histories import SQLChatMessageHistory
from utils.chat_util import _save_chat_session, _load_chat_session, _detect_document_query
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
import os
from prompts.prompt import aida_v011_prompt

class AgentState(TypedDict):
  messages: Annotated[list[AnyMessage],operator.add]

class Agent:
  def __init__(self, provider: str, model_name: str, system_prompt: str, tools: list):
    self.checkpointer = MemorySaver()
    self.system = system_prompt
    self.tools = {t.name: t for t in tools}
    self.llm = self.get_llm(provider=provider, model_name=model_name).bind_tools(tools)
    graph = StateGraph(AgentState)
    graph.add_node("llm", self.llm_node)
    graph.add_node("tools", self.tool_node)
    graph.add_conditional_edges("llm", self.conditional_edge, {True:"tools", False:END})
    graph.add_edge("tools", "llm")
    graph.set_entry_point("llm")
    self.graph = graph.compile(checkpointer=self.checkpointer)

  def get_llm(self, provider: str, model_name: str):
    if provider == 'ollama':
      return ChatOllama(model=model_name)
    elif provider == 'azure':
      return AzureChatOpenAI(model=model_name, api_version='2024-05-01-preview')
    else:
      return ChatGroq(model=model_name)

  def llm_node(self, state: AgentState):
    messages = state["messages"]
    if self.system:
      messages = [SystemMessage(content=self.system)] + messages
    response = self.llm.invoke(messages)
    return {"messages":[response]}

  def tool_node(self, state: AgentState):
    tool_calls = state["messages"][-1].tool_calls
    results = []
    for t in tool_calls:
      if t["name"] in self.tools:
        if t["name"] == "DocumentRetrieval":
          args = t["args"]
          filepath = args["filepath"]
          filepath = str(filepath.strip())
          t["args"]["filepath"] = filepath
        rprint(f"[blue]Using Tool: {t["name"]}[blue]")
        result = self.tools[t["name"]].invoke(t["args"])
        results.append(ToolMessage(content=str(result), tool_name=t["name"], tool_call_id = t["id"]))
      else:
        rprint("[red]Requested Tool is not available[red]")
    rprint("[blue]Analysing...[blue]")
    return {"messages":results}

  def conditional_edge(self, state: AgentState):
    tool_calls = state["messages"][-1].tool_calls
    if len(tool_calls)>0:
      return True
    else:
      return False

def get_model_name(provider: str, groq: str, ollama: str, azure: str)->str:
  if provider == 'ollama':
    return ollama
  elif provider == 'azure':
    return azure
  else:
    return groq


def chat():

  load_dotenv()
  groq_model_name = os.getenv('GROQ_MODEL_NAME')
  ollama_model_name = os.getenv('OLLAMA_MODEL_NAME')
  azure_model_name = os.getenv('AZURE_MODEL_NAME')
  default_provider = os.getenv('DEFAULT_PROVIDER')
  console = Console()
  tools = [DocumentRetrieverTool, WebScraperTool, WebSearchTool, SaveContentTool]
  chat_history = SQLChatMessageHistory(
    session_id="aida_chat_session",
    connection="sqlite:///aida_v0.1.1_chat_history.db"
  )

  prompt = aida_v011_prompt

  agent = Agent(provider=default_provider, model_name=get_model_name(default_provider, groq_model_name, ollama_model_name, azure_model_name), system_prompt=prompt, tools = tools)
  config = {"configurable":{"thread_id":"1"}}
  chat_history.add_message(SystemMessage(content=prompt))
  isChatLoaded = False
  rprint("[bold green]AiDA - CLI : AI Document Assistant V 0.1.1[/bold green]")
  rprint(f"[blue]LLM Provider: {default_provider} \nModel: {get_model_name(default_provider, groq_model_name, ollama_model_name, azure_model_name)}[blue]")
  rprint("[italic]Type 'exit' to end conversation, '/save' to save, '/load' to load[/italic]\n")

  while True:
    user = Prompt.ask("[bold yellow]User[/bold yellow] ").strip()

    doc_info = _detect_document_query(user)

    if doc_info:
      filepath, query = doc_info
      document_query_prompt = f"Use the below filepath (use as such don't change anyting in the filepath) and query to call the DocumentRetriever Tool: filepath: {filepath} , query: {query}"
      user = document_query_prompt

    if user == "exit":
      chat_history.clear()
      break

    elif user == "/save":
      _save_chat_session(chat_history=chat_history)

    elif user == "/load":
      _load_chat_session(chat_history=chat_history)
      messages = chat_history.get_messages()
      isChatLoaded = True

    else:
      if isChatLoaded:
        messages = messages + [HumanMessage(content=user)]
        isChatLoaded = False
      else:
        messages = [HumanMessage(content=user)]

      chat_history.add_user_message(user)
      response = agent.graph.invoke({"messages":messages},config=config)
      rprint("[bold green]AiDA:[/bold green]")
      chat_history.add_ai_message(response["messages"][-1].content)
      console.print(Markdown(response["messages"][-1].content))

if __name__ == "__main__":
  chat()