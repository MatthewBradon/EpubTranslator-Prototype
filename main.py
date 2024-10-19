import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sys
import threading
from EpubTranslator import run

# Class to redirect print statements to the GUI and limit text length
class TextRedirector(object):
    def __init__(self, text_widget, tag="stdout", line_limit=100):
        self.text_widget = text_widget
        self.tag = tag
        self.line_limit = line_limit

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # Automatically scroll to the bottom
        self._limit_text_lines()

    def flush(self):
        pass  # Required for compatibility with file-like objects

    def _limit_text_lines(self):
        # Get the current number of lines in the text box
        lines = int(self.text_widget.index('end-1c').split('.')[0])
        if lines > self.line_limit:
            # Remove the first line (1.0 means line 1, character 0; '2.0' is line 2)
            self.text_widget.delete('1.0', '2.0')

# Function to run the script in a separate thread to prevent freezing the GUI
def run_script(file_path, finalZipPath, console_output, run_button, browse_button, select_dir_button):
    # Check if both fields have valid paths
    if not file_path or not finalZipPath:
        messagebox.showerror("Error", "Both the file and directory paths must be specified.")
        return

    # Disable all buttons while the script is running
    run_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)
    select_dir_button.config(state=tk.DISABLED)

    def task():
        try:
            print(f"Running translation on: {file_path}")
            run(file_path, finalZipPath)
            print("Script executed successfully")
            messagebox.showinfo("Success", "Script executed successfully")
        except Exception as e:
            print(f"Error: {e}")
            messagebox.showerror("Error", str(e))
        finally:
            # Re-enable all buttons after the script finishes
            run_button.config(state=tk.NORMAL)
            browse_button.config(state=tk.NORMAL)
            select_dir_button.config(state=tk.NORMAL)

    # Run the task in a separate thread to keep the GUI responsive
    threading.Thread(target=task).start()

# Function to open a file dialog and select a file
def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a file", 
        filetypes=(("EPUB files", "*.epub"), ("All files", "*.*"))
    )
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)

# Function to open a directory dialog and select a save directory
def select_directory():
    dir_path = filedialog.askdirectory(title="Select directory to save new EPUB")
    if dir_path:
        finalZipPath_entry.delete(0, tk.END)
        finalZipPath_entry.insert(0, dir_path)

# Create the main window
root = tk.Tk()
root.title("EPUB Translator")

# Create a file selection entry
file_label = tk.Label(root, text="Select EPUB file:")
file_label.pack(pady=10)

file_entry = tk.Entry(root, width=50)
file_entry.pack(padx=10, pady=5)

browse_button = tk.Button(root, text="Browse", command=open_file)
browse_button.pack(pady=5)

# Create a finalZipPath directory selection
finalZipPath_label = tk.Label(root, text="Select directory to save the translated EPUB:")
finalZipPath_label.pack(pady=10)

finalZipPath_entry = tk.Entry(root, width=50)
finalZipPath_entry.pack(padx=10, pady=5)

select_dir_button = tk.Button(root, text="Select Directory", command=select_directory)
select_dir_button.pack(pady=5)

# Create a scrolled text box for console output
console_output = scrolledtext.ScrolledText(root, height=10, width=70)
console_output.pack(pady=10)

# Create a button to run the script and disable it while running
run_button = tk.Button(root, text="Run Script", command=lambda: run_script(file_entry.get(), finalZipPath_entry.get(), console_output, run_button, browse_button, select_dir_button))
run_button.pack(pady=20)

# Redirect stdout and stderr to the text box with line limiting (100 lines)
sys.stdout = TextRedirector(console_output, "stdout", line_limit=100)
sys.stderr = TextRedirector(console_output, "stderr", line_limit=100)

# Start the GUI event loop
root.mainloop()