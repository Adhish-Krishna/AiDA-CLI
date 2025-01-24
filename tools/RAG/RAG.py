from tools.RAG.Chunking import ChunkDocument
from tools.RAG.Retrieve import RetrieveChunks
from langchain_core.tools import Tool
from rich import print as rprint
from typing import Union

@Tool
def RAG(filepath: str, query: str) -> Union[str, None]:
  '''
  Retrieves context from the vector database based on the given query
  Arguments:
    filepath: str - the filepath of the document to query about
    query : str - the query from the user
  Output:
    context : str | None - the retrieved context from the vector database or else return None
  '''
  filepath = filepath.replace("\\", "/")

  try:
    context = ""
    # Parse and chunk the document
    chunking = ChunkDocument(filepath)

    if not chunking.parseDocument():
      try:
        chunking.initializeEmbeddings()
        chunking.storeEmbeddings()
      except Exception as e:
        rprint(f"[red]Error during embedding initialization: {str(e)}[/red]")
        return None

    # Retrieve context based on the query
    try:
      retrieve = RetrieveChunks(filepath, query)
      chunks: list = retrieve.retrieveChunks()
    except Exception as e:
      rprint(f"[red]Error during chunk retrieval: {str(e)}[/red]")
      return None

    for j, i in enumerate(chunks):
      context += f"Document: {j+1}\n{i}\n"

    return context

  except FileNotFoundError:
    rprint(f"[red]Error: File '{filepath}' not found[/red]")
    return None
  except Exception as e:
    rprint(f"[red]Unexpected error: {str(e)}[/red]")
    return None