import tkinter as tk
from tkinter import ttk
import cli
import threading
import subprocess
from playsound import playsound
from verify import repair_generated_code
import os

MODEL = "phi"  # Default model for all operations


def ensure_model_async():
    def task():
        try:
            result = subprocess.run(["ollama", "show", MODEL],
                                    check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

    # Change style
    style = ttk.Style()
    style.theme_use("classic")  # Use a predefined theme

    # Start loading model in background
    ensure_model_async()

    # Callback function to handle input and call other functions
    def handle_input(action):
        ensure_model_async()
        user_query = dialogue_input.get()
        dialogue_text.insert(tk.END, "Processing...\n")  # Show a loading message
        thread = threading.Thread(target=process_query, args=(user_query, action), daemon=True)
        thread.start()

    def process_query(user_query, action):
        try:
            if action == "Code":
                explanation, code, sources = cli.codegen_command(user_query, MODEL)
                update_output("Code generated. Running syntax check...\n", dialogue_text)
                # Save the generated code to a temporary file for syntax checking
                temp_file = "output.py"
                with open(temp_file, "w") as f:
                    f.write(code)

                # Perform syntax check
                try:
                    compile(code, "<string>", "exec")
                    # Syntax check passed, update the GUI
                    update_output(explanation, dialogue_text)
                    update_output(code, code_output_text)
                    update_output("Syntax check passed!\n", dialogue_text)

                    fixed, msg = repair_generated_code(
                        file_path=temp_file,
                        repo_path=os.getcwd(),
                        replace_with="placeholder.csv"
                    )
                    if fixed:
                        update_output(msg + "\n", code_output_text)
                    else:
                        update_output("No file name issues found in code.\n", code_output_text)
                except SyntaxError as e:
                    # Syntax check failed, show error in the GUI
                    update_output("Syntax check failed:\n" + e, dialogue_text)
            elif action == "Query":
                output = cli.query_command(user_query, MODEL)
                update_output(output, dialogue_text)
        except Exception as e:
            update_output(f"Error: {e}\n", dialogue_text)
        play_sound_async('chime.mp3')

    def update_output(output, target_widget):
        target_widget.insert(tk.END, output + "\n")
        target_widget.see(tk.END)

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

    # Column 1: Inputs
    rag_frame = ttk.LabelFrame(root, text="Inputs", padding=10)
    rag_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    # Add a Text widget inside the LabelFrame for redirected output
    rag_text = tk.Text(rag_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    rag_text.pack(fill="both", expand=True)

    # Add a Label above the rag_input
    rag_label = tk.Label(rag_frame, text="Enter folder path to ingest (e.g. data):")
    rag_label.pack(fill="x", pady=(5, 0))
    # Input box for user to enter folder path for ingestion
    rag_input = tk.Entry(rag_frame)
    rag_input.pack(fill="x", pady=(0, 5))
    rag_input.insert(0, "Enter folder name here")
    rag_input.bind("<FocusIn>", clear_entry)
    # Add a button to submit folder path
    submit_ingest = ttk.Button(rag_frame, text="Submit", command=ingest_data)
    submit_ingest.pack(pady=(10, 0))

    # Column 2: Dialogue Box
    dialogue_frame = ttk.LabelFrame(root, text="LLM Dialogue", padding=10)
    dialogue_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    dialogue_text = tk.Text(dialogue_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    dialogue_text.pack(fill="both", expand=True)

    # Add a Label above the rag_input
    dialogue_label = tk.Label(dialogue_frame, text="Enter query to LLM:")
    dialogue_label.pack(fill="x", pady=(5, 0))
    # Input box for user to enter command for code generation
    dialogue_input = tk.Entry(dialogue_frame)
    dialogue_input.pack(fill="x", pady=(0, 5))
    dialogue_input.insert(0, "Enter query here")
    dialogue_input.bind("<FocusIn>", clear_entry)

    # Update button commands
    button_frame = tk.Frame(dialogue_frame)
    button_frame.pack(pady=(10, 10))
    code_button = tk.Button(button_frame, text="Generate Code", command=lambda: handle_input("Code"))
    code_button.pack(side=tk.LEFT, padx=(0, 5))
    query_button = tk.Button(button_frame, text="Ask Question", command=lambda: handle_input("Query"))
    query_button.pack(side=tk.LEFT, padx=(5, 0))

    # Column 3: Outputs
    container_frame = ttk.LabelFrame(root, text="Outputs", padding=10)
    container_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
    # Add a Text widget for code output in the container_frame
    code_output_text = tk.Text(container_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    code_output_text.pack(fill="both", expand=True)

    # Configure column weights for resizing
    root.columnconfigure(0, weight=2)
    root.columnconfigure(1, weight=2)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(0, weight=1)

    # Run the application
    play_sound_async('chime.mp3')
    root.mainloop()


if __name__ == "__main__":
    create_gui()
