import tkinter as tk
from tkinter import ttk
import compile_csv_summary
import cli
import threading
import sys
import subprocess
# import required module
from playsound import playsound
import cProfile

MODEL = "phi"  # Default model for all operations


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


def ensure_model_async():
    def task():
        try:
            result = subprocess.run(["ollama", "show", MODEL], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode != 0:
                subprocess.Popen(["ollama", "pull", MODEL])
        except subprocess.CalledProcessError:
            subprocess.Popen(["ollama", "pull", MODEL])

    threading.Thread(target=task, daemon=True).start()

def play_sound_async(sound_file):
    threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()

def create_gui():
    # Create the main window
    root = tk.Tk()
    root.title("Telemetry LLM Interface")
    root.geometry("800x400")  # Set the window size
    root.state('zoomed')  # Maximize the window (with top bar)

    # Start loading model in background
    ensure_model_async()

    # Callback function to handle input and call other functions
    # Callback function to handle input and call other functions
    def handle_input(action):
        ensure_model_async()
        user_query = dialogue_input.get()
        dialogue_text.insert(tk.END, "Processing...")  # Show a loading message
        thread = threading.Thread(target=process_query, args=(user_query,action), daemon=True)
        thread.start()

    def process_query(user_query, action):
        try:
            if action == "Code":
                output = cli.codegen_command(user_query, MODEL)
            elif action == "Query":
                output = cli.query_command(user_query, MODEL)
            update_output(output, dialogue_text)
        except Exception as e:
            update_output(f"Error: {e}\n", dialogue_text)
        play_sound_async('chime.mp3')

    def update_output(output, target_widget):
        target_widget.insert(tk.END, output + "\n")
        target_widget.see(tk.END)
        #playsound('chime.mp3')

    def ingest_data():
        def run_ingest_data():
            folder = rag_input.get()
            generator = cli.ingest_command(folder, MODEL)

            def process_next():
                try:
                    message = next(generator)
                    update_output(message, rag_text)
                    rag_text.after(10, process_next)  # Schedule the next message
                except StopIteration:
                    play_sound_async('chime.mp3')  # Play sound when done
                except Exception as e:
                    update_output(f"Error: {e}", rag_text)

            process_next()  # Start processing the generator

        thread = threading.Thread(target=run_ingest_data, daemon=True)
        thread.start()

    def clear_entry(event):
        event.widget.delete(0, tk.END)

    # Column 1: Dialogue Box
    dialogue_frame = ttk.LabelFrame(root, text="Dialogue Box", padding=10)
    dialogue_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    dialogue_text = tk.Text(dialogue_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    dialogue_text.pack(fill="both", expand=True)

    # Add a Label above the rag_input
    dialogue_label = tk.Label(dialogue_frame, text="Enter command to generate code:")
    dialogue_label.pack(fill="x", pady=(0, 5))
    # Input box for user to enter command for code generation
    dialogue_input = tk.Entry(dialogue_frame)
    dialogue_input.pack(fill="x", pady=(10, 0))
    dialogue_input.bind("<FocusIn>", clear_entry)

    # Update button commands
    button_frame = tk.Frame(dialogue_frame)
    button_frame.pack(pady=(10, 0))
    code_button = tk.Button(button_frame, text="Generate Code", command=lambda: handle_input("Code"))
    code_button.pack(side=tk.LEFT, padx=(0, 5))
    query_button = tk.Button(button_frame, text="Ask Question", command=lambda: handle_input("Query"))
    query_button.pack(side=tk.LEFT, padx=(5, 0))

    # Column 2: Outputs
    rag_frame = ttk.LabelFrame(root, text="Outputs", padding=10)
    rag_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    # Add a Text widget inside the LabelFrame for redirected output
    rag_text = tk.Text(rag_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    rag_text.pack(fill="both", expand=True)

    # Add a Label above the rag_input
    rag_label = tk.Label(rag_frame, text="Enter folder path to ingest (e.g. data):")
    rag_label.pack(fill="x", pady=(0, 5))
    # Input box for user to enter folder path for ingestion
    rag_input = tk.Entry(rag_frame)
    rag_input.pack(fill="x", pady=(10, 0))
    rag_input.insert(0, "Enter command here")
    rag_input.bind("<FocusIn>", clear_entry)
    # Add a button to submit folder path
    submit_ingest = tk.Button(rag_frame, text="Submit", command=ingest_data)
    submit_ingest.pack(pady=(10, 0))

    # Column 3: Analysis of Outputs
    container_frame = ttk.LabelFrame(root, text="Analysis of Outputs", padding=10)
    container_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    container_label = tk.Label(container_frame,
                               text="Extra information about the LLM output is shown here (e.g. confidence level)",
                               justify="left")
    container_label.pack(fill="both", expand=True)

    # Configure column weights for resizing
    root.columnconfigure(0, weight=2)
    root.columnconfigure(1, weight=2)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)

    # Run the application
    play_sound_async('chime.mp3')
    root.mainloop()


if __name__ == "__main__":
    cProfile.run(create_gui())
