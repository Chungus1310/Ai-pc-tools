import os
import shutil
import tempfile
import glob
import subprocess
import vlc
import zipfile
from gui import *
from tools_definition import *
from helpers import *
from tools import *
import logging
import time
import threading
import queue
import signal
import sys

# Global thread manager
thread_manager = None

class ThreadManager:
    def __init__(self):
        self.threads = []
        self.stop_event = threading.Event()

    def start_thread(self, target, args=()):
        thread = threading.Thread(target=target, args=args)
        thread.daemon = True  # Set daemon to True to ensure threads die with the main process
        thread.start()
        self.threads.append(thread)
        return thread

    def stop_all_threads(self):
        self.stop_event.set()
        for thread in self.threads:
            thread.join()
        self.threads = []
        self.stop_event.clear()

def setup_thread_manager():
    global thread_manager
    thread_manager = ThreadManager()

def execute_tool_calls(tool_calls):
    logging.debug("Starting tool execution")
    results = []
    for tool in tool_calls:
        tool_name = tool.get("name")
        arguments = tool.get("arguments", {})
        logging.debug(f"Executing tool: {tool_name} with arguments: {arguments}")
        
        try:
            func = globals().get(tool_name)
            if callable(func):
                result = thread_manager.start_thread(func, args=(arguments,))
                results.append({
                    "tool": tool_name,
                    "success": result is not None,
                    "arguments": arguments
                })
            else:
                logging.warning(f"Tool {tool_name} not found.")
                results.append({
                    "tool": tool_name,
                    "success": False,
                    "error": "Tool not found"
                })
        except Exception as e:
            logging.error(f"Error executing tool {tool_name}: {e}")
            results.append({
                "tool": tool_name,
                "success": False,
                "error": str(e)
            })
    return results

def create_file(arguments):
    file_path = arguments.get("file_path")
    content = arguments.get("content", "")
    logging.debug(f"Creating file at {file_path}")
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        logging.debug(f"File created at {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to create file: {e}")
        return False

def create_folder(arguments):
    folder_path = arguments.get("folder_path")
    logging.debug(f"Creating folder at {folder_path}")
    try:
        os.makedirs(folder_path, exist_ok=True)
        logging.debug(f"Folder created at {folder_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to create folder: {e}")
        return False

def move_file(arguments):
    source = arguments.get("source")
    destination = arguments.get("destination")
    logging.debug(f"Moving file from {source} to {destination}")
    try:
        shutil.move(source, destination)
        logging.debug(f"Moved file from {source} to {destination}")
        return True
    except Exception as e:
        logging.error(f"Failed to move file: {e}")
        return False

def copy_file(arguments):
    source = arguments.get("source")
    destination = arguments.get("destination")
    logging.debug(f"Copying file from {source} to {destination}")
    try:
        shutil.copy2(source, destination)
        logging.debug(f"Copied file from {source} to {destination}")
        return True
    except Exception as e:
        logging.error(f"Failed to copy file: {e}")
        return False

def delete_file(arguments):
    file_path = arguments.get("file_path")
    logging.debug(f"Deleting file at {file_path}")
    try:
        os.remove(file_path)
        logging.debug(f"Deleted file: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to delete file: {e}")
        return False

def rename_file(arguments):
    old_path = arguments.get("old_path")
    new_name = arguments.get("new_name")
    logging.debug(f"Renaming file from {old_path} to {new_name}")
    try:
        directory = os.path.dirname(old_path)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        logging.debug(f"Renamed file from {old_path} to {new_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to rename file: {e}")
        return False

def compress_files(arguments):
    files = arguments.get("files")
    output_path = arguments.get("output_path")
    logging.debug(f"Compressing files into {output_path}")
    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                zipf.write(file, os.path.basename(file))
        logging.debug(f"Created zip archive at {output_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to create zip archive: {e}")
        return False

def extract_archive(arguments):
    archive_path = arguments.get("archive_path")
    extract_path = arguments.get("extract_path")
    logging.debug(f"Extracting archive from {archive_path} to {extract_path}")
    try:
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(extract_path)
        logging.debug(f"Extracted archive to {extract_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to extract archive: {e}")
        return False

def search_files(arguments):
    directory = arguments.get("directory")
    pattern = arguments.get("pattern")
    recursive = arguments.get("recursive", True)
    logging.debug(f"Searching for files in {directory} with pattern {pattern}")
    try:
        if recursive:
            search_path = os.path.join(directory, "**", pattern)
            files = glob.glob(search_path, recursive=True)
        else:
            search_path = os.path.join(directory, pattern)
            files = glob.glob(search_path)
        logging.debug(f"Found {len(files)} files matching pattern")
        return files
    except Exception as e:
        logging.error(f"Failed to search files: {e}")
        return []

def launch_application(arguments):
    app_path = arguments.get("app_path")
    arguments = arguments.get("arguments", "")
    logging.debug(f"Launching application at {app_path} with arguments {arguments}")
    
    try:
        # Ensure the application path is correctly formatted and escaped
        app_path = os.path.normpath(app_path)
        if not os.path.exists(app_path):
            logging.error(f"Application path does not exist: {app_path}")
            return False
        
        # Escape the arguments if necessary
        arguments = arguments.replace('"', '\\"')
        
        # Launch the application
        subprocess.Popen([app_path] + (arguments.split() if arguments else []))
        logging.debug(f"Launched application: {app_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to launch application: {e}")
        return False

def take_screenshot(arguments):
    output_path = arguments.get("output_path")
    region = arguments.get("region")
    logging.debug(f"Taking screenshot and saving to {output_path}")
    try:
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        screenshot.save(output_path)
        logging.debug(f"Saved screenshot to {output_path}")
        return True
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        return False

def schedule_task(arguments):
    task_name = arguments.get("task_name")
    command = arguments.get("command")
    schedule = arguments.get("schedule")
    time = arguments.get("time")
    logging.debug(f"Scheduling task {task_name} with command {command} and schedule {schedule}")
    try:
        if time is None:
            time = datetime.now().strftime("%H:%M")
        
        schedule_map = {
            "daily": "/sc DAILY",
            "weekly": "/sc WEEKLY",
            "monthly": "/sc MONTHLY"
        }
        
        schedule_param = schedule_map.get(schedule.lower(), "/sc ONCE")
        cmd = f'schtasks /create /tn "{task_name}" {schedule_param} /tr "{command}" /st {time}'
        subprocess.run(cmd, shell=True, check=True)
        logging.debug(f"Scheduled task: {task_name}")
        return True
    except Exception as e:
        logging.error(f"Failed to schedule task: {e}")
        return False

def system_control(arguments):
    action = arguments.get("action")
    delay = arguments.get("delay", 0)
    logging.debug(f"Executing system control action {action} with delay {delay}")
    try:
        actions = {
            "shutdown": lambda: subprocess.run(f"shutdown /s /t {delay}", shell=True),
            "restart": lambda: subprocess.run(f"shutdown /r /t {delay}", shell=True),
            "sleep": lambda: win32api.SetSuspendState(0, 1, 0),
            "hibernate": lambda: win32api.SetSuspendState(1, 1, 0)
        }
        
        if action in actions:
            actions[action]()
            logging.debug(f"Executed system control: {action}")
            return True
        return False
    except Exception as e:
        logging.error(f"Failed to execute system control: {e}")
        return False

def set_timer(arguments):
    duration = arguments.get("duration")
    message = arguments.get("message", "Timer finished!")
    logging.debug(f"Setting timer for {duration} with message {message}")
    try:
        seconds = convert_to_seconds(duration)
        def timer_thread():
            time.sleep(seconds)
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            notification.notify(
                title="Timer Complete",
                message=message,
                app_icon=None,
                timeout=10,
            )
        thread_manager.start_thread(timer_thread)
        logging.debug(f"Timer set for {duration}")
        return True
    except Exception as e:
        logging.error(f"Failed to set timer: {e}")
        return False

def set_alarm(arguments):
    alarm_time = arguments.get("alarm_time")
    message = arguments.get("message", "Alarm!")
    logging.debug(f"Setting alarm for {alarm_time} with message {message}")
    try:
        def alarm_thread():
            while not thread_manager.stop_event.is_set():
                current_time = datetime.now().strftime("%H:%M")
                if current_time == alarm_time:
                    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
                    notification.notify(
                        title="Alarm",
                        message=message,
                        app_icon=None,
                        timeout=10,
                    )
                    break
                time.sleep(30)
        thread_manager.start_thread(alarm_thread)
        logging.debug(f"Alarm set for {alarm_time}")
        return True
    except Exception as e:
        logging.error(f"Failed to set alarm: {e}")
        return False

def set_reminder(arguments):
    remind_time = arguments.get("remind_time")
    message = arguments.get("message")
    logging.debug(f"Setting reminder for {remind_time} with message {message}")
    try:
        if remind_time.lower().endswith(('h', 'm', 's')):
            seconds = convert_to_seconds(remind_time)
            reminder_time = datetime.now() + timedelta(seconds=seconds)
        else:
            reminder_time = datetime.strptime(remind_time, "%H:%M").time()
        
        def reminder_thread():
            while not thread_manager.stop_event.is_set():
                current_time = datetime.now().time()
                if current_time >= reminder_time:
                    notification.notify(
                        title="Reminder",
                        message=message,
                        app_icon=None,
                        timeout=10,
                    )
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                    break
                time.sleep(30)
        thread_manager.start_thread(reminder_thread)
        logging.debug(f"Reminder set for {remind_time}: {message}")
        return True
    except Exception as e:
        logging.error(f"Failed to set reminder: {e}")
        return False

def set_recurring_reminder(arguments):
    schedule_time = arguments.get("schedule_time")
    message = arguments.get("message")
    frequency = arguments.get("frequency", "daily")
    logging.debug(f"Setting recurring reminder for {schedule_time} with message {message} and frequency {frequency}")
    try:
        def show_reminder():
            notification.notify(
                title="Recurring Reminder",
                message=message,
                app_icon=None,
                timeout=10,
            )
            winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)

        schedule_map = {
            "daily": schedule.every().day.at(schedule_time).do(show_reminder),
            "hourly": schedule.every().hour.at(":00").do(show_reminder),
            "weekly": schedule.every().week.at(schedule_time).do(show_reminder),
            "workdays": schedule.every().monday.to(schedule.every().friday).at(schedule_time).do(show_reminder)
        }

        if frequency in schedule_map:
            def schedule_thread():
                while not thread_manager.stop_event.is_set():
                    schedule.run_pending()
                    time.sleep(30)
            thread_manager.start_thread(schedule_thread)
            logging.debug(f"Recurring reminder set for {frequency} at {schedule_time}")
            return True
        return False
    except Exception as e:
        logging.error(f"Failed to set recurring reminder: {e}")
        return False

def set_pomodoro_timer(arguments):
    work_duration = arguments.get("work_duration", "25m")
    break_duration = arguments.get("break_duration", "5m")
    cycles = arguments.get("cycles", 4)
    logging.debug(f"Setting Pomodoro timer with work duration {work_duration}, break duration {break_duration}, and cycles {cycles}")
    try:
        work_seconds = convert_to_seconds(work_duration)
        break_seconds = convert_to_seconds(break_duration)
        
        def pomodoro_thread():
            for cycle in range(cycles):
                time.sleep(work_seconds)
                notification.notify(
                    title="Pomodoro Timer",
                    message=f"Time for a break! Cycle {cycle + 1}/{cycles} completed",
                    timeout=10
                )
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
                
                if cycle < cycles - 1:
                    time.sleep(break_seconds)
                    notification.notify(
                        title="Pomodoro Timer",
                        message="Break over! Time to work",
                        timeout=10
                    )
                    winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
        
        thread_manager.start_thread(pomodoro_thread)
        logging.debug(f"Pomodoro timer started: {cycles} cycles")
        return True
    except Exception as e:
        logging.error(f"Failed to start Pomodoro timer: {e}")
        return False

def countdown_timer(arguments):
    duration = arguments.get("duration")
    title = arguments.get("title", "Countdown")
    logging.debug(f"Setting countdown timer for {duration} with title {title}")
    try:
        seconds = convert_to_seconds(duration)
        end_time = datetime.now() + timedelta(seconds=seconds)
        
        def countdown_thread():
            while not thread_manager.stop_event.is_set():
                remaining = end_time - datetime.now()
                remaining_str = str(remaining).split('.')[0]
                notification.notify(
                    title=title,
                    message=f"Time remaining: {remaining_str}",
                    timeout=1
                )
                time.sleep(1)
            winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)
            notification.notify(
                title=title,
                message="Countdown Complete!",
                timeout=10
            )
        
        thread_manager.start_thread(countdown_thread)
        logging.debug(f"Countdown timer started for {duration}")
        return True
    except Exception as e:
        logging.error(f"Failed to start countdown timer: {e}")
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

def volume_control(arguments):
    level = arguments.get("level")
    mute = arguments.get("mute")
    logging.debug(f"Setting volume level to {level} and mute to {mute}")
    try:
        pythoncom.CoInitialize()
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        if mute is not None:
            volume.SetMute(mute, None)
        if level is not None:
            volume.SetMasterVolumeLevelScalar(level / 100, None)
        logging.debug(f"Set volume level to {level}")
        return True
    except Exception as e:
        logging.error(f"Failed to control volume: {e}")
        return False

def send_email(arguments):
    recipient = arguments.get("recipient")
    subject = arguments.get("subject")
    body = arguments.get("body")
    attachment_path = arguments.get("attachment_path")
    msg = MIMEMultipart()
    msg['From'] = 'your_email@example.com'
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    if attachment_path:
        attachment = open(attachment_path, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
        msg.attach(part)
    server = smtplib.SMTP('smtp.example.com', 587)
    server.starttls()
    server.login('your_email@example.com', 'your_password')
    text = msg.as_string()
    server.sendmail('your_email@example.com', recipient, text)
    server.quit()
    return True

def read_emails(arguments):
    mail = imaplib.IMAP4_SSL('imap.example.com')
    mail.login('your_email@example.com', 'your_password')
    mail.select('inbox')
    typ, data = mail.search(None, 'ALL')
    for num in data[0].split():
        typ, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        print(f"Subject: {email_message['Subject']}")
        print(f"From: {email_message['From']}")
        print(f"Date: {email_message['Date']}")
    mail.logout()
    return True

def add_event(arguments):
    summary = arguments.get("summary")
    start_time = arguments.get("start_time")
    end_time = arguments.get("end_time")
    creds = Credentials.from_authorized_user_file('credentials.json')
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': summary,
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f'Event created: {event.get("htmlLink")}')
    return True

def voice_command(arguments):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio)
        print(f"You said: {query}")
        response = "Command executed successfully."
        tts = gTTS(text=response, lang='en')
        tts.save("response.mp3")
        os.system("start response.mp3")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def web_search(arguments):
    query = arguments.get("query")
    driver = webdriver.Chrome()
    driver.get(f"https://www.google.com/search?q={query}")
    driver.quit()
    return True

def play_song(arguments):
    song_name = arguments.get("song_name")
    logging.debug(f"Playing song: {song_name}")
    try:
        # Create a temporary directory within the project directory
        temp_dir = tempfile.mkdtemp(dir=os.getcwd())
        logging.debug(f"Created temporary directory: {temp_dir}")
        
        # Download the song using spotdl to the temporary directory
        spotdl_command = f'spotdl download "{song_name}" --output "{temp_dir}"'
        subprocess.run(spotdl_command, shell=True, check=True)
        
        # Find the downloaded song file
        song_files = glob.glob(os.path.join(temp_dir, "*.mp3"))
        if not song_files:
            logging.error(f"Failed to find downloaded song: {song_name}")
            shutil.rmtree(temp_dir)  # Clean up the temporary directory
            return False
        
        # Play the song using vlc-python in a separate thread
        def play_song_thread():
            try:
                instance = vlc.Instance()
                player = instance.media_player_new()
                media = instance.media_new(song_files[0])
                player.set_media(media)
                player.play()
                
                # Wait for the song to finish playing
                while player.get_state() != vlc.State.Ended and not thread_manager.stop_event.is_set():
                    time.sleep(1)
                
                logging.debug(f"Song {song_name} has finished playing")
                
                # Clean up the temporary directory
                shutil.rmtree(temp_dir)
                logging.debug(f"Deleted temporary directory: {temp_dir}")
            except Exception as e:
                logging.error(f"Failed to play song: {e}")
                if 'temp_dir' in locals():
                    shutil.rmtree(temp_dir)  # Clean up the temporary directory if an error occurs
        
        # Start the song playing thread
        song_thread = thread_manager.start_thread(play_song_thread)
        
        return True
    except Exception as e:
        logging.error(f"Failed to play song: {e}")
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)  # Clean up the temporary directory if an error occurs
        return False

# Signal handler to stop all threads when the main process is terminated
def signal_handler(sig, frame):
    logging.info("Main process terminated. Stopping all threads.")
    thread_manager.stop_all_threads()
    sys.exit(0)

# Set up signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Initialize thread manager
setup_thread_manager()