from langchain_core.tools import tool
import chromadb
import spacy
from agent_graph.load_tools_config import LoadToolsConfig

TOOLS_CFG = LoadToolsConfig()


class SwissAirlinePolicyRAGTool:
    """
    A RAG-based tool for retrieving relevant Swiss Airline policy documents using vector embeddings.

    This tool uses a spaCy embedding model to convert natural language queries into vector form,
    and then queries a Chroma vector database to fetch top-k similar policy documents.

    Attributes:
        embedding_model (str): Name of the spaCy model used for embeddings.
        vectordb_dir (str): Path to the persisted Chroma vector database.
        k (int): Number of nearest documents to retrieve.
        client (chromadb.PersistentClient): Client instance for Chroma DB.
        collection (chromadb.Collection): Chroma collection used for querying documents.
        nlp (spacy.Language): Loaded spaCy model for generating embeddings.
    """

    def __init__(self, embedding_model: str, vectordb_dir: str, k: int, collection_name: str) -> None:
        """
        Initialize the SwissAirlinePolicyRAGTool with required configuration.

        Args:
            embedding_model (str): Name of the spaCy model (e.g., "en_core_web_md").
            vectordb_dir (str): Directory where Chroma DB is stored.
            k (int): Number of top results to retrieve from the collection.
            collection_name (str): Name of the Chroma collection containing Swiss Airline policy documents.
        """
        self.embedding_model = embedding_model
        self.vectordb_dir = vectordb_dir
        self.k = k
        self.client = chromadb.PersistentClient(path=self.vectordb_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.nlp = spacy.load(self.embedding_model)
        print("Number of vectors in vectordb:", self.collection.count(), "\n\n")


@tool
def lookup_swiss_airline_policy(query: str) -> str:
    # """Consult the company policies to check whether certain options are permitted."""
    """
    Query Swiss Airline policies using natural language and return the most relevant documents.

    Args:
        query (str): User's question about airline policies.

    Returns:
        str: Combined string of top matching policy documents.
    """
    rag_tool = SwissAirlinePolicyRAGTool(
        embedding_model=TOOLS_CFG.policy_rag_embedding_model,
        vectordb_dir=TOOLS_CFG.policy_rag_vectordb_directory,
        k=TOOLS_CFG.policy_rag_k,
        collection_name=TOOLS_CFG.policy_rag_collection_name)
    query_embedding = rag_tool.nlp(query).vector

    results = rag_tool.collection.query(
        query_embeddings=[query_embedding],
        n_results=rag_tool.k,
        include=["documents", "metadatas"]
    )
    return "\n\n".join(results["documents"][0])
