import tkinter as tk
from tkinter import ttk, filedialog
from profiler import UltraProfiler
import os
import pandas as pd
import time
import sys
import io

class TextRedirector(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, s):
        self.text_widget.insert(tk.END, s)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class ProfilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UltraProfiler GUI")
        self.profiler = UltraProfiler()
        self.script_path = None

        # Menu
        menu = tk.Menu(root)
        root.config(menu=menu)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Script", command=self.load_script)

        # Buttons
        self.run_btn = tk.Button(root, text="Run Profiler", command=self.run_profiler)
        self.run_btn.pack(pady=5)

        # Treeview for block stats
        self.tree = ttk.Treeview(root, columns=("Duration", "Mem", "Funcs"), show="headings")
        self.tree.heading("Duration", text="Time (s)")
        self.tree.heading("Mem", text="Peak Mem (MB)")
        self.tree.heading("Funcs", text="Functions")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Text widget for issues
        self.issue_text = tk.Text(root, height=10)
        self.issue_text.pack(fill=tk.BOTH, expand=True)

    def load_script(self):
        self.script_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if self.script_path:
            self.root.title(f"UltraProfiler GUI - {os.path.basename(self.script_path)}")
            self.issue_text.delete("1.0", tk.END)
            self.issue_text.insert(tk.END, f"Loaded script: {self.script_path}\n")


    def run_profiler(self):
        # Clear previous results
        self.tree.delete(*self.tree.get_children())
        self.issue_text.delete("1.0", tk.END)
        self.profiler = UltraProfiler()  # reset profiler

        # Redirect stdout to GUI
        sys.stdout = TextRedirector(self.issue_text)

        # Execute script
        global_ns = {"pd": pd, "time": time, "profiler": self.profiler, "os": os}
        with open(self.script_path, "r") as f:
            code = f.read()
        try:
            exec(code, global_ns)
        except Exception as e:
            print(f"Error running script: {e}")

        # Restore stdout
        sys.stdout = sys.__stdout__

        # Populate Treeview with block stats
        for block in self.profiler.blocks:
            self.tree.insert("", tk.END, values=(
                block['name'],
                f"{block['duration']:.2f}",
                f"{block['mem_peak']/1e6:.2f}",
                len(block.get("functions_defined", []))
            ))


if __name__ == "__main__":
    root = tk.Tk()
    gui = ProfilerGUI(root)
    root.mainloop()
