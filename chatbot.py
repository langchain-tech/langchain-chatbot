# Import necessary modules
from colorama import init, Fore, Style
import os
import json
from utils.ingest import ingest
from utils.query import query
from dotenv import load_dotenv

# Initialize colorama module
init()

# Load environment variables
load_dotenv()

# Get API keys and settings from environment variables
openai_api_key = os.environ.get('OPENAI_API_KEY')
pinecone_api_key = os.environ.get('PINECONE_API_KEY')
pinecone_environment = os.environ.get('PINECONE_ENVIRONMENT')
pinecone_index = os.environ.get('PINECONE_INDEX')
pinecone_namespace = 'testing-pdf-0001'
temperature = 0.7
source_amount = 4

# Print the startup display
print(f"""{Fore.WHITE}Using the following credentials:{Fore.WHITE}
OpenAI API Key: {Fore.RED}{openai_api_key}{Fore.WHITE}
Pinecone API Key: {Fore.BLUE}{pinecone_api_key}{Fore.WHITE}
Pinecone Environment: {Fore.BLUE}{pinecone_environment}{Fore.WHITE}
Pinecone Index: {Fore.BLUE}{pinecone_index}{Fore.WHITE}
Pinecone Namespace: {Fore.GREEN}{pinecone_namespace}{Fore.WHITE}

{Fore.WHITE}Using the following settings:{Fore.WHITE}
Temperature (Creativity): {Fore.MAGENTA}{temperature}{Fore.WHITE}
Sources (Cites): {Fore.MAGENTA}{source_amount}{Fore.WHITE}
""")

# Check whether the user wants to use Pinecone
r = input('Do you want to use Pinecone? (Y/N): ')
if r == 'Y' and pinecone_api_key != '':
    use_pinecone = True
else:
    print('Not using Pinecone or empty Pinecone API key provided. Using Chroma instead')
    use_pinecone = False

# Check whether the user wants to ingest
r = input('Do you want to ingest? (Y/N): ')

# If the user wants to ingest, call the ingest function
if r == 'Y':
    ingest_response = ingest(openai_api_key=openai_api_key, pinecone_api_key=pinecone_api_key,
                             pinecone_environment=pinecone_environment, pinecone_index=pinecone_index,
                             pinecone_namespace=pinecone_namespace, use_pinecone=use_pinecone)
    print(ingest_response)

# If the user doesn't want to ingest, check whether to use Pinecone or Chroma
elif r == 'N':
    if use_pinecone:
        print('Using already ingested namespace at Pinecone.')
    else:
        print('Using already ingested vectors at ./vectorstore.')

# If no method provided, skip
else:
    print('No method given, passing')
    pass

# Call the query function and set up a chat loop
process = query(openai_api_key=openai_api_key, pinecone_api_key=pinecone_api_key,
                pinecone_environment=pinecone_environment, pinecone_index=pinecone_index,
                pinecone_namespace=pinecone_namespace, temperature=temperature, sources=source_amount, use_pinecone=use_pinecone)

def chat_loop():
    # Set up chat history list
    chat_history = []
    while True:
        # Ask for user input
        query = input("Please enter your question (or type 'exit' to end): ")

        # If user wants to exit, break out of the loop
        if query.lower() == 'exit':
            break

        # Get the response from the query function
        result = process({"question": query, "chat_history": chat_history})
        source_documents = result['source_documents']

        # Parse the source documents for display
        parsed_documents = []
        for doc in source_documents:
            parsed_doc = {
                "page_content": doc.page_content,
                "metadata": {
                    "author": doc.metadata.get("author", ""),
                    "creationDate": doc.metadata.get("creationDate", ""),
                    "creator": doc.metadata.get("creator", ""),
                    "file_path": doc.metadata.get("file_path", ""),
                    "format": doc.metadata.get("format", ""),
                    "keywords": doc.metadata.get("keywords", ""),
                    "modDate": doc.metadata.get("modDate", ""),
                    "page_number": doc.metadata.get("page_number", 0),
                    "producer": doc.metadata.get("producer", ""),
                    "source": doc.metadata.get("source", ""),
                    "subject": doc.metadata.get("subject", ""),
                    "title": doc.metadata.get("title", ""),
                    "total_pages": doc.metadata.get("total_pages", 0),
                    "trapped": doc.metadata.get("trapped", "")
                }
            }
            parsed_documents.append(parsed_doc)

        # Print the AI's answer
        print(f'{Fore.BLUE}{Style.BRIGHT}AI:{Fore.RESET}{Style.NORMAL} {result["answer"]}')

        # Append the user input and AI's answer to the chat history
        chat_history.append((query, result["answer"]))

        # Print the answer citations
        print(f'\n{Fore.RED}Answer Citations')
        for doc in parsed_documents:
            print(f"{Fore.GREEN}{Style.BRIGHT}Source:{Fore.RESET}",
                  doc["metadata"]["source"])
            print(f"{Fore.MAGENTA}Page Number:{Fore.RESET}",
                  doc["metadata"]["page_number"], f"{Style.NORMAL}")

        # Write chat history to a JSON file
        with open('chat_history.json', 'w') as json_file:
            json.dump(chat_history, json_file, ensure_ascii=False, indent=4)

# Call the chat_loop function
chat_loop()