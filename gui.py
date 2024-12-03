import customtkinter
from queue import Queue
from tools_definition import *
from helpers import *
from tools import *
import logging
import threading
import time
from mistralai import Mistral
import json
import speech_recognition as sr

# Initialize logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chun's Probably broken Assistant")
        self.geometry("800x600")
        
        self.task_queue = Queue()
        self.result_queue = Queue()
        self.api_key = None  # To store the user's API key

        # API Key Input Frame
        self.api_key_frame = customtkinter.CTkFrame(self)
        self.api_key_frame.pack(pady=10)
        
        self.api_key_label = customtkinter.CTkLabel(self.api_key_frame, text="Enter Mistral API Key:")
        self.api_key_label.pack(side="left", padx=5)
        
        self.api_key_entry = customtkinter.CTkEntry(self.api_key_frame, width=200)
        self.api_key_entry.pack(side="left", padx=5)
        
        self.api_key_button = customtkinter.CTkButton(self.api_key_frame, text="Submit", command=self.submit_api_key)
        self.api_key_button.pack(side="left", padx=5)
        
        # Input frame
        self.input_frame = customtkinter.CTkFrame(self)
        self.input_frame.pack(pady=20)
        
        self.command_entry = customtkinter.CTkEntry(self.input_frame, placeholder_text="Enter command", width=600)
        self.command_entry.pack(side="left", padx=10)
        
        self.execute_button = customtkinter.CTkButton(self.input_frame, text="Execute", command=self.execute_command)
        self.execute_button.pack(side="left", padx=10)
        
        # Mic button for voice input
        self.mic_button = customtkinter.CTkButton(self.input_frame, text="Mic", command=self.voice_input)
        self.mic_button.pack(side="left", padx=10)
        
        # Output frame
        self.output_frame = customtkinter.CTkFrame(self)
        self.output_frame.pack(pady=20)
        
        self.output_text = customtkinter.CTkTextbox(self.output_frame, width=700, height=300)
        self.output_text.pack(pady=10)
        
        # Start the task handler thread after API key is submitted
        self.mistral_client = None  # To be initialized after API key is provided

    def submit_api_key(self):
        self.api_key = self.api_key_entry.get()
        if self.api_key:
            self.mistral_client = Mistral(api_key=self.api_key)
            self.output_text.insert("end", "API key submitted and Mistral client initialized.\n")
            threading.Thread(target=self.generate_and_execute_tools, daemon=True).start()
            threading.Thread(target=self.update_output, daemon=True).start()
        else:
            self.output_text.insert("end", "API key not provided.\n")
    
    def execute_command(self):
        user_command = self.command_entry.get()
        if not user_command:
            self.output_text.insert("end", "No command entered.\n")
            return
        self.task_queue.put(user_command)
    
    def voice_input(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            self.output_text.insert("end", "Listening...\n")
            audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            self.output_text.insert("end", f"Voice input: {text}\n")
            self.command_entry.delete(0, "end")
            self.command_entry.insert(0, text)
            self.execute_command()
        except sr.UnknownValueError:
            self.output_text.insert("end", "Could not understand audio.\n")
        except sr.RequestError as e:
            self.output_text.insert(f"end", f"Error occurred: {e}\n")
    
    def generate_and_execute_tools(self):
        while True:
            user_command = self.task_queue.get()
            logging.debug(f"User command entered: {user_command}")
            
            # Generate tool calls from Mistral agent
            if self.mistral_client:
                tool_calls_json = self.generate_tool_calls(user_command)
                if tool_calls_json is None:
                    self.result_queue.put("Invalid JSON response from Mistral agent.\n")
                    continue
                
                # Validate JSON response
                if not validate_json_response(tool_calls_json):
                    self.result_queue.put("Invalid JSON response format.\n")
                    continue
                
                # Execute tool calls
                tool_calls = tool_calls_json.get("tool_calls", [])
                results = execute_tool_calls(tool_calls)
                for res in results:
                    if res["success"]:
                        self.result_queue.put(f"Tool {res['tool']} executed successfully.\n")
                    else:
                        error = res.get("error", "Unknown error")
                        self.result_queue.put(f"Tool {res['tool']} failed: {error}\n")
            else:
                self.result_queue.put("API key not provided. Please submit your API key.\n")
    
    def generate_tool_calls(self, user_command):
        # Task and format instructions
        task_instruction = """
        You are an expert in composing functions for a Windows Automation Assistant. Your task is to generate JSON-formatted tool calls based on user commands. The output MUST strictly adhere to the following JSON format, and NO other text MUST be included. If no function call is needed, please make tool_calls an empty list '[]'. and remember that programs are stored at C:\\Program Files
        """.strip()

        format_instruction = """
        The output MUST strictly adhere to the following JSON format, and NO other text MUST be included.
        The example format is as follows. Please make sure the parameter type is correct. If no function call is needed, please make tool_calls an empty list '[]'.
        ```json
        {
            "tool_calls": [
            {"name": "func_name1", "arguments": {"argument1": "value1", "argument2": "value2"}},
            ... (more tool calls as required)
            ]
        }
        ```
        """.strip()

        # Convert tools to xLAM format
        xlam_format_tools = convert_to_xlam_tool(tools)

        # Build the prompt
        prompt = f"""
        [BEGIN OF TASK INSTRUCTION]
        {task_instruction}
        [END OF TASK INSTRUCTION]

        [BEGIN OF AVAILABLE TOOLS]
        {json.dumps(xlam_format_tools)}
        [END OF AVAILABLE TOOLS]

        [BEGIN OF FORMAT INSTRUCTION]
        {format_instruction}
        [END OF FORMAT INSTRUCTION]

        [BEGIN OF QUERY]
        {user_command}
        [END OF QUERY]
        """

        # Generate model response using Mistral agent
        try:
            chat_response = self.mistral_client.agents.complete(
                agent_id="ag:364281a7:20241130:word-agent:9c4d242f",
                messages=[{"role": "user", "content": prompt},],
            )
            response = chat_response.choices[0].message.content
            logging.debug(f"Mistral agent response: {response}")
        except Exception as e:
            logging.error(f"Mistral agent request failed: {e}")
            self.result_queue.put(f"Mistral agent request failed: {e}\n")
            return None

        # Extract JSON from response
        tool_calls_json = extract_json(response)
        return tool_calls_json
    
    def update_output(self):
        while True:
            result = self.result_queue.get()
            self.output_text.insert("end", result)
            self.output_text.see("end")
            time.sleep(0.1)