#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 10:07:25 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports

import os

from time import sleep

from shutil import which

from subprocess import run as subproc_run

from tempfile import TemporaryDirectory


# ---------------------------------------------------------------------------------------------------------------------
#%% Define Classes

# .....................................................................................................................

# .....................................................................................................................
# .....................................................................................................................

# ---------------------------------------------------------------------------------------------------------------------
#%% Define Functions

# .....................................................................................................................

def _using_spyder():
    return any(["spyder" in key.lower() for key in os.environ])

# .....................................................................................................................

def _safe_quit():
    # Handle special quitting case when using spyder ide
    if _using_spyder():
        raise SystemExit("Spyder-friendly quit")
    quit()

# .....................................................................................................................
    
def ranger_spyder_check():
    if _using_spyder():
        print("",
              "Can't run 'ranger' in spyder IDE!",
              "",
              "Quitting...", sep="\n")
        _safe_quit()

# .....................................................................................................................

def ranger_exists():
    ranger_spyder_check()
    return True if which("ranger") else False

# .....................................................................................................................

def ranger_missing_message(quit_after_message = True):
    
    print("",
          "Could not find program 'ranger'!",
          "To install on Ubuntu, use:",
          "  sudo apt install ranger",
          "",
          "Quitting...", sep="\n")
    
    if quit_after_message:
        _safe_quit()

# .....................................................................................................................

def ranger_file_select(start_dir = "~/Desktop"):
    
    # First make sure ranger exists, before trying to use it for file selection!
    if not ranger_exists():
        ranger_missing_message(quit_after_message = True)
    
    # Build actual pathing
    launch_path = os.path.expanduser(start_dir)
    launch_path = launch_path if os.path.exists(launch_path) else "/"
    
    # Create a temporary directory to store ranger outputs, so clean up is automatically taken care of...
    with TemporaryDirectory() as temp_dir_path:
        
        # Build path to temporary 'choosefile' for ranger to store selection results
        choosefile_path = os.path.join(temp_dir_path, "ranger_choosefile")
    
        # Run ranger
        run_commands = ["ranger", launch_path, "--choosefile", choosefile_path]
        subproc_run(run_commands)
        
        # Make sure the choosefile is there so we can read it
        if not os.path.exists(choosefile_path):
            print("", "File select cancelled!", "", sep = "\n")
            _safe_quit()

        # Read the path in choosefile
        with open(choosefile_path, "r") as in_file:
            selected_file_path = in_file.read()
    
    # Make sure the selected file path is valid
    if not os.path.exists(selected_file_path):
        raise FileNotFoundError("RANGER ERROR: selected file path is invalid ({})".format(selected_file_path))
    
    return selected_file_path

# .....................................................................................................................
    
def ranger_multifile_select(start_dir = "~/Desktop", sort_output = True):
    
    # First make sure ranger exists, before trying to use it for file selection!
    if not ranger_exists():
        ranger_missing_message(quit_after_message = True)
        
    # Build actual pathing
    launch_path = os.path.expanduser(start_dir)
    launch_path = launch_path if os.path.exists(launch_path) else "/"
    
    # Create a temporary directory to store ranger outputs, so clean up is automatically taken care of...
    with TemporaryDirectory() as temp_dir_path:
        
        # Build path to temporary 'choosefiles' for ranger to store selection results
        choosefiles_path = os.path.join(temp_dir_path, "ranger_choosefiles")
    
        # Run ranger
        run_commands = ["ranger", launch_path, "--choosefiles", choosefiles_path]
        subproc_run(run_commands)
        
        # Make sure the choosefile is there so we can read it
        if not os.path.exists(choosefiles_path):
            print("", "File select cancelled!", "", sep = "\n")
            _safe_quit()
        
        # Read the paths in the choosefile
        with open(choosefiles_path, "r") as in_file:
            select_file_paths_str = in_file.read()
            selected_file_paths_list = sorted(select_file_paths_str.splitlines())
    
    # Make sure the selected file paths are valid
    for each_path in selected_file_paths_list:
        if not os.path.exists(each_path):
            raise FileNotFoundError("RANGER ERROR: selected file path is invalid ({})".format(each_path))
            
    # Sort the output if needed
    if sort_output:
        selected_file_paths_list.sort()
    
    return selected_file_paths_list

# .....................................................................................................................

def ranger_preprompt(message_string = "Please use ranger cli to select a file", 
                     prepend_newline = True,
                     delay_before_input_sec = 0.5):
    
    ''' Function used to provide some context to the user before launching into ranger '''
    
    # Add empty line prior to message, if needed
    if prepend_newline:
        print("")
    
    # Print message with delay and input to block further execution without user input
    print(message_string)
    sleep(delay_before_input_sec)
    input("  Press Enter key to continue...")
    
    return
    
# .....................................................................................................................
# .....................................................................................................................    

# ---------------------------------------------------------------------------------------------------------------------
#%% Demo
    
if __name__ == "__main__":
    
    # Try ranger
    file_select = ranger_file_select()

# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap

