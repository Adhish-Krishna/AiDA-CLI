from tools.RAG.RAG import RAG_Tool

context = RAG_Tool(r"{}".format(input("Enter the file path: ")),input("Enter your Query: "))

print(context)