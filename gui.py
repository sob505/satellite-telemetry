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
        update_output(f"User query: {user_query}\n", dialogue_text, align="right")
        dialogue_text.insert(tk.END, "Processing...\n")  # Show a loading message
        thread = threading.Thread(target=process_query, args=(user_query, action), daemon=True)
        thread.start()
        global prev_query, prev_action
        prev_query = user_query
        prev_action = action

    def feedback_input():
        ensure_model_async()
        user_query = r'You did not do it right. Please retry query: ' + prev_query
        action = prev_action
        dialogue_text.insert(tk.END, "Processing...\n")  # Show a loading message
        update_output(f"Retrying {user_query}\n", dialogue_text, align="right")
        thread = threading.Thread(target=process_query, args=(user_query,action), daemon=True)
        thread.start()

    def feedback_input():
        ensure_model_async()
        user_query = r'You did not do it right. Please retry query: ' + prev_query
        action = prev_action
        dialogue_text.insert(tk.END, "Processing...\n")  # Show a loading message
        thread = threading.Thread(target=process_query, args=(user_query,action), daemon=True)
        thread.start()

    def process_query(user_query, action):
        try:
            if action == "Code":
                explanation, code, sources = cli.codegen_command(user_query, MODEL)
                print(f"Explanation: {explanation}")  # Debugging
                update_output("Code generated. Running syntax check...\n", dialogue_text)
                # Save the generated code to a temporary file for syntax checking
                temp_file = "output.py"
                with open(temp_file, "w") as f:
                    f.write(code)

                # Perform syntax check
                try:
                    compile(code, "<string>", "exec")
                    # Syntax check passed, update the GUI
                    update_output("Explanation: \n" + explanation, dialogue_text)
                    update_output(code, code_output_text)
                    update_output("Syntax check passed!\n", dialogue_text)

                    fixed, msg = repair_generated_code(
                        file_path=temp_file,
                        repo_path=os.getcwd(),
                        replace_with="placeholder.csv"
                    )
                    if fixed:
                        update_output(msg + "\n", dialogue_text)
                    else:
                        update_output("No file name issues found in code.\n", dialogue_text)
                except SyntaxError as e:
                    # Syntax check failed, show error in the GUI
                    update_output("Syntax check failed:\n", dialogue_text)
            elif action == "Query":
                output = cli.query_command(user_query, MODEL)
                update_output(output, dialogue_text)
        except Exception as e:
            update_output(f"Error: {e}\n", dialogue_text)
        play_sound_async('chime.mp3')

    def update_output(output, target_widget, align="left"):
        # Configure the tag for boxed messages
        target_widget.tag_configure("box", lmargin1=10, lmargin2=10, rmargin=10, background="#f0f0f0", relief="solid", borderwidth=1)
        target_widget.tag_configure(align, justify=align)

        # Insert the text with the "box" tag
        if align == "right":
            target_widget.insert(tk.END, output + "\n", ("box", align))
        else:
            target_widget.insert(tk.END, output + "\n", align)
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

    # Create a Notebook widget for tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Tab 1: Ingesting Data
    ingest_tab = ttk.Frame(notebook)
    notebook.add(ingest_tab, text="Ingest Data")

    # Tab 2: LLM Dialogue and Outputs
    dialogue_tab = ttk.Frame(notebook)
    notebook.add(dialogue_tab, text="LLM Interaction")

    # Ingest Tab Content
    rag_frame = ttk.LabelFrame(ingest_tab, text="Inputs", padding=10)
    rag_frame.pack(fill="both", expand=True, padx=10, pady=10)

    rag_text = tk.Text(rag_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    rag_text.pack(fill="both", expand=True)

    rag_label = tk.Label(rag_frame, text="Enter folder path to ingest (e.g. data):")
    rag_label.pack(fill="x", pady=(5, 0))

    rag_input = tk.Entry(rag_frame)
    rag_input.pack(fill="x", pady=(0, 5))
    rag_input.insert(0, "Enter folder name here")
    rag_input.bind("<FocusIn>", clear_entry)

    submit_ingest = ttk.Button(rag_frame, text="Submit", command=ingest_data)
    submit_ingest.pack(pady=(10, 0))

    # Dialogue Tab Content
    dialogue_frame = ttk.LabelFrame(dialogue_tab, text="LLM Dialogue", padding=10)
    dialogue_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Create two columns
    left_frame = tk.Frame(dialogue_frame)
    left_frame.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 5))

    right_frame = tk.Frame(dialogue_frame)
    right_frame.pack(side=tk.RIGHT, fill="both", expand=True, padx=(5, 0))

    # Left Column: Dialogue Input
    dialogue_text = tk.Text(left_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    dialogue_text.pack(fill="both", expand=True)

    dialogue_label = tk.Label(left_frame, text="Enter query to LLM:")
    dialogue_label.pack(fill="x", pady=(5, 0))

    dialogue_input = tk.Entry(left_frame)
    dialogue_input.pack(fill="x", pady=(0, 5))
    dialogue_input.insert(0, "Enter query here")
    dialogue_input.bind("<FocusIn>", clear_entry)

    button_frame = tk.Frame(left_frame)
    button_frame.pack(pady=(10, 10))
    code_button = tk.Button(button_frame, text="Generate Code", command=lambda: handle_input("Code"))
    code_button.pack(side=tk.LEFT, padx=(0, 5))
    query_button = tk.Button(button_frame, text="Ask Question", command=lambda: handle_input("Query"))
    query_button.pack(side=tk.LEFT, padx=(5, 5))
    retry_button = tk.Button(button_frame, text="Retry", command=lambda: feedback_input())
    retry_button.pack(side=tk.LEFT, padx=(5, 0))

    # Right Column: Outputs
    code_output_text = tk.Text(right_frame, wrap=tk.WORD, state=tk.NORMAL, height=10, width=50)
    code_output_text.pack(fill="both", expand=True)

    # Run the application
    play_sound_async('chime.mp3')
    root.mainloop()


if __name__ == "__main__":
    create_gui()
