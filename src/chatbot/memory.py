import os
import pandas as pd
from typing import List
from datetime import datetime, date


class Memory:
    """
    A utility class for saving chatbot conversation history to daily CSV files.

    Methods:
        write_chat_history_to_file(streamlit_chatbot: List, thread_id: str, folder_path: str) -> None:
            Saves the latest user-bot interaction to a CSV file with timestamp and thread ID.
    """
    @staticmethod
    def write_chat_history_to_file(streamlit_chatbot: List,  thread_id: str, folder_path: str) -> None:
        """
        Writes the most recent chatbot interaction (user query and bot response) to a dated CSV log file.
        Each record includes the thread ID and timestamp. The log file is stored in the given folder
        and is named using the current date (YYYY-MM-DD.csv).

        Args:
            streamlit_chatbot (List): List of tuples representing the conversation history.
                                      Each tuple is (user_query, bot_response).
            thread_id (str): Unique ID identifying the current chat session.
            folder_path (str): Path to the directory where log files should be stored.

        CSV Format:
            - Filename: 'YYYY-MM-DD.csv'
            - Columns: 'thread_id', 'timestamp', 'user_query', 'response'
            - Appends to existing file if present, or creates a new one.
        """
        tmp_list = list(streamlit_chatbot[-1])  # Convert the tuple to a list

        today_str = date.today().strftime('%Y-%m-%d')
        tmp_list.insert(0, thread_id)  # Add the new value to the list

        current_time_str = datetime.now().strftime('%H:%M:%S')
        tmp_list.insert(1, current_time_str)  # Add the new value to the list

        # File path for today's CSV file
        file_path = os.path.join(folder_path, f'{today_str}.csv')

        # Create a DataFrame from the list
        new_df = pd.DataFrame([tmp_list], columns=[
                              "thread_id", "timestamp", "user_query", "response"])

        # Check if the file for today exists
        if os.path.exists(file_path):
            # If it exists, append the new data to the CSV file
            new_df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            # If it doesn't exist, create the CSV file with the new data
            new_df.to_csv(file_path, mode='w', header=True, index=False)
