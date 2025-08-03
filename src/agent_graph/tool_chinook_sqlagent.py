from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain.chains.openai_tools import create_extraction_chain_pydantic
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
from langchain_core.tools import tool
from agent_graph.load_tools_config import LoadToolsConfig
from .extract_sql_query import extract_sql_query

TOOLS_CFG = LoadToolsConfig()


class Table(BaseModel):
    """
    Pydantic model representing a semantic category that maps to one or more SQL tables.

    Attributes:
        name (str): Category name, such as "Music" or "Business".
    """
    name: str = Field(description="Name of table in SQL database.")


def get_tables(categories: List[Table]) -> List[str]:
    """
    Map high-level category names to their corresponding SQL table names.

    Args:
        categories (List[Table]): A list of `Table` objects containing category names.

    Returns:
        List[str]: List of SQL table names relevant to the provided categories.
    """
    tables = []
    for category in categories:
        if category.name == "Music":
            tables.extend(
                [
                    "Album",
                    "Artist",
                    "Genre",
                    "MediaType",
                    "Playlist",
                    "PlaylistTrack",
                    "Track",
                ]
            )
        elif category.name == "Business":
            tables.extend(
                ["Customer", "Employee", "Invoice", "InvoiceLine"])
    return tables


class ChinookSQLAgent:
    """
    SQL agent for interacting with the Chinook database using LLM-generated queries.

    This agent uses a language model to:
    - Identify relevant SQL tables based on the question.
    - Construct a SQL query targeting only those tables.
    - Clean and return the final SQL query string.

    Attributes:
        sql_agent_llm (ChatGoogleGenerativeAI): Configured LLM for query understanding and generation.
        db (SQLDatabase): SQL database connection for the Chinook DB.
        full_chain (Runnable): Execution pipeline for table extraction, query generation, and cleanup.
    """
    
    def __init__(self, sqldb_directory: str, llm: str, llm_temerature: float, llm_api_key: str) -> None:
        """
        Initialize the ChinookSQLAgent with database path and LLM configuration.

        Args:
            sqldb_directory (str): Path to the Chinook SQLite database.
            llm (str): Name of the LLM model (e.g., "gemini-2.5-flash").
            llm_temerature (float): Temperature for LLM response variability.
            llm_api_key (str): API key for the LLM service provider.
        """
        self.sql_agent_llm = ChatGoogleGenerativeAI(
            model=llm,
            temperature=llm_temerature,
            google_api_key=llm_api_key
        )
        self.db = SQLDatabase.from_uri(f"sqlite:///{sqldb_directory}")
        print(self.db.get_usable_table_names())
        category_chain_system = """Return the names of the SQL tables that are relevant to the user question. \
        The tables are:

        Music
        Business"""
        category_chain = create_extraction_chain_pydantic(
            Table, self.sql_agent_llm, system_message=category_chain_system)
        table_chain = category_chain | get_tables  # noqa
        query_chain = create_sql_query_chain(self.sql_agent_llm, self.db)
        clean_query_output = RunnableLambda(extract_sql_query)
        # Convert "question" key to the "input" key expected by current table_chain.
        table_chain = {"input": itemgetter("question")} | table_chain
        # Set table_names_to_use using table_chain.
        self.full_chain = RunnablePassthrough.assign(
            table_names_to_use=table_chain) | query_chain | clean_query_output


@tool
def query_chinook_sqldb(query: str) -> str:
    # """Query the Chinook SQL Database. Input should be a search query."""
    """
    Query the Chinook SQL database using natural language.

    Args:
        query (str): User's natural language question.

    Returns:
        str: Query result after LLM-driven SQL generation and execution.
    """
    # Create an instance of ChinookSQLAgent
    agent = ChinookSQLAgent(
        sqldb_directory=TOOLS_CFG.chinook_sqldb_directory,
        llm=TOOLS_CFG.chinook_sqlagent_llm,
        llm_temerature=TOOLS_CFG.chinook_sqlagent_llm_temperature,
        llm_api_key=TOOLS_CFG.chinook_sqlagent_llm_api_key
    )

    query = agent.full_chain.invoke({"question": query})

    return agent.db.run(query)
