import json
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class State(TypedDict):
    """Represents the state structure containing a list of messages.

    Attributes:
        messages (list): A list of messages, where each message can be processed
        by adding messages using the `add_messages` function.
    """
    messages: Annotated[list, add_messages]

class BasicToolNode:
    """
    Node for executing tools requested in the last AIMessage.

    This class maps tool names to callable tool objects and handles both the
    legacy and modern tool call formats. It processes the tool calls and returns
    structured responses to be used in the LangGraph flow.
    """
    def __init__(self, tools: list) -> None:
        """
        Initialize the BasicToolNode with a list of tool objects.

        Args:
            tools (list): A list of tools, each having a `.name` attribute and an `.invoke()` method.
        """
        # For StructuredTool objects, use .name attribute
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        """
        Execute the tools based on the tool calls in the last message.

        Args:
            inputs (dict): Dictionary containing a 'messages' list, where the last message may have tool calls.

        Returns:
            dict: A dictionary with a single key 'messages' containing a list of tool response messages.
        """
        messages = inputs.get("messages", [])
        message = messages[-1]
        outputs = []
                
        for tool_call in message.tool_calls:
                        
            # Handle both dictionary and object formats
            if isinstance(tool_call, dict):
                # Check if it's the new format (name/args directly) or old format (function nested)
                if "function" in tool_call:
                    # Old format: {'function': {'name': '...', 'arguments': '...'}, 'id': '...'}
                    tool_name = tool_call["function"]["name"]
                    tool_args = json.loads(tool_call["function"]["arguments"])
                    tool_call_id = tool_call["id"]
                else:
                    # New format: {'name': '...', 'args': {...}, 'id': '...'}
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]  # Already a dict, no need to json.loads
                    tool_call_id = tool_call["id"]
            else:
                # Object format (original Fireworks object)
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_call_id = tool_call.id
            
            # Get the tool and invoke it
            if tool_name in self.tools_by_name:
                tool = self.tools_by_name[tool_name]
                result = tool.invoke(tool_args)
            else:
                result = f"Unknown tool: {tool_name}"
            
            outputs.append({
                "role": "tool",
                "content": json.dumps(result),
                "name": tool_name,
                "tool_call_id": tool_call_id,
            })
        return {"messages": outputs}


def route_tools(
    state: State,
) -> Literal["tools", "__end__"]:
    """

    Determines whether to route to the ToolNode or end the flow.

    This function is used in the conditional_edge and checks the last message in the state for tool calls. If tool
    calls exist, it routes to the 'tools' node; otherwise, it routes to the end.

    Args:
        state (State): The input state containing a list of messages.

    Returns:
        Literal["tools", "__end__"]: Returns 'tools' if there are tool calls;
        '__end__' otherwise.

    Raises:
        ValueError: If no messages are found in the input state.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(
            f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"
