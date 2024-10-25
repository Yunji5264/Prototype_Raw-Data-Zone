import tkinter as tk
from tkinter import messagebox


import tkinter as tk
from tkinter import messagebox

class MeasureSelectionApp:
    def __init__(self, root, columns):
        self.root = root
        # Initialize data dictionary
        self.data = {
            "parameters": columns,
            "measures": [],
            "complementaryInfo": []
        }

        # Window configuration
        self.root.title("Select Measures")
        self.root.geometry("400x400")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)  # Keep window on top

        # Selection prompt
        label = tk.Label(self.root, text="Select columns that are measures (optional):")
        label.pack(pady=10)

        # Create scrolling area and button frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        # Canvas and Scrollbar configuration
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Generate checkboxes
        self.check_vars = {}
        for item in self.data["parameters"]:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(scrollable_frame, text=item, variable=var)
            cb.pack(anchor="w")
            self.check_vars[item] = var

        # Bottom button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(side="bottom", fill="x", pady=10)

        # Submit button
        submit_button = tk.Button(button_frame, text="Submit", command=self.submit_selection)
        submit_button.pack(pady=5)

    def submit_selection(self):
        # Update the dictionary based on user selections
        self.data["measures"] = [item for item, var in self.check_vars.items() if var.get()]
        self.data["complementaryInfo"] = [item for item, var in self.check_vars.items() if not var.get()]

        # Show selection results and close the window
        messagebox.showinfo("Selection Completed", f"Measures selected: {self.data['measures']}")
        self.root.destroy()

    def get_ci_m(self):
        # Return complementaryInfo and measures; measures can be empty
        return self.data["complementaryInfo"], self.data["measures"]


