
import os
import yaml
from dotenv import load_dotenv
from pyprojroot import here

load_dotenv()

with open(here("configs/project_config.yml")) as cfg:
    app_config = yaml.load(cfg, Loader=yaml.FullLoader)


class LoadProjectConfig:
    """
    Loads and sets project-level configurations including LangSmith settings and memory directory path.

    This class is responsible for:
    - Setting LangChain environment variables (API key, tracing flag, project name)
    - Loading the path to the directory where conversation memory will be stored

    Attributes:
        memory_dir (str): The resolved path to the local directory where chatbot memory (chat logs) will be saved.
    """

    def __init__(self) -> None:
        """
        Initializes the project configuration loader.

        This sets environment variables required for LangSmith and retrieves the memory
        directory path from the YAML configuration file.
        """
        # Load LangSmith environment variables
        os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
        os.environ["LANGCHAIN_TRACING_V2"] = app_config["langsmith"]["tracing"]
        os.environ["LANGCHAIN_PROJECT"] = app_config["langsmith"]["project_name"]

        # Load memory directory config
        self.memory_dir = here(app_config["memory"]["directory"])
