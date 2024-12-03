from gui import *
from tools_definition import *
from helpers import *
from tools import *
import json
import re
import logging

def convert_to_xlam_tool(tools):
    if isinstance(tools, dict):
        return {
            "name": tools["name"],
            "description": tools["description"],
            "parameters": {k: v for k, v in tools["parameters"].get("properties", {}).items()}
        }
    elif isinstance(tools, list):
        return [convert_to_xlam_tool(tool) for tool in tools]
    else:
        return tools

def extract_json(response):
    logging.debug(f"Attempting to extract JSON from response: {response}")
    match = re.search(r'```json(.*?)```', response, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            json_obj = json.loads(json_str)
            logging.debug(f"Successfully extracted JSON: {json_obj}")
            return json_obj
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return None
    else:
        logging.warning("No JSON found in response.")
        return None

def validate_json_response(tool_calls_json):
    if isinstance(tool_calls_json, dict):
        tool_calls = tool_calls_json.get("tool_calls", [])
        if isinstance(tool_calls, list):
            for tool in tool_calls:
                if not isinstance(tool, dict):
                    return False
                if "name" not in tool or "arguments" not in tool:
                    return False
            return True
        return False
    return False

def convert_to_seconds(duration_str):
    logging.debug(f"Converting duration {duration_str} to seconds")
    total_seconds = 0
    current_number = ""
    
    for char in duration_str:
        if char.isdigit():
            current_number += char
        elif char.lower() in ['h', 'm', 's']:
            if current_number:
                number = int(current_number)
                if char.lower() == 'h':
                    total_seconds += number * 3600
                elif char.lower() == 'm':
                    total_seconds += number * 60
                elif char.lower() == 's':
                    total_seconds += number
                current_number = ""
    logging.debug(f"Converted duration to {total_seconds} seconds")
    return total_seconds