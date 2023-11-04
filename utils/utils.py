import logging
import tkinter as tk
from tkinter import filedialog

# @eel.expose
def select_folder():
    root = tk.Tk()
    root.attributes('-topmost', True)
    # root.iconify()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(parent=root,
                                    initialdir='~/')  # Open the folder dialog
    # root.destroy() # Destroy the root window when folder selected.
    return folder_path

if __name__ == '__main__':
    try:
        select_folder()
        # test()

    except Exception as e:
        print("Error: ", e)