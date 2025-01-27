from tavily import TavilyClient
from dotenv import load_dotenv
import os

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def scrapWebsite(url: str | list, query: str):
  context = ""
  urls = [url] if isinstance(url,str) else url
  response = tavily_client.extract(urls=urls, include_images=False)
  for res in response["results"]:
    context += f"URL: {res["url"]}\n Raw Conent: {res['raw_content']}\n"
  context += f"\n Answer the below query using the above context: \n Query: {query}"
  return context