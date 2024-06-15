import os
import glob
import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

# Paths to the Roblox versions directories
roblox_versions_paths = [
    r"C:\Program Files (x86)\Roblox\Versions",
    os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Roblox\Versions"),
    os.path.expandvars(r"C:\Users\%USERNAME%\AppData\Local\Bloxstrap\Versions")
]

def find_latest_version_folder(versions_paths):
    version_folders = []
    
    # Iterate over possible paths and collect version folders
    for path in versions_paths:
        version_folders.extend(glob.glob(os.path.join(path, 'version-*')))

    if not version_folders:
        raise FileNotFoundError("No version folders found in the specified directories.")
    
    # Sort the folders by their modification time in descending order
    version_folders.sort(key=os.path.getmtime, reverse=True)
    
    # Return the most recent version folder
    return version_folders[0]

def check_fast_flags(fast_flags_file):
    if os.path.exists(fast_flags_file):
        with open(fast_flags_file, 'r') as file:
            content = json.load(file)
            return content
    return {}

def edit_fast_flags(version_folder):
    # Path to the fast flags file
    client_settings_folder = os.path.join(version_folder, 'ClientSettings')
    fast_flags_file = os.path.join(client_settings_folder, 'ClientAppSettings.json')
    
    # Ensure the ClientSettings directory exists
    if not os.path.exists(client_settings_folder):
        os.makedirs(client_settings_folder)

    # Initialize current_flags with existing FastFlags
    current_flags = check_fast_flags(fast_flags_file)

    def remove_duplicates(flags):
        unique_flags = current_flags.copy()
        for key, value in flags.items():
            if key in unique_flags and unique_flags[key] == value:
                print(f"Flag '{key}' with value '{value}' already exists. Skipping.")
            else:
                unique_flags[key] = value
        return unique_flags

    def import_fast_flags():
        file_path = filedialog.askopenfilename(title="Select JSON file with FastFlags to import", filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, 'r') as file:
                try:
                    imported_flags = json.load(file)
                    return imported_flags
                except json.JSONDecodeError as e:
                    messagebox.showerror("Error", f"Failed to import FastFlags: {e}")
                    return {}
        return {}

    def input_fast_flags():
        def print_input():
            inp = inputtxt.get(1.0, "end-1c").strip()
            if inp:
                try:
                    flags_to_add = json.loads(inp)
                    flags_to_add = remove_duplicates(flags_to_add)  # Check and remove duplicates
                    frame.destroy()  # Close the input window after successful input
                    return flags_to_add
                except json.JSONDecodeError as e:
                    messagebox.showerror("Error", f"Invalid JSON format: {e}")
            else:
                messagebox.showwarning("Warning", "Please input FastFlags in JSON format.")
        
        # Create Tkinter window for manual input
        frame = tk.Tk()
        frame.title("Input FastFlags")
        frame.geometry('700x400')

        inputtxt = scrolledtext.ScrolledText(frame, height=23, width=80)
        inputtxt.pack()

        printButton = tk.Button(frame, text="Save", command=print_input)
        printButton.pack()

        frame.mainloop()

    def view_edit_fast_flags():
        view_edit_frame = tk.Tk()
        view_edit_frame.title("View/Edit FastFlags")
        view_edit_frame.geometry('700x400')

        current_flags_text = scrolledtext.ScrolledText(view_edit_frame, height=23, width=80)
        current_flags_text.insert(tk.END, json.dumps(current_flags, indent=4))
        current_flags_text.pack()

        def save_flags():
            nonlocal current_flags
            current_flags = check_fast_flags(fast_flags_file)  # Refresh current_flags
            
            # Update current_flags based on displayed text
            try:
                current_flags = json.loads(current_flags_text.get(1.0, tk.END))
            except json.JSONDecodeError as e:
                messagebox.showerror("Error", f"Invalid JSON format: {e}")
                return

            with open(fast_flags_file, 'w') as file:
                json.dump(current_flags, file, indent=4)
            messagebox.showinfo("Success", f"Successfully saved the fast flags in: {fast_flags_file}")
            view_edit_frame.destroy()  # Close the input window after successful input

        save_button = tk.Button(view_edit_frame, text="Save", command=save_flags)
        save_button.pack()

        view_edit_frame.mainloop()

    # Console menu for FastFlags editing
    while True:
        print("\n=== FastFlags Editor Menu ===")
        print("1. Import FastFlags from JSON file")
        print("2. Input FastFlags manually")
        print("3. View/Edit FastFlags")
        print("4. Save and Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == '1':
            imported_flags = import_fast_flags()
            if imported_flags:
                current_flags.update(remove_duplicates(imported_flags))
        elif choice == '2':
            input_fast_flags()
        elif choice == '3':
            view_edit_fast_flags()
        elif choice == '4':
            # Write the modified contents back to the file
            with open(fast_flags_file, 'w') as file:
                json.dump(current_flags, file, indent=4)
            print(f"Successfully edited the fast flags in: {fast_flags_file}")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 4.")

try:
    version_folder = find_latest_version_folder(roblox_versions_paths)
    print(f"Found latest version folder: {version_folder}")
    edit_fast_flags(version_folder)
except Exception as e:
    print(f"An error occurred: {e}")
