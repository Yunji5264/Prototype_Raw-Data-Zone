import shutil
import os
import tkinter as tk
from tkinter import messagebox, Tk, simpledialog, filedialog
from pathlib import Path
from save_on_cloud import *

# Specify the base path (where these folders have already been created)
base_path = r'C:\Users\ADMrechbay20\Documents\experimentation\RAW_DATA_ZONE'  # e.g., 'C:/Users/YourName/Documents'

# Retrieve the path to a specific theme
def get_path(structure, target, path=None):
    if path is None:
        path = []
    for key, sub_structure in structure.items():
        if key == target:
            return path + [key]
        elif sub_structure:
            found_path = get_path(sub_structure, target, path + [key])
            if found_path:
                return found_path
    return None


# Find the Least Common Ancestor (LCA) for multiple themes
def find_least_common_ancestor(folder_structure, selections):
    paths = [get_path(folder_structure, selection) for selection in selections]
    min_length = min(len(path) for path in paths if path)
    lca = []
    for i in range(min_length):
        current_level = paths[0][i]
        if all(path[i] == current_level for path in paths if len(path) > i):
            lca.append(current_level)
        else:
            break
    return lca

def determine_path(folder_structure, theme):
    """根据主题确定文件应上传的路径。

    参数:
    folder_structure (dict): 文件夹结构定义。
    theme (str): 文件的主题。

    返回:
    str: 文件应上传的路径。
    """
    path = ''
    for key, subfolders in folder_structure.items():
        if theme in subfolders:
            path = key + '/' + theme
        elif theme == key:
            path = key
    return path


# Save a file to the specified path
def save_file_to_path(source_file_path, target_path):
    # Get the file name
    filename = os.path.basename(source_file_path)

    # If target_path is empty, save to the base_path directory
    destination_folder = os.path.join(base_path, *target_path) if target_path else base_path
    os.makedirs(destination_folder, exist_ok=True)  # Create the directory if it does not exist

    destination_file_path = os.path.join(destination_folder, filename)

    # Copy the file
    shutil.copy(source_file_path, destination_file_path)
    print(f"\nFile copied to: {destination_file_path}")


# Tkinter UI
import tkinter as tk
from tkinter import messagebox

class ThemeSelectionApp:
    def __init__(self, root, folder_structure, file_path, measures, complementary_info):
        self.root = root
        self.folder_structure = folder_structure
        self.file_path = file_path
        self.measures = measures if measures else []
        self.complementary_info = complementary_info if complementary_info else []
        self.current_index = 0
        self.selected_measures_themes = []  # Stores each measure and its theme
        self.selected_complementary_themes = []  # Stores each complementary info and its theme
        self.final_theme = None

        # Check if there are measures or complementary_info available to select
        if not self.measures and not self.complementary_info:
            self.calculate_overall_theme()
            self.root.destroy()
            return

        # Set the initial selection type
        self.selection_type = "measure" if self.measures else "complementary_info"

        # Set window properties
        self.root.title("Theme Selection")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 500
        window_height = 400
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        self.display_current_selection()

    def display_current_selection(self):
        # Clear old widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Set the current item label
        if self.selection_type == "measure":
            current_item = self.measures[self.current_index]
            label_text = f"Select a theme for '{current_item}':"
        else:
            current_item = self.complementary_info[self.current_index]
            label_text = f"Select a theme for complementary info '{current_item}':"

        # Display label
        item_label = tk.Label(self.root, text=label_text, wraplength=450)
        item_label.pack(pady=10)

        # Create a scrollable area to hold radio buttons
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Create Canvas and Scrollbar
        canvas = tk.Canvas(frame)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Place the Canvas and Scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Theme radio buttons
        self.theme_var = tk.StringVar(value="")
        self.create_radiobuttons(self.folder_structure, scrollable_frame)

        # Fixed "Skip" and "Submit" buttons at the bottom
        button_frame = tk.Frame(self.root)
        button_frame.pack(side="bottom", fill="x", pady=5)

        if self.selection_type == "complementary_info":
            skip_button = tk.Button(button_frame, text="Skip", command=self.skip_selection)
            skip_button.pack(side="left", padx=10)

        submit_button = tk.Button(button_frame, text="Submit Selection", command=self.submit_selection)
        submit_button.pack(side="right", padx=10)

    def create_radiobuttons(self, structure, parent_frame=None):
        for key, sub_structure in structure.items():
            rb = tk.Radiobutton(parent_frame, text=key, variable=self.theme_var, value=key)
            rb.pack(anchor="w")

            if sub_structure:
                sub_frame = tk.Frame(parent_frame)
                sub_frame.pack(anchor="w", padx=20)
                self.create_radiobuttons(sub_structure, sub_frame)

    def skip_selection(self):
        # If skipping, add None to the corresponding list
        if self.selection_type == "measure":
            self.selected_measures_themes.append({self.measures[self.current_index]: None})
        else:
            self.selected_complementary_themes.append({self.complementary_info[self.current_index]: None})
        self.move_to_next_selection()

    def submit_selection(self):
        selected = self.theme_var.get()

        # For measures, selection is required; for complementary info, skipping is allowed
        if self.selection_type == "measure" and not selected:
            messagebox.showwarning("Warning", "Please select at least one theme.")
            return

        # Add selection to the corresponding list
        if self.selection_type == "measure":
            self.selected_measures_themes.append({self.measures[self.current_index]: selected})
        else:
            self.selected_complementary_themes.append({self.complementary_info[self.current_index]: selected})

        self.move_to_next_selection()

    def move_to_next_selection(self):
        # Check the current selection type and move to the next item
        if self.selection_type == "measure":
            if self.current_index < len(self.measures) - 1:
                self.current_index += 1
                self.display_current_selection()
            else:
                # If measures are done or empty, start selecting complementary_info
                self.selection_type = "complementary_info"
                self.current_index = 0
                # If complementary_info is empty, calculate the final theme directly
                if not self.complementary_info:
                    self.calculate_overall_theme()
                    self.root.destroy()  # Close window
                else:
                    self.display_current_selection()
        elif self.selection_type == "complementary_info":
            if self.current_index < len(self.complementary_info) - 1:
                self.current_index += 1
                self.display_current_selection()
            else:
                # Calculate the final theme after all selections
                self.calculate_overall_theme()
                self.root.destroy()  # Close window

    def calculate_overall_theme(self):
        # Filter out None values and find the least common ancestor theme
        filtered_themes = [theme for item in self.selected_measures_themes + self.selected_complementary_themes for
                           theme in item.values() if theme]
        overall_theme_path = find_least_common_ancestor(self.folder_structure,
                                                        filtered_themes) if filtered_themes else []
        # self.final_theme = " -> ".join(overall_theme_path) if overall_theme_path else "Root Directory"
        # messagebox.showinfo("Overall Theme", f"The least common ancestor is: {self.final_theme}")

        # Determine the path based on the theme
        determined_path = determine_path(self.folder_structure, overall_theme_path[0])
        bucket_name = 'prototype_raw_data'
        destination_blob_name = 'well-being/' + determined_path + '/' + os.path.basename(self.file_path)

        # Save the file to Google Cloud
        save_file_to_cloud(self.file_path, bucket_name, destination_blob_name)

        # # Save the file to the determined path
        # save_file_to_path(self.file_path, overall_theme_path)

    # Method to get the final theme path
    def get_final_theme(self):
        return self.final_theme

    # Get each measure and complementary_info with their corresponding theme
    def get_measures_and_themes(self):
        return self.selected_complementary_themes, self.selected_measures_themes
