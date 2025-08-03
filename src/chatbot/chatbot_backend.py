from typing import List, Tuple
from chatbot.load_config import LoadProjectConfig
from agent_graph.load_tools_config import LoadToolsConfig
from agent_graph.build_full_graph import build_graph
from utils.app_utils import create_directory
from chatbot.memory import Memory
import re

PROJECT_CFG = LoadProjectConfig()
TOOLS_CFG = LoadToolsConfig()

graph = build_graph()
config = {"configurable": {"thread_id": TOOLS_CFG.thread_id}}

create_directory("memory")


class ChatBot:
    """
    A class that drives chatbot interactions using a LangGraph agent.

    This chatbot sends user input through a tool-integrated graph agent and
    manages message history, including saving conversations to disk.

    Attributes:
        config (dict): A configuration dictionary containing runtime metadata (e.g., thread ID).

    Methods:
        respond(chatbot: List, message: str) -> List:
            Processes the user input using the LangGraph-based graph and returns
            an updated chatbot history after storing it in memory.
    """
    @staticmethod
    def respond(chatbot: List, message: str) -> List:
        """
        Processes a user message using the agent graph and returns the chatbot history.

        This method:
        1. Sends the message through the graph.
        2. Extracts visible content (removing any <think>...</think> metadata).
        3. Appends the response to the chatbot history.
        4. Writes the updated history to a memory file.

        Args:
            chatbot (List): List of (user_message, bot_response) tuples.
            message (str): The user message to process.

        Returns:
            List: A two-element list: an empty string (for resetting the input field) and the updated chatbot list.
        """
        # The config is the **second positional argument** to stream() or invoke()!
        events = graph.stream(
            {"messages": [{"role": "user", "content": message}]}, config, stream_mode="values"
        )
        for event in events:
            event["messages"][-1].pretty_print()

        # Extract the visible content (remove <think>...</think>)
        full_content = event["messages"][-1].content
        visible_content = re.sub(r"<think>.*?</think>", "", full_content, flags=re.DOTALL).strip()

        chatbot.append((message, visible_content))

        Memory.write_chat_history_to_file(
            streamlit_chatbot=chatbot, folder_path=PROJECT_CFG.memory_dir, thread_id=TOOLS_CFG.thread_id)
        return "", chatbot
