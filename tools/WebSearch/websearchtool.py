from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def web_search(query: str) -> str:
  context = tavily_client.get_search_context(query=query,max_tokens=1000,max_results=3)
  return context