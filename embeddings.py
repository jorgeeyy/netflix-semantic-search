import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import dotenv_loader
import os

dotenv_loader.load_env()

client = chromadb.PersistentClient(path=r"C:\Users\jorgeeyy\Documents\projects\ai-engineer-devs-track\chroma_db")
collection = client.get_or_create_collection(
    name="my_collection", 
    embedding_function=OpenAIEmbeddingFunction(
        model_name="text-embedding-3-small",
        api_key=os.environ.get("OPENAI_API_KEY"),))