from langchain_core.tools import tool
import chromadb
import spacy
from agent_graph.load_tools_config import LoadToolsConfig

TOOLS_CFG = LoadToolsConfig()


class StoriesRAGTool:
    """
    A tool for retrieving relevant fictional stories using a Retrieval-Augmented Generation (RAG) approach.

    This tool uses a spaCy embedding model to convert a query into a vector representation, then performs
    similarity search on a Chroma vector database to find the top-k matching stories.

    Attributes:
        embedding_model (str): Name of the spaCy model used for generating embeddings.
        vectordb_dir (str): Path to the Chroma vector database directory.
        k (int): Number of nearest results to retrieve.
        client (chromadb.PersistentClient): Persistent Chroma client instance.
        collection (chromadb.Collection): Chroma collection used for similarity search.
        nlp (spacy.Language): Loaded spaCy language model for embedding generation.
    """

    def __init__(self, embedding_model: str, vectordb_dir: str, k: int, collection_name: str) -> None:
        """
        Initialize the StoriesRAGTool with embedding model, Chroma DB directory, and search parameters.

        Args:
            embedding_model (str): Name of the spaCy model to use (e.g., "en_core_web_md").
            vectordb_dir (str): Directory path where Chroma DB is stored.
            k (int): Number of top similar documents to retrieve.
            collection_name (str): Name of the collection inside Chroma DB to query from.
        """
        self.embedding_model = embedding_model
        self.vectordb_dir = vectordb_dir
        self.k = k
        self.client = chromadb.PersistentClient(path=self.vectordb_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.nlp = spacy.load(self.embedding_model)
        print("Number of vectors in vectordb:", self.collection.count(), "\n\n")


@tool
def lookup_stories(query: str) -> str:
    # """Search among the fictional stories and find the answer to the query. Input should be the query."""
    """
    Perform a semantic search over fictional stories and return top-k matching results.

    Args:
        query (str): Natural language query to search within the vectorized stories.

    Returns:
        str: Concatenated results of the top matching story documents.
    """
    rag_tool = StoriesRAGTool(
        embedding_model=TOOLS_CFG.stories_rag_embedding_model,
        vectordb_dir=TOOLS_CFG.stories_rag_vectordb_directory,
        k=TOOLS_CFG.stories_rag_k,
        collection_name=TOOLS_CFG.stories_rag_collection_name)
    query_embedding = rag_tool.nlp(query).vector

    results = rag_tool.collection.query(
        query_embeddings=[query_embedding],
        n_results=rag_tool.k,
        include=["documents", "metadatas"]
    )
    return "\n\n".join(results["documents"][0])
