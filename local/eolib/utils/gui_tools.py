#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 13:22:42 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports

import os

# ---------------------------------------------------------------------------------------------------------------------
#%% Define classes


# ---------------------------------------------------------------------------------------------------------------------
#%% Define functions

# .....................................................................................................................

def _safe_quit():
    # Handle special quitting case when using spyder ide
    using_spyder_ide = any(["spyder" in key.lower() for key in os.environ])
    if using_spyder_ide:
        raise SystemExit("Spyder quit (Keyboard interrupt)")
    quit()
    
# .....................................................................................................................

def _make_file_type_list(file_exts, file_exts_labels):
    
    # Make lists out of inputs (in case they aren't already!) for convenience
    file_ext_list = file_exts if type(file_exts) in {list, tuple} else [file_exts]
    file_ext_labels_list = file_exts_labels if type(file_exts_labels) in {list, tuple} else [file_exts_labels]
    
    # Build the file type selection
    if file_exts is None and file_exts_labels is None:
        # If no extenstions or file type names are given, just use all/*
        file_type_list = [["all", "*"]]
        
    elif file_exts is None:
        # If extension labels are given (e.g. 'video', 'image' etc.) but no extensions are provided
        file_type_list = [[each_ext_name, "*"] for each_ext_name in file_ext_labels_list]
        
    elif file_exts_labels is None:
        # If extensions are given, but not labels are provided
        file_type_list = [["File", each_ext] for each_ext in file_ext_list]
        
    else:
        # If both exts and labels are given, assume they are matched, so combine and display them
        file_type_list = [[each_label, each_ext] for each_label, each_ext in zip(file_exts_labels, file_ext_list)]

    return file_type_list

# .....................................................................................................................

def tkinter_exists():
    
    try:
        import tkinter
        root = tkinter.Tk()
        root.destroy()
        tk_exists = True
    except ImportError:
        tk_exists = False
    
    return tk_exists

# .....................................................................................................................

def tkinter_missing_message(quit_after_message = True):
    
    print("",
          "Could not find tkinter!",
          "To install on Ubuntu, use:",
          "  sudo apt install python3-tk",
          "",
          "Quitting...", sep="\n")
    
    if quit_after_message:
        _safe_quit()
    
# .....................................................................................................................

def gui_file_select(start_dir="~/Desktop", 
                    window_title="Select a file", 
                    file_exts_labels = None, 
                    file_exts = None,
                    quit_if_missing = True):
    
    # First make sure tkinter exists, before trying to use it!
    if not tkinter_exists():
        tkinter_missing_message(quit_after_message = True)
        
    import tkinter
    from tkinter import filedialog
    
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Ask user to select file
    start_dir = os.path.expanduser(start_dir)
    file_type_list = _make_file_type_list(file_exts, file_exts_labels)
    file_select = filedialog.askopenfilename(initialdir=start_dir, 
                                             title=window_title, 
                                             filetypes=file_type_list)
    file_select = file_select if file_select not in {None, ""} else None
    
    # Get rid of UI elements
    root.destroy()
    
    # If needed, quit when a file isn't selected
    if quit_if_missing and file_select is None:
        print("", "No file selection", "Quitting...", "", sep="\n")
        _safe_quit()
    return file_select

# .....................................................................................................................

def gui_file_select_many(start_dir="~/Desktop", 
                         window_title="Select file(s)", 
                         file_exts_labels = None, 
                         file_exts = None,
                         quit_if_missing = True):
    
    # First make sure tkinter exists, before trying to use it!
    if not tkinter_exists():
        tkinter_missing_message(quit_after_message = True)
        
    import tkinter
    from tkinter import filedialog
        
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Ask user to select file
    start_dir = os.path.expanduser(start_dir)
    file_type_list = _make_file_type_list(file_exts, file_exts_labels)
    file_select_list = filedialog.askopenfilenames(initialdir = start_dir, 
                                                   title = window_title, 
                                                   filetypes = file_type_list)
    file_select_list = file_select_list if len(file_select_list) > 0 else None
    
    # Get rid of UI elements
    root.destroy()
    
    # If needed, quit when files aren't selected
    if quit_if_missing and file_select_list is None:
        print("", "No file selection", "Quitting...", "", sep="\n")
        _safe_quit()    
    return file_select_list

# .....................................................................................................................
    
def gui_text_entry(prompt_message, 
                   window_title = "Input", 
                   default_value = None,
                   return_type = None,
                   quit_if_missing = True):
    
    # First make sure tkinter exists, before trying to use it!
    if not tkinter_exists():
        tkinter_missing_message(quit_after_message = True)
        
    import tkinter
    from tkinter import simpledialog
    
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Append default text, if a value was provided
    if default_value is not None:
        default_message = "\n(Default: {})".format(default_value)
        prompt_message += default_message
    
    # Get user entry (and clean it up)
    user_entry = simpledialog.askstring(window_title, prompt_message)
    user_entry = user_entry.strip() if type(user_entry) is str else user_entry
    user_entry = user_entry if user_entry not in {None, ""} else None
    
    # Get rid of UI elements
    root.destroy() 
    
    # Insert default value if present and user entered nothing
    if user_entry is None and default_value is not None:
        user_entry = default_value
    
    # If needed, quit when nothing is entered aren't selected
    if quit_if_missing and user_entry is None:
        print("", "No entry", "Quitting...", "", sep="\n")
        _safe_quit()
        
    # Apply return type conversion if needed before returning
    if return_type is not None:
        return return_type(user_entry)
    return user_entry

# .....................................................................................................................

def gui_confirm(confirm_text, windowTitle="Confirmation"):
    
    # First make sure tkinter exists, before trying to use it!
    if not tkinter_exists():
        tkinter_missing_message(quit_after_message = True)
        
    import tkinter
    from tkinter import messagebox
    
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    # Get user response
    userResponse = messagebox.askyesno(windowTitle, confirm_text)
    
    # Get rid of UI elements
    root.destroy()    
    
    return userResponse

# .....................................................................................................................

def gui_save(start_dir="~/Desktop", 
             window_title="Save file", 
             file_exts_labels = None, 
             file_exts = None,
             quit_if_missing = True):
    
    # First make sure tkinter exists, before trying to use it!
    if not tkinter_exists():
        tkinter_missing_message(quit_after_message = True)
        
    import tkinter
    from tkinter import filedialog
        
    # UI: Hide main window
    root = tkinter.Tk()
    root.withdraw()
    
    
    # Ask user to select file
    start_dir = os.path.expanduser(start_dir)
    file_type_list = _make_file_type_list(file_exts, file_exts_labels)
    file_save_path = filedialog.asksaveasfilename(initialdir = start_dir, 
                                                  title = window_title, 
                                                  filetypes = file_type_list)
    file_save_path = file_save_path if file_save_path not in {None, ""} else None
    
    # Get rid of UI elements
    root.destroy()    
    
    # If needed, quit when a save file isn't specified
    if quit_if_missing and file_save_path is None:
        print("", "No save path provided", "Quitting...", "", sep="\n")
        _safe_quit()
    
    return file_save_path

# .....................................................................................................................
# .....................................................................................................................

# ---------------------------------------------------------------------------------------------------------------------
#%% Demo
    
if __name__ == "__main__":
    pass


# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap


