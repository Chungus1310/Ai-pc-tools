tools = [
    {
        "name": "set_timer",
        "description": "Set a timer for a specified duration.",
        "parameters": {
            "type": "object",
            "properties": {
                "duration": {"type": "string", "description": "Duration in format: '1h30m', '45m', '90s'"},
                "message": {"type": "string", "description": "Optional message to show when timer completes"}
            },
            "required": ["duration"]
        }
    },
    {
        "name": "set_alarm",
        "description": "Set an alarm for a specific time.",
        "parameters": {
            "type": "object",
            "properties": {
                "alarm_time": {"type": "string", "description": "Time in 24-hour format (HH:MM)"},
                "message": {"type": "string", "description": "Optional message to show when alarm triggers"}
            },
            "required": ["alarm_time"]
        }
    },
    {
        "name": "set_reminder",
        "description": "Set a reminder for a specific time or after duration.",
        "parameters": {
            "type": "object",
            "properties": {
                "remind_time": {"type": "string", "description": "Time (HH:MM) or duration (1h30m)"},
                "message": {"type": "string", "description": "Reminder message"}
            },
            "required": ["remind_time", "message"]
        }
    },
    {
        "name": "set_recurring_reminder",
        "description": "Set a recurring reminder.",
        "parameters": {
            "type": "object",
            "properties": {
                "schedule_time": {"type": "string", "description": "Time in 24-hour format (HH:MM)"},
                "message": {"type": "string", "description": "Reminder message"},
                "frequency": {"type": "string", "enum": ["daily", "hourly", "weekly", "workdays"]}
            },
            "required": ["schedule_time", "message"]
        }
    },
    {
        "name": "set_pomodoro_timer",
        "description": "Set up a Pomodoro timer for focused work sessions.",
        "parameters": {
            "type": "object",
            "properties": {
                "work_duration": {"type": "string", "description": "Work period duration (default: 25m)"},
                "break_duration": {"type": "string", "description": "Break period duration (default: 5m)"},
                "cycles": {"type": "integer", "description": "Number of work/break cycles (default: 4)"}
            }
        }
    },
    {
        "name": "countdown_timer",
        "description": "Create a countdown timer with visual feedback.",
        "parameters": {
            "type": "object",
            "properties": {
                "duration": {"type": "string", "description": "Countdown duration (e.g., '5m', '1h30m')"},
                "title": {"type": "string", "description": "Optional timer title"}
            },
            "required": ["duration"]
        }
    },
    {
        "name": "create_file",
        "description": "Create a file at a specified path.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "The full path of the file to create."},
                "content": {"type": "string", "description": "Optional content to write to the file."}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "create_folder",
        "description": "Create a new folder at specified path.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "The path where the folder should be created."}
            },
            "required": ["folder_path"]
        }
    },
    {
        "name": "move_file",
        "description": "Move a file from one location to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source file path"},
                "destination": {"type": "string", "description": "Destination path"}
            },
            "required": ["source", "destination"]
        }
    },
    {
        "name": "copy_file",
        "description": "Copy a file from one location to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Source file path"},
                "destination": {"type": "string", "description": "Destination path"}
            },
            "required": ["source", "destination"]
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file at specified path.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path of the file to delete"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "rename_file",
        "description": "Rename a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "old_path": {"type": "string", "description": "Current file path"},
                "new_name": {"type": "string", "description": "New name for the file"}
            },
            "required": ["old_path", "new_name"]
        }
    },
    {
        "name": "compress_files",
        "description": "Compress files into a zip archive.",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {"type": "array", "items": {"type": "string"}, "description": "List of file paths to compress"},
                "output_path": {"type": "string", "description": "Output zip file path"}
            },
            "required": ["files", "output_path"]
        }
    },
    {
        "name": "extract_archive",
        "description": "Extract a zip archive.",
        "parameters": {
            "type": "object",
            "properties": {
                "archive_path": {"type": "string", "description": "Path to the archive file"},
                "extract_path": {"type": "string", "description": "Extraction destination path"}
            },
            "required": ["archive_path", "extract_path"]
        }
    },
    {
        "name": "search_files",
        "description": "Search for files matching a pattern.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory to search in"},
                "pattern": {"type": "string", "description": "Search pattern (e.g., *.txt)"},
                "recursive": {"type": "boolean", "description": "Search in subdirectories"}
            },
            "required": ["directory", "pattern"]
        }
    },
    {
        "name": "launch_application",
        "description": "Launch a Windows application.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_path": {"type": "string", "description": "Path to the application"},
                "arguments": {"type": "string", "description": "Command line arguments"}
            },
            "required": ["app_path"]
        }
    },
    {
        "name": "take_screenshot",
        "description": "Capture screen screenshot.",
        "parameters": {
            "type": "object",
            "properties": {
                "output_path": {"type": "string", "description": "Path to save screenshot"},
                "region": {"type": "object", "description": "Optional region to capture"}
            },
            "required": ["output_path"]
        }
    },
    {
        "name": "schedule_task",
        "description": "Schedule a Windows task.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_name": {"type": "string", "description": "Name of the task"},
                "command": {"type": "string", "description": "Command to execute"},
                "schedule": {"type": "string", "description": "Schedule timing (e.g., daily, weekly)"},
                "time": {"type": "string", "description": "Time to execute"}
            },
            "required": ["task_name", "command", "schedule"]
        }
    },
    {
        "name": "system_control",
        "description": "Control system operations.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["shutdown", "restart", "sleep", "hibernate"], "description": "System control action"},
                "delay": {"type": "integer", "description": "Delay in seconds before action"}
            },
            "required": ["action"]
        }
    },
    {
        "name": "volume_control",
        "description": "Control system volume.",
        "parameters": {
            "type": "object",
            "properties": {
                "level": {"type": "integer", "description": "Volume level (0-100)"},
                "mute": {"type": "boolean", "description": "Mute/unmute"}
            },
            "required": ["level"]
        }
    },
    {
        "name": "send_email",
        "description": "Send an email with optional attachment.",
        "parameters": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "attachment_path": {"type": "string"}
            },
            "required": ["recipient", "subject", "body"]
        }
    },
    {
        "name": "read_emails",
        "description": "Read emails from the inbox.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "add_event",
        "description": "Add an event to the calendar.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "start_time": {"type": "string"},
                "end_time": {"type": "string"}
            },
            "required": ["summary", "start_time", "end_time"]
        }
    },
    {
        "name": "voice_command",
        "description": "Execute voice commands.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "web_search",
        "description": "Perform a web search.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    },
]