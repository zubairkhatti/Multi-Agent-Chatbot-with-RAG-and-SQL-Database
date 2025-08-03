from langchain_core.tools import tool
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
from .extract_sql_query import extract_sql_query
from agent_graph.load_tools_config import LoadToolsConfig

TOOLS_CFG = LoadToolsConfig()


class TravelSQLAgentTool:   
    """
    A LangChain-based tool for querying a travel-related SQL database using natural language.

    This agent uses a language model to convert user questions into SQL queries, executes those queries 
    against a SQLite database, and generates human-readable responses based on query results.

    Attributes:
        sql_agent_llm (ChatGoogleGenerativeAI): The LLM used for query generation and answering.
        system_role (str): Prompt template to guide the model in formatting final answers.
        db (SQLDatabase): SQLite database instance.
        chain (Runnable): LangChain pipeline that generates SQL, runs the query, and returns an answer.

    Methods:
        __init__: Initializes the TravelSQLAgentTool by setting up the language model, SQL database, and query-answering pipeline.
    """

    def __init__(self, llm: str, sqldb_directory: str, llm_temerature: float, llm_api_key: str) -> None:
        """
        Initialize the TravelSQLAgentTool with model and database configurations.

        Args:
            llm (str): Name of the language model to use (e.g., 'gemini-2.5-flash').
            sqldb_directory (str): Path to the SQLite database file.
            llm_temerature (float): Temperature setting for the model (controls randomness).
            llm_api_key (str): API key for the language model provider.
        """
        self.sql_agent_llm = ChatGoogleGenerativeAI(
            model=llm,
            temperature=llm_temerature,
            google_api_key=llm_api_key
        )
        self.system_role = """Given the following user question, corresponding SQL query, and SQL result, answer the user question.\n
            Question: {question}\n
            SQL Query: {query}\n
            SQL Result: {result}\n
            Answer:
            """
        self.db = SQLDatabase.from_uri(
            f"sqlite:///{sqldb_directory}")
        print(self.db.get_usable_table_names())

        execute_query = QuerySQLDataBaseTool(db=self.db)
        write_query = create_sql_query_chain(
            self.sql_agent_llm, self.db)
        clean_query_output = RunnableLambda(extract_sql_query)
        answer_prompt = PromptTemplate.from_template(
            self.system_role)

        answer = answer_prompt | self.sql_agent_llm | StrOutputParser()
        self.chain = (
            RunnablePassthrough.assign(raw_query=write_query)
            .assign(query=itemgetter("raw_query") | clean_query_output)
            .assign(result=itemgetter("query") | execute_query)
            | answer
        )


@tool
def query_travel_sqldb(query: str) -> str:
    """Query the Swiss Airline SQL Database and access all the company's information. Input should be a search query."""
    agent = TravelSQLAgentTool(
        llm=TOOLS_CFG.travel_sqlagent_llm,
        sqldb_directory=TOOLS_CFG.travel_sqldb_directory,
        llm_temerature=TOOLS_CFG.travel_sqlagent_llm_temperature,
        llm_api_key=TOOLS_CFG.travel_sqlagent_api_key
    )
    response = agent.chain.invoke({"question": query})
    return response
