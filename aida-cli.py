'''
  AiDA-CLI : AI Document Assistant - Command Line Interface
  - It is a command line based agent which helps the user to chat with their documents no matter how complex the document is whether it is a pdf, pptx, docx, txt or markdown files, AiDA can handle them.
  - As of now AiDA, in its core uses Groq as its LLM provider. The user needs to provide the Groq API key in a .env file. See README.md for further instructions.
  - AiDA lets the users to choose between the multiple models provided by Groq

  What AiDA is capable of?
    - AiDA is an AI Agent that lets users to upload their document (pdf, pptx, docx, txt or markdown files) and ask questions about them.
    - AiDA is also capable of searching the web for the answers for the user's query
    - For complex user query AiDA can write python code and execute it and answer to the user's query (For example when the user asks to visualize some data, AiDA can to do that)
    - It can save content to the file system when the user asks about it. (For example when the user uploads a book or a pdf and asks AiDA to create a learning material, it reads through the pdf and creates a learning material and saves it in the file system and the user can use it to learn)

'''

# Importing necessary modules and libraries

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live

# Load the Groq API Key from the .env file
load_dotenv()

#Initializing the model
model = ChatGroq(model="llama-3.3-70b-versatile")

#Initializing the Console from rich
console = Console()

#Streams the response from the llm in markdown to the console
def display_streaming_markdown(prompt: str) -> None:
    markdown_output = ""

    with Live(Markdown(markdown_output), console=console, refresh_per_second=10) as live:
        for chunk in model.stream(prompt):
            markdown_output += chunk.content
            live.update(Markdown(markdown_output))

# Example usage
prompt = "generate point wise content of deep learning in about 300 words"
display_streaming_markdown(prompt)