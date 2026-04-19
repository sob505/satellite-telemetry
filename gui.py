import tkinter as tk
from tkinter import ttk
import compile_csv_summary
import cli
import threading
import sys
import subprocess

MODEL = "phi"  # Default model to use for all operations
class RedirectOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.after(0, lambda: self._append(message))

    def _append(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass  # Required for compatibility with sys.stdout

def ensure_model(model="phi"):
    try:
        subprocess.run(["ollama", "show", model], check=True, stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        subprocess.run(["ollama", "pull", model], check=True)

def create_gui():
    ensure_model(model=MODEL)

    # Create the main window
    root = tk.Tk()
    root.title("Telemetry LLM Interface")
    root.geometry("800x400")  # Set the window size
    root.state('zoomed')  # Maximize the window (with top bar)

    # Callback function to handle input and call other functions
    # Callback function to handle input and call other functions
    def handle_input():
        user_query = user_input.get()
        dialogue_output.config(text="Processing...")  # Show a loading message
        thread = threading.Thread(target=process_query, args=(user_query,), daemon=True)
        thread.start()

    def process_query(user_query):
        try:
            output = cli.codegen_command(user_query, MODEL)
            update_output(output)
        except Exception as e:
            update_output(f"Error: {e}")

    def update_output(output):
        output_text.insert(tk.END, output + "\n")
        output_text.see(tk.END)

    def ingest_data():
        try:
            filename = rag_input.get()
            output = cli.ingest_command(filename, MODEL)
            update_output(output)
        except Exception as e:
            output_text.insert(tk.END, f"Error: {e}")

    def clear_entry(event):
        if user_input.get() == "Enter command here":
            user_input.delete(0, tk.END)

    # Column 1: Dialogue Box
    dialogue_frame = ttk.LabelFrame(root, text="Dialogue Box", padding=10)
    dialogue_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    dialogue_output = tk.Label(dialogue_frame, text="LLM's natural language response is here", justify="left")
    dialogue_output.pack(fill="both", expand=True, pady=(0, 10))

    user_input = tk.Entry(dialogue_frame)
    user_input.pack(fill="x", pady=(10, 0))

    user_input.bind("<FocusIn>", clear_entry)

    # Add a button to trigger the callback
    submit_button = tk.Button(dialogue_frame, text="Submit", command=handle_input)
    submit_button.pack(pady=(10, 0))

    # Column 2: Outputs
    output_frame = ttk.LabelFrame(root, text="Outputs", padding=10)
    output_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Add a Text widget inside the LabelFrame for redirected output
    output_text = tk.Text(output_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    output_text.pack(fill="both", expand=True)

    rag_input = tk.Entry(output_frame)
    rag_input.pack(fill="x", pady=(10, 0))
    rag_input.insert(0, "Enter command here")

    # Add a button to trigger the callback
    submit_ingest = tk.Button(output_frame, text="Submit", command=ingest_data)
    submit_ingest.pack(pady=(10, 0))

    # Column 3: Analysis of Outputs
    container_frame = ttk.LabelFrame(root, text="Vertical Container", padding=10)
    container_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    container_label = tk.Label(container_frame, text="Extra information about the LLM output is shown here (e.g. confidence level)", justify="left")
    container_label.pack(fill="both", expand=True)

    # Configure column weights for resizing
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)

    # Run the application
    root.mainloop()

if __name__ == "__main__":
    create_gui()