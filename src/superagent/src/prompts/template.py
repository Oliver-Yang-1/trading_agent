import os
import re
import json
import copy
from datetime import datetime
from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate
from langgraph.prebuilt.chat_agent_executor import AgentState


def get_prompt_template(prompt_name: str) -> str:
    template = open(os.path.join(os.path.dirname(__file__), f"{prompt_name}.md")).read()
    # Escape curly braces using backslash
    template = template.replace("{", "{{").replace("}", "}}")
    # Replace `<<VAR>>` with `{VAR}`
    template = re.sub(r"<<([^>>]+)>>", r"{\1}", template)
    return template


def compress_large_arrays(obj: Any, max_array_size: int = 20, keep_elements: int = 5) -> Any:
    """
    Recursively compress large arrays in an object to reduce context size.
    
    Args:
        obj: The object to compress (can be dict, list, string, etc.)
        max_array_size: Maximum array size before compression (default: 20)
        keep_elements: Number of elements to keep from the beginning of large arrays (default: 5)
    
    Returns:
        Compressed object with large arrays truncated
    """
    if isinstance(obj, dict):
        # Recursively process dictionary values
        return {key: compress_large_arrays(value, max_array_size, keep_elements) for key, value in obj.items()}
    elif isinstance(obj, list):
        # If list is too large, keep only first `keep_elements` and add a note
        if len(obj) > max_array_size:
            compressed_list = obj[:keep_elements]
            # Add a note about compression
            compressed_list.append(f"... (compressed: showing {keep_elements} of {len(obj)} total elements)")
            return compressed_list
        else:
            # Recursively process list elements
            return [compress_large_arrays(item, max_array_size, keep_elements) for item in obj]
    elif isinstance(obj, str):
        # Try to parse as JSON and compress if it's a valid JSON string containing arrays
        try:
            parsed = json.loads(obj)
            compressed = compress_large_arrays(parsed, max_array_size, keep_elements)
            return json.dumps(compressed, ensure_ascii=False)
        except (json.JSONDecodeError, TypeError):
            # Not a JSON string, return as is
            return obj
    else:
        # For other types (int, float, bool, None), return as is
        return obj


def compress_messages(messages: List[Any], max_array_size: int = 20, keep_elements: int = 5) -> List[Any]:
    """
    Compress large arrays in message content to reduce context size.
    
    Args:
        messages: List of message objects (HumanMessage, ToolMessage, etc.)
        max_array_size: Maximum array size before compression
        keep_elements: Number of elements to keep from large arrays
    
    Returns:
        List of messages with compressed content
    """
    compressed_messages = []
    
    for message in messages:
        # Deep copy the message to avoid modifying the original
        compressed_message = copy.deepcopy(message)
        
        # Check if this is a ToolMessage and compress its content
        if hasattr(compressed_message, '__class__') and 'ToolMessage' in str(compressed_message.__class__):
            if hasattr(compressed_message, 'content') and compressed_message.content:
                compressed_message.content = compress_large_arrays(
                    compressed_message.content, 
                    max_array_size, 
                    keep_elements
                )
        # Also handle dictionary-style messages for backward compatibility
        elif isinstance(compressed_message, dict) and 'content' in compressed_message:
            compressed_message['content'] = compress_large_arrays(
                compressed_message['content'], 
                max_array_size, 
                keep_elements
            )
        # Handle any message object with content attribute
        elif hasattr(compressed_message, 'content') and compressed_message.content:
            compressed_message.content = compress_large_arrays(
                compressed_message.content, 
                max_array_size, 
                keep_elements
            )
        
        compressed_messages.append(compressed_message)
    
    return compressed_messages


def apply_prompt_template(prompt_name: str, state: AgentState) -> list:
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template(prompt_name),
    ).format(CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"), **state)
    return [{"role": "system", "content": system_prompt}] + state["messages"]


def apply_prompt_template_compressed(prompt_name: str, state: AgentState, max_array_size: int = 20, keep_elements: int = 5) -> list:
    """
    Apply prompt template with message compression to handle large context scenarios.
    
    This function is designed to handle cases where messages contain large arrays that might
    exceed LLM context limits. Instead of simple message truncation, it intelligently
    compresses large arrays within message content.
    
    Args:
        prompt_name: Name of the prompt template to use
        state: Agent state containing messages and other data
        max_array_size: Maximum array size before compression (default: 100)
        keep_elements: Number of elements to keep from large arrays (default: 5)
    
    Returns:
        List of messages with system prompt and compressed user messages
    """
    # Create system prompt same as original function
    system_prompt = PromptTemplate(
        input_variables=["CURRENT_TIME"],
        template=get_prompt_template(prompt_name),
    ).format(CURRENT_TIME=datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"), **state)
    
    # Compress messages to handle large arrays
    compressed_messages = compress_messages(state["messages"], max_array_size, keep_elements)
    
    return [{"role": "system", "content": system_prompt}] + compressed_messages
