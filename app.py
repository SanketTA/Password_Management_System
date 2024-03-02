import tkinter as tk
from tkinter import messagebox
from pyDes import des, PAD_PKCS5
import hashlib
import sqlite3
import os

# Function to ensure key is 8 bytes
def ensure_key_size(key):
    if len(key) != 8:
        # If the key is not 8 bytes, hash it to get a suitable size
        hashed_key = hashlib.md5(key).digest()
        return hashed_key[:8]
    return key

# Function to pad data with PKCS5
def pad_data(data):
    pad_size = 8 - len(data) % 8
    return data + bytes([pad_size] * pad_size)

# Function to unpad data with PKCS5
def unpad_data(data):
    pad_size = data[-1]
    return data[:-pad_size]

# Function to generate key
def generate_key():
    key_file = "key.key"
    if os.path.exists(key_file):
        with open(key_file, "rb") as file:
            key = file.read()
    else:
        key = os.urandom(8)  # Generate a random 8-byte key for DES
        with open(key_file, "wb") as file:
            file.write(key)
    return key

# Function to encrypt password
def encrypt_password(key, password):
    key = ensure_key_size(key)
    d = des(key, PAD_PKCS5)
    encrypted_password = d.encrypt(pad_data(password.encode()))
    return encrypted_password

# Function to decrypt password
def decrypt_password(key, encrypted_password):
    key = ensure_key_size(key)
    d = des(key, PAD_PKCS5)
    decrypted_password = d.decrypt(encrypted_password)
    return unpad_data(decrypted_password).decode()

# Check if the database file exists, if not, create it
if not os.path.exists('passwords.db'):
    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE passwords (
            service TEXT PRIMARY KEY,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to add password to the database
def add_password():
    service = service_entry.get()
    username = username_entry.get()
    password = password_entry.get()
    custom_key = key_entry.get()

    if custom_key:
        key = custom_key.encode()
    else:
        key = generate_key()

    key = ensure_key_size(key)

    if service and username and password:
        encrypted_password = encrypt_password(key, password)

        conn = sqlite3.connect('passwords.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO passwords (service, username, password) VALUES (?, ?, ?)
        ''', (service, username, encrypted_password))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "Password added successfully!")
    else:
        messagebox.showwarning("Error", "Please fill in all the fields.")

# Function to get password from the database
def get_password():
    service = service_entry.get()
    custom_key = key_entry.get()

    if custom_key:
        key = custom_key.encode()
    else:
        key = generate_key()

    key = ensure_key_size(key)

    conn = sqlite3.connect('passwords.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, password FROM passwords WHERE service=?', (service,))
    result = cursor.fetchone()
    conn.close()

    if result:
        username_result, encrypted_password = result
        decrypted_password = decrypt_password(key, encrypted_password)
        messagebox.showinfo("Password", f"Username: {username_result}\nPassword: {decrypted_password}")
    else:
        messagebox.showwarning("Error", "Password not found.")

# GUI code
window = tk.Tk()
window.title("Password Manager")
window.configure(bg="red")

window.resizable(False, False)

center_frame = tk.Frame(window, bg="#d3d3d3")
center_frame.grid(row=0, column=0, padx=10, pady=10)

instructions = '''To add a password, fill in all the fields and press "Add Password".
To view the password, enter the Account Name (if Custom Key used fill it) and press "Get Password".'''

instruction_label = tk.Label(center_frame, text=instructions, bg="#d3d3d3")
instruction_label.grid(row=0, column=1, padx=10, pady=5)

service_label = tk.Label(center_frame, text="Account:", bg="#d3d3d3")
service_label.grid(row=1, column=0, padx=10, pady=5)
service_entry = tk.Entry(center_frame)
service_entry.grid(row=1, column=1, padx=10, pady=5)

username_label = tk.Label(center_frame, text="Username:", bg="#d3d3d3")
username_label.grid(row=2, column=0, padx=10, pady=5)
username_entry = tk.Entry(center_frame)
username_entry.grid(row=2, column=1, padx=10, pady=5)

password_label = tk.Label(center_frame, text="Password:", bg="#d3d3d3")
password_label.grid(row=3, column=0, padx=10, pady=5)
password_entry = tk.Entry(center_frame, show="*")
password_entry.grid(row=3, column=1, padx=10, pady=5)

key_label = tk.Label(center_frame, text="Custom Key:", bg="#d3d3d3")
key_label.grid(row=4, column=0, padx=10, pady=5)
key_entry = tk.Entry(center_frame)
key_entry.grid(row=4, column=1, padx=10, pady=5)

add_button = tk.Button(center_frame, text="Add Password", command=add_password, height=1, width=15)
add_button.grid(row=5, column=1, padx=10, pady=5)

get_button = tk.Button(center_frame, text="Get Password", command=get_password, height=1, width=15)
get_button.grid(row=6, column=1, padx=10, pady=5)

window.mainloop()
