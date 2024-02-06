import tkinter as tk
from tkinter import ttk, filedialog
import speech_recognition as sr
import pyttsx3
from googletrans import Translator  
from tkinter import Toplevel, Menu
import threading  # Import the threading module

# Create an original text box with program information
program_info_text = """
This program allows you to perform the following tasks:
- Recognize speech using a microphone (Recognizing English Only So Far)
- Select a translation language (Chinese, Japanese, Franch)
- Translate Recognized Text to the Selected Language
- Read and Save the Text From or Into a Text File
- Read out the Text (English Only So Far)
"""

# Create the main window
root = tk.Tk()
root.title("Voice Recognition and Text Processing")

# Create a label for displaying recognized text
text_label = ttk.Label(root, text="Please Write in the TextBox Below")
text_label.grid(row=0, column=0, columnspan=3, pady=5)

# Create a Text widget to display recognized text
text_display = tk.Text(root, height=25, width=75)
text_display.insert(tk.END, program_info_text)
text_display.grid(row=1, column=0, columnspan=3, padx=5)

# Create a frame for the buttons
button_frame = ttk.Frame(root)
button_frame.grid(row=2, column=0, columnspan=3, pady=5)

# Create a label to indicate voice recognition status
voice_status_label = ttk.Label(button_frame, text="Ready to Listen")
voice_status_label.grid(row=3, column=0, columnspan=3, padx=15, sticky="nse")

# Create a button to trigger voice recognition
def recognize_voice_thread():
    def recognize_voice():
        recognizer = sr.Recognizer()

        # Update the status label to indicate voice recognition is active
        voice_status_label.config(text="Listening...")

        with sr.Microphone() as source:
            audio = recognizer.listen(source)

        # Update the status label to indicate voice recognition has ended
        voice_status_label.config(text="Processing...")

        try:
            recognized_text = recognizer.recognize_google(audio)
            text_display.delete("1.0", tk.END)
            text_display.insert(tk.END, recognized_text)
        except sr.UnknownValueError:
            text_display.delete("1.0", tk.END)
            text_display.insert(tk.END, "Unable to recognize speech")
        except sr.RequestError:
            text_display.delete("1.0", tk.END)
            text_display.insert(tk.END, "Could not request results")

        # Clear the status label and display a message indicating that voice recognition has stopped
        voice_status_label.config(text="Voice Recording Stopped")

    # Create a thread for voice recognition
    voice_thread = threading.Thread(target=recognize_voice)
    voice_thread.daemon = True  # Set the thread as a daemon to close it when the program exits
    voice_thread.start()

voice_button = ttk.Button(button_frame, text="Recognize Voice", command=recognize_voice_thread)
voice_button.grid(row=0, column=0, padx=25, pady=5)

# Create a function to open a language selection window
def open_language_selection():
    language_window = Toplevel(root)
    language_window.title("Select Language")
    
    # Create a label and combobox for language selection
    language_label = ttk.Label(language_window, text="Select Language:")
    language_label.pack()
    
    language_options = ["English", "Chinese", "Japanese", "French"]
    selected_language = tk.StringVar()
    
    language_combobox = ttk.Combobox(language_window, textvariable=selected_language, values=language_options)
    language_combobox.pack()
    
    # Create a button to perform the translation
    def translate_selected_language():
        selected_language_code = {
            "English": "en",
            "Chinese": "zh-CN",
            "Japanese": "ja",
            "French": "fr"
        }
        translator = Translator()
        text_to_translate = text_display.get("1.0", tk.END)
        selected_lang = selected_language.get()
        translated_text = translator.translate(text_to_translate, dest=selected_language_code.get(selected_lang, "en"))
        text_display.delete("1.0", tk.END)
        text_display.insert(tk.END, translated_text.text)
        language_window.destroy()  # Close the language selection window
    
    translate_button = ttk.Button(language_window, text="Translate", command=translate_selected_language)
    translate_button.pack()

# Create a button to open the language selection window
language_selection_button = ttk.Button(button_frame, text="Select Translation Language", command=open_language_selection)
language_selection_button.grid(row=0, column=1, padx=25, pady=5)

# Create a function to open a file dialog and read text from a selected file
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Word Files", "*.docx")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                text_display.delete("1.0", tk.END)
                text_display.insert(tk.END, file_content)
        except Exception as e:
            text_display.delete("1.0", tk.END)
            text_display.insert(tk.END, f"Error: {str(e)}")

def save_text_to_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        text_to_save = text_display.get("1.0", tk.END)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(text_to_save)

def clear_text_display():
    text_display.delete("1.0", tk.END)

def read_text_aloud_thread():
    def read_text_aloud():
        try:
            text_to_read = text_display.get("1.0", tk.END)
            engine = pyttsx3.init()
            engine.say(text_to_read)
            engine.runAndWait()
        except Exception as e:
            print(f"Error during TTS: {e}")

    voice_thread = threading.Thread(target=read_text_aloud)
    voice_thread.daemon = True
    voice_thread.start()

voice_output_button = ttk.Button(button_frame, text="Voice Output", command=read_text_aloud_thread)
voice_output_button.grid(row=0, column=3, padx=25, pady=5)

clears_button = ttk.Button(button_frame, text="Clear Text", command=clear_text_display)
clears_button.grid(row=0, column=4, padx=25, pady=5)

# Bind keyboard shortcuts
root.bind("<Control-s>", lambda event=None: save_text_to_file())
root.bind("<Control-r>", lambda event=None: open_file())

# Create a "File" menu
menu_bar = Menu(root)
root.config(menu=menu_bar)
file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open File", command=open_file)
file_menu.add_command(label="Save Text to File", command=save_text_to_file)

# Start the GUI main loop
root.mainloop()
