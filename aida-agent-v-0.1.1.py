from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, ToolMessage
from typing import Annotated, TypedDict
from dotenv import load_dotenv
from tools.RAG.RAG import DocumentRetrieverTool
from tools.WebSearch.websearchtool import WebSearchTool
from tools.WebsiteScraper.website_scraper import WebScraperTool
import operator
from langchain_community.chat_message_histories import SQLChatMessageHistory
from utils.chat_util import _save_chat_session, _load_chat_session
from rich import print as rprint
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
import os

class AgentState(TypedDict):
  messages: Annotated[list[AnyMessage],operator.add]

class Agent:
  def __init__(self, provider: str, model_name: str, system_prompt: str, tools: list):
    self.checkpointer = MemorySaver()
    self.system = system_prompt
    self.tools = {t.name: t for t in tools}
    self.llm = (ChatOllama(model=model_name) if provider == 'ollama' else ChatGroq(model=model_name)).bind_tools(tools)
    graph = StateGraph(AgentState)
    graph.add_node("llm", self.llm_node)
    graph.add_node("tools", self.tool_node)
    graph.add_conditional_edges("llm", self.conditional_edge, {True:"tools", False:END})
    graph.add_edge("tools", "llm")
    graph.set_entry_point("llm")
    self.graph = graph.compile(checkpointer=self.checkpointer)

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
        result = self.tools[t["name"]].invoke(t["args"])
        results.append(ToolMessage(content=str(result), tool_name=t["name"], tool_call_id = t["id"]))
        print(f"Calling {t}")
      else:
        print("Requested Tool is not available")
    print("Back to the model")
    return {"messages":results}

  def conditional_edge(self, state: AgentState):
    tool_calls = state["messages"][-1].tool_calls
    if len(tool_calls)>0:
      return True
    else:
      return False

def chat():

  load_dotenv()
  groq_model_name = os.getenv('GROQ_MODEL_NAME')
  ollama_model_name = os.getenv('OLLAMA_MODEL_NAME')
  default_provider = os.getenv('DEFAULT_PROVIDER')
  console = Console()
  tools = [DocumentRetrieverTool, WebScraperTool, WebSearchTool]
  chat_history = SQLChatMessageHistory(
    session_id="aida_chat_session",
    connection="sqlite:///aida_v0.1.1_chat_history.db"
  )

  prompt = """You are AiDA, an AI Document Assistant.\
  When answering document-related questions, only use the DocumentRetrieval tool if the user explicitly provides a valid filepath (e.g., ending with .pdf, .docx, .pptx, .txt, or .md) along with a specific question about the document content. Never assume a file path if it is not provided.\
  Example: User: "C:\\Users\\strea\\Downloads\\MathsPaper.pdf" sumarize this doc
  Then the filepath = "C:\\Users\\strea\\Downloads\\MathsPaper.pdf" and the query = sumarize this doc
  You have WebSearch Tool to search the web with provided query. \
  You have WebsiteScraper tool to scrap the website with provided Web URL and the query. \
  You are allowed to make multiple calls (either together or in sequence). \
  Only look up information when you are sure of what you want. \
  If you need to look up some information before asking a follow up question, you are allowed to do that!
  """

  agent = Agent(provider=default_provider, model_name=(ollama_model_name if default_provider == 'ollama' else groq_model_name), system_prompt=prompt, tools = tools)
  config = {"configurable":{"thread_id":"1"}}
  chat_history.add_message(SystemMessage(content=prompt))
  isChatLoaded = False
  rprint("[bold green]AiDA - CLI : AI Document Assistant V 0.1.1[/bold green]")
  rprint(f"[blue]LLM Provider: {default_provider} \nModel: {ollama_model_name if default_provider == 'ollama' else groq_model_name}[blue]")
  rprint("[italic]Type 'exit' to end conversation, '/save' to save, '/load' to load[/italic]\n")

  while True:
    user = Prompt.ask("[bold yellow]User[/bold yellow] ").strip()

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