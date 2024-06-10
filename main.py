import re
import tkinter as tk
from tkinter import messagebox, filedialog
import openai
from pypdf import PdfReader

# Indsæt din OpenAI API-nøgle her
openai.api_key = 'your-openai-api-key'

# Funktion til at tjekke for følsomme oplysninger
def detect_sensitive_info(prompt):
    patterns = {
        "CPR": r"\b\d{6}-\d{4}\b",
        "Phone": r"\b\d{2,4}[-\s]?\d{2,4}[-\s]?\d{2,4}\b",
        "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Address": r"\b\d{1,3}\s[A-Za-z]{1,}\s[A-Za-z]{1,}\b",
        "Address_DK":r"\b[A-Za-zæøåÆØÅ]+(?:\s[A-Za-zæøåÆØÅ]+)*\s\d{1,3}(?:\s?[A-Za-zæøåÆØÅ]*\s?\d*\.?\s?[A-Za-z]*)?\b"
    }

    for key, pattern in patterns.items():
        if re.search(pattern, prompt):
            return True, key
    
    return False, None

# Funktion til at sende besked til ChatGPT og få svar
def get_chatgpt_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# Funktion til at sende besked
def send_message(event=None):
    message = entry.get()
    is_sensitive, info_type = detect_sensitive_info(message)
    
    if is_sensitive:
        messagebox.showwarning("Advarsel", f"Din besked indeholder følsomme oplysninger: {info_type}. Vær venlig at fjerne dem.")
    else:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "Du: " + message + "\n")
        chat_log.config(state=tk.DISABLED)
        
        # Få svar fra ChatGPT
        response = get_chatgpt_response(message)
        
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "ChatGPT: " + response + "\n")
        chat_log.config(state=tk.DISABLED)
        
        entry.delete(0, tk.END)

# Funktion til at uploade og læse PDF-fil
def upload_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            display_pdf_text(text)

def display_pdf_text(text):
    is_sensitive, info_type = detect_sensitive_info(text)
    if is_sensitive:
        messagebox.showwarning("Advarsel", f"Den uploadede PDF indeholder følsomme oplysninger: {info_type}. Vær venlig at fjerne dem.")
    else:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "PDF indhold:\n" + text + "\n")
        chat_log.config(state=tk.DISABLED)

# Opret hovedvinduet
root = tk.Tk()
root.title("ChatGPT Chatbox")

# Opret chat log
chat_log = tk.Text(root, state=tk.DISABLED, width=50, height=20, bg="light gray")
chat_log.pack(padx=10, pady=10)

# Opret tekstfelt til input
entry = tk.Entry(root, width=50)
entry.pack(padx=10, pady=10)
entry.bind("<Return>", send_message)  # Bind Enter-tasten til send_message-funktionen

# Opret send-knap
send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(padx=10, pady=10)

# Opret upload-knap
upload_button = tk.Button(root, text="Upload PDF", command=upload_pdf)
upload_button.pack(padx=10, pady=10)

# Kør GUI'en
root.mainloop()
