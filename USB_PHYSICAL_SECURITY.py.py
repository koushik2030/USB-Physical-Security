import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import threading
import http.server
import socketserver
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import subprocess
import requests
from PIL import Image, ImageTk
from io import BytesIO
import re
import hashlib

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Path to store registered Gmail hash
registration_hash_file = os.path.join(script_dir, "registered_gmail_hash.txt")

# Sender email credentials
sender_email = "usb.boss234@gmail.com"  # Replace with your sender email
sender_password = "yrjb opgd jqsf xxra"  # Replace with your sender password

# Global variable to store the generated password
generated_password = None

# Function to start the local server
def start_local_server():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

# Function to open project info
def open_project_info():
    # Run the local server in a separate thread
    threading.Thread(target=start_local_server, daemon=True).start()
    # Open the HTML page in the default web browser
    webbrowser.open('http://teamboss.great-site.net/')

# Function to validate email
def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email)

# Function to hash a string (Gmail in this case)
def hash_string(s):
    return hashlib.sha256(s.encode()).hexdigest()

# Function to register Gmail
def register_gmail(email):
    hashed_email = hash_string(email)
    with open(registration_hash_file, "w") as f:
        f.write(hashed_email)
    
    messagebox.showinfo("Registration Successful", "Gmail registered successfully.")

# Function to open registration form
def open_registration_form():
    if os.path.exists(registration_hash_file) and os.path.getsize(registration_hash_file) > 0:
        messagebox.showinfo("Already Registered", "You are already registered with your email")
        return
    
    registration_window = tk.Toplevel(root)
    registration_window.title("Registration Form")
    registration_window.geometry("300x200")

    tk.Label(registration_window, text="Enter your Gmail address:").pack(pady=10)
    email_entry = ttk.Entry(registration_window, width=30)
    email_entry.pack(pady=10)

    def verify_email():
        email = email_entry.get()
        if email:
            if is_valid_email(email):
                register_gmail(email)
                registration_window.destroy()  # Close registration window after registration
            else:
                messagebox.showerror("Invalid Email", "The entered email is not valid.")

    verify_button = ttk.Button(registration_window, text="Register", command=verify_email)
    verify_button.pack(pady=10)

# Function to send password email
def send_password_email(email_address):
    global generated_password
    generated_password = generate_password()
    
    # Email details
    subject = "Password for USB Control"
    body = f"Your generated password is: {generated_password}"
    
    # Create email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return generated_password
    except Exception as e:
        print(f"Failed to send email: {e}")
        return None

# Function to generate a random password
def generate_password():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=8))

# Function to open login page
def check_user_generate_password():
    if not os.path.exists(registration_hash_file) or os.path.getsize(registration_hash_file) == 0:
        messagebox.showwarning("Not Registered", "You need to register your Gmail first.")
        return

    login_window = tk.Toplevel(root)
    login_window.title("Login Page")
    login_window.geometry("350x250")

    tk.Label(login_window, text=f"Enter your Registered Gmail address to receive the password").pack(pady=5)

    tk.Label(login_window, text="Enter your Gmail address:").pack(pady=5)
    gmail_entry = ttk.Entry(login_window, width=30)
    gmail_entry.pack(pady=5)

    def generate_new_password():
        email = gmail_entry.get()
        if os.path.exists(registration_hash_file):
            with open(registration_hash_file, "r") as f:
                stored_hash = f.read().strip()
                entered_hash = hash_string(email)
                if entered_hash == stored_hash:
                    sent_password = send_password_email(email)
                    if sent_password:
                        messagebox.showinfo("Password Sent", f"Password sent to your registered mail. Please check your email.")
                        login_window.destroy()
                    else:
                        messagebox.showerror("Failed to Send", "Failed to send password email. Please try again.")
                else:
                    messagebox.showerror("Invalid Gmail", "Entered Gmail does not match registered Gmail.")
        else:
            messagebox.showwarning("Not Registered", "You need to register your Gmail first.")

    generate_button = ttk.Button(login_window, text="Generate Password", command=generate_new_password)
    generate_button.pack(pady=10)

# Function to verify the entered password
def verify_password(input_password):
    global generated_password
    if input_password == generated_password:
        return True
    else:
        messagebox.showerror("Invalid Password", "The entered password is incorrect.")
        return False

# Function to enable USB ports on Windows
def enable_usb_windows():
    password = simpledialog.askstring("Enter Password", "Enter the password received in your email:", show='*')
    if password and verify_password(password):
        try:
            key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
            subprocess.run(["reg", "add", f"HKEY_LOCAL_MACHINE\\{key_path}", "/v", "Start", "/t", "REG_DWORD", "/d", "3", "/f"], check=True)
            messagebox.showinfo("USB Control", "USB ports enabled successfully.")
            update_usb_status_label("Enabled")
        except PermissionError:
            messagebox.showerror("Error", "Access denied. Run the script with administrator privileges.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to enable USB ports: {e}")
    else:
        messagebox.showerror("Invalid Password", "Incorrect password. Operation canceled.")

# Function to disable USB ports on Windows
def disable_usb_windows():
    password = simpledialog.askstring("Enter Password", "Enter the password received in your email:", show='*')
    if password and verify_password(password):
        try:
            key_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
            subprocess.run(["reg", "add", f"HKEY_LOCAL_MACHINE\\{key_path}", "/v", "Start", "/t", "REG_DWORD", "/d", "4", "/f"], check=True)
            messagebox.showinfo("USB Control", "USB ports disabled successfully.")
            update_usb_status_label("Disabled")
        except PermissionError:
            messagebox.showerror("Error", "Access denied. Run the script with administrator privileges.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to disable USB ports: {e}")
    else:
        messagebox.showerror("Invalid Password", "Incorrect password. Operation canceled.")

# Function to update USB port status label
def update_usb_status_label(status):
    status_label_usb.config(text=f"USB Port Status: {status}")
    if status == "Enabled":
        status_label_usb.config(bg="lightgreen")
    elif status == "Disabled":
        status_label_usb.config(bg="red")
    else:
        status_label_usb.config(bg="white")

# Function to display the image
def display_image(frame):
    image_url = "https://infosysmysore.in/wp-content/uploads/2020/03/is-pen-drive-allowed-in-infosys-mysore-campus.jpg"
    response = requests.get(image_url)
    image_data = response.content
    image = Image.open(BytesIO(image_data))
    image = image.resize((300, 225))  # Resize the image
    photo = ImageTk.PhotoImage(image)

    image_label = tk.Label(frame, image=photo)
    image_label.image = photo
    image_label.pack()

# Initialize Tkinter root
root = tk.Tk()
root.title("USB Control System")
root.geometry("600x700")

# Create a top frame for buttons
top_frame = tk.Frame(root)
top_frame.pack(pady=20)

# Project info button
project_info_button = ttk.Button(top_frame, text="Project Info", command=open_project_info, style='TButton', padding=(10, 5), width=15)
project_info_button.grid(row=0, column=0, padx=10)

# Register Gmail button
register_gmail_button = ttk.Button(top_frame, text="Register Gmail", command=open_registration_form, style='TButton', padding=(10, 5), width=15)
register_gmail_button.grid(row=0, column=1, padx=10)

# Frame for image
image_frame = tk.Frame(root)
image_frame.pack(pady=20)
display_image(image_frame)

# USB control buttons
usb_button_frame = tk.Frame(root)
usb_button_frame.pack(pady=10)

enable_usb_button = ttk.Button(usb_button_frame, text="Enable USB", command=enable_usb_windows, style='TButton', padding=(10, 5), width=15)
enable_usb_button.grid(row=0, column=0, padx=10)

disable_usb_button = ttk.Button(usb_button_frame, text="Disable USB", command=disable_usb_windows, style='TButton', padding=(10, 5), width=15)
disable_usb_button.grid(row=0, column=1, padx=10)

# USB status label
status_label_usb = tk.Label(root, text="USB Port Status: Unknown", bg="white", relief="solid", width=30, height=2)
status_label_usb.pack(pady=10)

# Check User and Generate Password button
check_user_button = ttk.Button(root, text="Check User & Generate Password", command=check_user_generate_password, style='TButton', padding=(10, 5), width=25)
check_user_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
