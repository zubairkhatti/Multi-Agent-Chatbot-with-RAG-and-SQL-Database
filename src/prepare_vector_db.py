import chromadb
import spacy
import os
import yaml
from pyprojroot import here
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv


class PrepareVectorDB:
    """
    A class to prepare and manage a Vector Database (VectorDB) using documents from a specified directory.
    The class performs the following tasks:
    - Loads and splits documents (PDFs).
    - Splits the text into chunks based on the specified chunk size and overlap.
    - Embeds the document chunks using a specified embedding model.
    - Stores the embedded vectors in a persistent VectorDB directory.

    Attributes:
        doc_dir (str): Path to the directory containing documents (PDFs) to be processed.
        chunk_size (int): The maximum size of each chunk (in characters) into which the document text will be split.
        chunk_overlap (int): The number of overlapping characters between consecutive chunks.
        embedding_model (str): The name of the embedding model to be used for generating vector representations of text.
        vectordb_dir (str): Directory where the resulting vector database will be stored.
        collection_name (str): The name of the collection to be used within the vector database.

    Methods:
        path_maker(file_name: str, doc_dir: str) -> str:
            Creates a full file path by joining the given directory and file name.

        run() -> None:
            Executes the process of reading documents, splitting text, embedding them into vectors, and 
            saving the resulting vector database. If the vector database directory already exists, it skips
            the creation process.
    """

    def __init__(self,
                 doc_dir: str,
                 chunk_size: int,
                 chunk_overlap: int,
                 vectordb_dir: str,
                 collection_name: str
                 ) -> None:
        """
        Initializes the PrepareVectorDB class with directory paths and chunking parameters.

        Args:
            doc_dir (str): Directory containing the input PDF documents.
            chunk_size (int): Max characters in each chunk.
            chunk_overlap (int): Number of overlapping characters between chunks.
            vectordb_dir (str): Output directory for storing vector DB.
            collection_name (str): Collection name used in Chroma DB.
        """
        self.doc_dir = doc_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.vectordb_dir = vectordb_dir
        self.collection_name = collection_name

    def path_maker(self, file_name: str, doc_dir):
        """
        Creates a full file path by joining the provided directory and file name.

        Args:
            file_name (str): Name of the file.
            doc_dir (str): Path of the directory.

        Returns:
            str: Full path of the file.
        """
        return os.path.join(here(doc_dir), file_name)

    def run(self):
        """
        Executes the main logic to create and store document embeddings in a VectorDB.

        If the vector database directory doesn't exist:
        - It loads PDF documents from the `doc_dir`, splits them into chunks,
        - Embeds the document chunks using the specified embedding model,
        - Stores the embeddings in a persistent VectorDB directory.

        If the directory already exists, it skips the embedding creation process.

        Prints the creation status and the number of vectors in the vector database.

        Returns:
            None
        """
        if not os.path.exists(here(self.vectordb_dir)):
            # If it doesn't exist, create the directory and create the embeddings
            os.makedirs(here(self.vectordb_dir))
            print(f"Directory '{self.vectordb_dir}' was created.")

            file_list = os.listdir(here(self.doc_dir))
            docs = [PyPDFLoader(self.path_maker(
                fn, self.doc_dir)).load_and_split() for fn in file_list]
            docs_list = [item for sublist in docs for item in sublist]

            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
            )
            doc_splits = text_splitter.split_documents(docs_list)

            # Load spaCy model
            try:
                nlp = spacy.load(os.getenv("EMBEDDING_MODEL_NAME"))
            except OSError:
                raise ValueError("spaCy model not found. Run: python -m spacy download en_core_web_lg")

            # Generate embeddings for each chunk
            texts = [doc.page_content for doc in doc_splits]
            embeddings = [nlp(text).vector for text in texts]
            ids = [str(i) for i in range(len(texts))]

            # Use Chroma native client
            client = chromadb.PersistentClient(path=str(here(self.vectordb_dir)))
            collection = client.get_or_create_collection(name=self.collection_name)
            collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings
            )

            print("VectorDB is created and saved.")
            print("Number of vectors in vectordb:",
                  collection.count(), "\n\n")
        else:
            print(f"Directory '{self.vectordb_dir}' already exists.")


if __name__ == "__main__":
    # Runs vector DB preparation for both Swiss airline policies and stories dataset using configs.
    load_dotenv()
    with open(here("configs/tools_config.yml")) as cfg:
        app_config = yaml.safe_load(cfg)

    # Uncomment the following configs to run for stories document
    chunk_size = app_config["swiss_airline_policy_rag"]["chunk_size"]
    chunk_overlap = app_config["swiss_airline_policy_rag"]["chunk_overlap"]
    vectordb_dir = app_config["swiss_airline_policy_rag"]["vectordb"]
    collection_name = app_config["swiss_airline_policy_rag"]["collection_name"]
    doc_dir = app_config["swiss_airline_policy_rag"]["unstructured_docs"]

    prepare_db_instance = PrepareVectorDB(
        doc_dir=doc_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        vectordb_dir=vectordb_dir,
        collection_name=collection_name)

    prepare_db_instance.run()

    # Uncomment the following configs to run for stories document
    chunk_size = app_config["stories_rag"]["chunk_size"]
    chunk_overlap = app_config["stories_rag"]["chunk_overlap"]
    vectordb_dir = app_config["stories_rag"]["vectordb"]
    collection_name = app_config["stories_rag"]["collection_name"]
    doc_dir = app_config["stories_rag"]["unstructured_docs"]

    prepare_db_instance = PrepareVectorDB(
        doc_dir=doc_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        vectordb_dir=vectordb_dir,
        collection_name=collection_name)

    prepare_db_instance.run()
