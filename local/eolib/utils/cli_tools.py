#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 15:42:22 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports


import os
import subprocess

from time import sleep


# ---------------------------------------------------------------------------------------------------------------------
#%% Define Classes

class Color(str):
    
    '''
    Class used to color terminal text. Example usage:
        print(Color("Hello").blue, Color("World").green.underline)
        
    When an object is called directly, it can also color other text:
        text = "yes" if True else "no"
        color_wrap = Color().green if True else Color().red
        print(color_wrap("  --> {}".format(text)))
        
    Note:
        This object can be buggy when used with other (normal) string objects!
        When used inside of "".join() functions, (and possibly other places), 
        this object will need to be wrapped with str(Color(...)) to function properly!
        Alternatively, adding '.str' to the end of the call will also work: Color(...).blue.bold.str    
    '''
    
    # Color/style codes from:
    # https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
    _color_lut = {"black": 0, "red": 1, "green": 2, "yellow": 3, "blue": 4, "purple": 5, "cyan": 6, "white": 7}
    _style_lut = {"none": 0, "bold": 1, "faint": 2, "italic": 3, "underline": 4, "blink": 5, "fast_blink": 6,
                  "invert": 7, "invisible": 8, "strikethru": 9, "double_underline": 21, "overline": 53}
    
    def __init__(self, text = ""):
        
        self._text = str(text)        
        self._styles = []
        self._fg_color = ""
        self._bg_color = ""
    
    def __repr__(self): return self._join_all()
    
    def __str__(self): return self._join_all()
    
    def __call__(self, text): 
        
        # Create a new color object and copy over styling/color info
        new_color_obj = Color(text)
        new_color_obj._fg_color = self._fg_color
        new_color_obj._bg_color = self._bg_color
        new_color_obj._styles = self._styles.copy()
        
        return new_color_obj
    
    def __add__(self, value):
        self._text += value
        return self
    
    def _join_all(self):
        
        prefix_strs = [*self._styles]
        if self._fg_color:
            prefix_strs += [self._fg_color]
        if self._bg_color:
            prefix_strs += [self._bg_color]
        prefix_code = ";".join(prefix_strs)
        complete_prefix_str = "\033[{}m".format(prefix_code)
        suffix_str = "\033[0m"
        full_str = "".join([complete_prefix_str, self._text, suffix_str])
        
        return full_str
    
    @property
    def str(self): return str(self)
    
    # .................................................................................................................
    # Foreground colors
    
    @property
    def black(self): return self._change_fg_color("black")
    
    @property
    def red(self): return self._change_fg_color("red")
    
    @property
    def green(self): return self._change_fg_color("green")
    
    @property
    def yellow(self): return self._change_fg_color("yellow")
    
    @property
    def blue(self): return self._change_fg_color("blue")
    
    @property
    def purple(self): return self._change_fg_color("purple")
    
    @property
    def cyan(self): return self._change_fg_color("cyan")
    
    @property
    def white(self): return self._change_fg_color("white")
    
    # .................................................................................................................
    # Background colors
    
    @property
    def black_bg(self): return self._change_bg_color("black")
    
    @property
    def red_bg(self): return self._change_bg_color("red")
    
    @property
    def green_bg(self): return self._change_bg_color("green")
    
    @property
    def yellow_bg(self): return self._change_bg_color("yellow")
    
    @property
    def blue_bg(self): return self._change_bg_color("blue")
    
    @property
    def purple_bg(self): return self._change_bg_color("purple")
    
    @property
    def cyan_bg(self): return self._change_bg_color("cyan")
    
    @property
    def white_bg(self): return self._change_bg_color("white")
    
    # .................................................................................................................
    # Styles  
    
    @property
    def bold(self): return self._add_style("bold")
    
    @property
    def faint(self): return self._add_style("faint")
    
    @property
    def italic(self): return self._add_style("italic")
    
    @property
    def underline(self): return self._add_style("underline")
    
    @property
    def blink(self): return self._add_style("blink")
    
    @property
    def invert(self): return self._add_style("invert")
    
    @property
    def strikethru(self): return self._add_style("strikethru")
    
    @property
    def double_underline(self): return self._add_style("double_underline")
    
    @property
    def overline(self): return self._add_style("overline")
    
    # .................................................................................................................
    # Helper functions
    
    def _set_prefix(self, prefix_list):
        self._prefix = prefix_list
        return self
    
    def _add_prefix(self, new_prefix):
        self._prefix.append(new_prefix)
        return self
    
    def _change_fg_color(self, new_fg_color_str):
        lowered_str = new_fg_color_str.lower()
        if lowered_str not in self._color_lut:
            raise AttributeError("Not a valid foreground color! ({})".format(lowered_str))
        color_code = self._color_lut.get(lowered_str)
        fg_color_str = "3{}".format(color_code)
        self._fg_color = fg_color_str
        return self
        
    def _change_bg_color(self, new_bg_color_str):
        lowered_str = new_bg_color_str.lower()
        if lowered_str not in self._color_lut:
            raise AttributeError("Not a valid background color! ({})".format(lowered_str))
        color_code = self._color_lut.get(lowered_str)
        bg_color_str = "4{}".format(color_code)
        self._bg_color = bg_color_str
        return self
    
    def _add_style(self, style_str):
        lowered_str = style_str.lower()
        if lowered_str not in self._style_lut:
            raise AttributeError("Not a valid style! ({})".format(lowered_str))
        self._styles.append(str(self._style_lut.get(lowered_str)))
        return self


# ---------------------------------------------------------------------------------------------------------------------
#%% Define Functions

#Color(text).bold().blue()

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

def keyboard_quit(function_to_cancel):
    
    ''' Decorator used to add keyboard-quit (ctrl + c) to functions '''
    
    def cancellable(*args, **kwargs):
        
        try:
            return function_to_cancel(*args, **kwargs)
        except KeyboardInterrupt:
            print("", "", "Keyboard cancel!", "", sep = "\n")
            _safe_quit()
    
    return cancellable

# .....................................................................................................................

def clean_error_quit(function_to_quit):
    
    ''' Decorator used to quit functions with cleaner error messages (beware, buries Traceback!)'''
    
    def quittable(*args, **kwargs):
        
        try:
            return function_to_quit(*args, **kwargs)
        except Exception as err_msg:
            print("", err_msg, "", sep = "\n")
            _safe_quit()
    
    return quittable

# .....................................................................................................................

def loop_on_index_error(function_to_loop):
    
    ''' Decorator used to re-evaluate a function if an IndexError occurs '''
    
    def looping_function(*args, **kwargs):
        
        while True:
            try:
                return_value = function_to_loop(*args, **kwargs)
                break
            except IndexError as err_msg:
                print("", err_msg, "", sep = "\n")
        
        return return_value
    
    return looping_function

# .....................................................................................................................

def loop_on_name_error(function_to_loop):
    
    ''' Decorator used to re-evaluate a function if a NameError occurs '''
    
    def looping_function(*args, **kwargs):
        
        while True:
            try:
                return_value = function_to_loop(*args, **kwargs)
                break
            except NameError as err_msg:
                print("", err_msg, "", sep = "\n")
        
        return return_value
    
    return looping_function

# .....................................................................................................................

def loop_on_value_error(function_to_loop):
    
    ''' Decorator used to re-evaluate a function if a ValueError occurs '''
    
    def looping_function(*args, **kwargs):
        
        while True:
            try:
                return_value = function_to_loop(*args, **kwargs)
                break
            except ValueError as err_msg:
                print("", err_msg, "", sep = "\n")
        
        return return_value
    
    return looping_function

# .....................................................................................................................

def clear_terminal(pre_delay_sec = 0, post_delay_sec = 0):
    
    # Wait before clearing (useful if some message is present)
    if pre_delay_sec > 0: 
        sleep(pre_delay_sec)
    
    # Try to clear the screen in a way that works on all operating systems
    clear_worked = False
    try:
        subprocess.run("clear")
        clear_worked = True
    except:
        pass
    
    # Clearing can fail on Windows, so try another clear command if needed
    if not clear_worked:
        try:
            subprocess.run("cls")
        except:
            pass
    
    # Wait after clearing (useful to prevent accidental inputs if the user isn't expecting the screen to clear)
    if post_delay_sec > 0: 
        sleep(post_delay_sec)

# .....................................................................................................................

def cli_select_from_list(entry_list, 
                         prompt_heading = "Select entry:",
                         default_selection = None, 
                         prepend_newline = True, 
                         zero_indexed = False,
                         default_indicator = "(default)",
                         clear_text = False,
                         debug_mode = False):
    
    '''
    Function used to provided a numerically indexed menu to allow a user to select entries from a list
    Inputs:
        entry_list -> List. Entries which will be printed out as a numerically indexed menu
        
        prompt_heading -> String. Heading which is printed above selection listing 
        
        default_selection -> String or None. If a string is provided and matches one of the list entries,
                             that entry will appear with a default indicator and will be 
                             automatically chosen if the user does not specify their selection.
        
        prepend_newline -> Boolean. If true, a newline will be printed out before the prompt heading
        
        zero_indexed -> Boolean. If true, the menu starts indexing at 0, otherwise it starts with 1
        
        default_indicator -> String. String concatenated onto default selection entry (if present)
        
        clear_text -> Boolean. If true, a 'clear' command will be sent to the terminal before printing
        
        debug_mode -> Boolean. If true, and a valid default selection is provided, the regular prompt 
                      and menu will print out, but the (default) selection will be made automatically,
                      with no user input.
    
    Outputs:
        selected_index, selected_entry
        
    *** Error cases ***:
        - ValueError occurs if a user makes no selection and a default selection isn't provided
        - IndexError occurs if a selection is made which isn't in the list
        - NameError occurs if the user enters anything that can't be interpretted as a number
    '''
    
    # Set default outputs
    selected_index = None
    selected_entry = None
    
    # Build the top part of the prompt message
    prompt_msg = []
    prompt_msg += [""] if prepend_newline else []
    prompt_msg += [Color(prompt_heading).bold.underline.str]
    prompt_msg += [""]
    
    # Use only entry as default if the entry list contains only 1 entry
    default_selection = entry_list[0] if len(entry_list) == 1 else default_selection
    index_offset = 1 - int(zero_indexed)
    
    # Build entry list part of the prompt message
    default_index = None
    for idx, each_entry in enumerate(entry_list):
        # Build the entry list by adding numbers to each entry as well as a default indicator if present
        file_string = "  {} - {}".format(index_offset + idx, each_entry)
        if each_entry == default_selection:
            file_string += " >> {}".format(Color(default_indicator).yellow)
            default_index = (index_offset + idx)
        prompt_msg += [file_string]
    
    # Clear the text if needed
    if clear_text:
        clear_terminal()
    
    # Print out selection entries and prompt user for input (or skip and use default in debug mode)
    print("\n".join(prompt_msg))
    user_response = input("Selection: ").strip() if not debug_mode else str(default_index)
    
    # If there is no user response (i.e. empty) assume a default entry, if present
    if not user_response:
        if default_index is None:
            raise ValueError("Not a valid selection! (No default available)")
        user_response = str(default_index)
        
    # If response is a number, check if it's in the list (if so, that's our selection!)
    if user_response.isdigit(): 
        user_response_int = int(user_response)
        user_index_selection = user_response_int - index_offset
        if user_index_selection < len(entry_list):
            selected_index = user_index_selection
            selected_entry = entry_list[selected_index]
        else:
            raise IndexError("Selection ({}) is not in the entry list!".format(user_response_int))
            
    else:
        # User entered something other than a digit so raise an error
        raise NameError("Expecting a number. Got: {}".format(user_response))
    
    # Print selection name for clarity
    print(Color("  --> {}".format(selected_entry)).cyan.bold.italic)
        
    return selected_index, selected_entry

# .....................................................................................................................

def cli_file_list_select(search_path, 
                         default_selection = None,
                         extra_entries = [],
                         show_file_ext = True,
                         show_hidden_files = False,
                         prompt_heading = "Select a file:",
                         prepend_newline = True, 
                         zeroth_entry_text = None,
                         clear_text = False,
                         debug_mode = False):
    
    '''
    Function for selecting from a list of files in a given folder, using a numerically index list.
    Inputs:
        search_path -> String. Folder path containing files to be listed
        
        default_selection -> String or None. If a string is provided and matches one of the list entries,
                             that entry will appear with a default indicator and will be 
                             automatically chosen if the user does not specify their selection.
        
        extra_entries -> List. Extra entries to append to the displayed selection listing
        
        show_file_ext -> Boolean. Show/hide file extensions (.json, .jpg etc.)
        
        show_hidden_files -> Boolean. Shown/hide files that begin with a "."
        
        prompt_heading -> String. Heading which is printed above selection listing
        
        prepend_newline -> Boolean. If true, a newline will be printed out before the prompt heading
        
        zeroth_entry_text -> String or None. If a string is provided, a zeroth entry will appear
                             on the file select listing (which normally starts at index 1)
                            
        clear_text -> Boolean. If true, a 'clear' command will be sent to the terminal before printing
                            
        debug_mode -> Boolean. If true, and a valid default selection is provided, the regular prompt 
                      and menu will print out, but the (default) selection will be made automatically,
                      with no user input.
    
    Outputs:
        full_path, selected_name, selected_index
        
    *** Error cases ***:
        - ValueError occurs if a user makes no selection and a default selection isn't provided
        - IndexError occurs if a selection is made which isn't in the list
        - NameError occurs if the user enters anything that can't be interpretted as a number
    '''
    
    # Add creation entry, if provided
    zero_entry_enabled = zeroth_entry_text is not None
    entry_list = [zeroth_entry_text] if zero_entry_enabled else []

    # Take out only the files from the list of items in the search folder
    entry_list += sorted([each_entry for each_entry in os.listdir(search_path) 
                        if os.path.isfile(os.path.join(search_path, each_entry))])
    
    # Remove hidden files if desired
    if not show_hidden_files:
        entry_list = [each_file for each_file in entry_list if each_file[0] != "."]
    
    # Add any extra entries (to the bottom of the list)
    entry_list += extra_entries
    
    # Create full file paths for later use
    entry_path_list = [os.path.join(search_path, each_file) for each_file in entry_list]
    
    # Remove file extensions if needed
    if not show_file_ext:
        entry_list = [os.path.splitext(each_file)[0] for each_file in entry_list]
    
    # Have the user select from the file list
    selected_index, entry_select = cli_select_from_list(entry_list,
                                                        prompt_heading,
                                                        default_selection,
                                                        prepend_newline,
                                                        zero_indexed = zero_entry_enabled,
                                                        clear_text = clear_text,
                                                        debug_mode = debug_mode)
    
    # Build outputs
    full_path = entry_path_list[selected_index]
    selected_name = entry_list[selected_index]
        
    return full_path, selected_name, selected_index

# .....................................................................................................................

def cli_folder_list_select(search_path, 
                           default_selection = None,
                           extra_entries = [],
                           show_hidden_folders = False,
                           prompt_heading = "Select a folder:",
                           prepend_newline = True, 
                           zeroth_entry_text = None,
                           clear_text = False,
                           debug_mode = False):
    
    '''
    Function for selecting from a list of folders within a given folder, using a numerically index list.
    Inputs:
        search_path -> String. Folder path containing folders to be listed
        
        default_selection -> String or None. If a string is provided and matches one of the list entries,
                             that entry will appear with a default indicator and will be 
                             automatically chosen if the user does not specify their selection.
        
        extra_entries -> List. Extra entries to append to the displayed selection listing
        
        show_hidden_folders -> Boolean. Shown/hide folders that begin with a "."
        
        prompt_heading -> String. Heading which is printed above selection listing
        
        prepend_newline -> Boolean. If true, a newline will be printed out before the prompt heading
        
        zeroth_entry_text -> String or None. If a string is provided, a zeroth entry will appear
                             on the folder select listing (which normally starts at index 1)
                            
        clear_text -> Boolean. If true, a 'clear' command will be sent to the terminal before printing
                            
        debug_mode -> Boolean. If true, and a valid default selection is provided, the regular prompt 
                      and menu will print out, but the (default) selection will be made automatically,
                      with no user input.
    
    Outputs:
        full_path, selected_name, selected_index
        
    *** Error cases ***:
        - ValueError occurs if a user makes no selection and a default selection isn't provided
        - IndexError occurs if a selection is made which isn't in the list
        - NameError occurs if the user enters anything that can't be interpretted as a number
    '''
    
    # Add creation entry, if provided
    zero_entry_enabled = zeroth_entry_text is not None
    entry_list = [zeroth_entry_text] if zero_entry_enabled else []

    # Take out only the folders from the list of items in the search folder
    entry_list += sorted([each_entry for each_entry in os.listdir(search_path) 
                          if os.path.isdir(os.path.join(search_path, each_entry))])
    
    # Remove hidden folders if desired
    if not show_hidden_folders:
        entry_list = [each_folder for each_folder in entry_list if each_folder[0] != "."]
    
    # Add any extra entries (to the bottom of the list)
    entry_list += extra_entries
    
    # Create full folder paths for later use
    entry_path_list = [os.path.join(search_path, each_file) for each_file in entry_list]
    
    # Have the user select from the folder list
    selected_index, entry_select = cli_select_from_list(entry_list,
                                                        prompt_heading,
                                                        default_selection,
                                                        prepend_newline,
                                                        zero_indexed = zero_entry_enabled,
                                                        clear_text = clear_text,
                                                        debug_mode = debug_mode)
    
    # Build outputs
    full_path = entry_path_list[selected_index]
    selected_name = entry_list[selected_index]
        
    return full_path, selected_name, selected_index
        
# .....................................................................................................................
     
def cli_prompt_with_defaults(prompt_message, 
                             default_value = None, 
                             return_type = None,
                             response_on_newline = False,
                             prepend_newline = True,
                             align_default_with_input = True,
                             debug_mode = False):
    
    '''
    Function which provides a input prompt with a default value.
    Inputs:
        prompt_message -> String. Message printed as a prompt to the user
        
        default_value -> Any type. Value returned if the user does not enter anything
        
        return_type -> Type. If not None, the user response will be cast to this type (ex. int, float, str)
        
        response_on_newline -> Boolean. If true, the users response will appear on the next line, below the prompt
        
        prepend_newline -> Boolean. If true, a newline will be printed out before the prompt
        
        align_default_with_input -> Boolean. If true, a default indicator will be printed out above the
                                    user input area, such that it can be aligned with the user's input
                                    (may need to add spaces to prompt message to get exact alignment)
                                    
        debug_mode -> Boolean. If true, the default value will be entered automatically, with no user input.
        
    Output:
        user_response
    '''
    
    # Modify prompt message, if using defaults to make things look as nice as possible (hopefully!)
    default_msg = ""
    if default_value is not None:
        
        # Set (colorful!) default message
        default_msg = Color("(default: {})\n".format(default_value)).yellow.faint.str
        
        # Add colon & space to line up with default message
        check_prompt = prompt_message.rstrip()
        prompt_has_colon = (check_prompt[-1] == ":")
        prompt_message = check_prompt + " " if prompt_has_colon else check_prompt + ": "
    
    # Set up helper add-ons
    prefix_1 = "\n" if prepend_newline else ""
    suffix_1 = "\n" if response_on_newline else ""
    
    # Modify default text to line up with user input (if desired)
    if align_default_with_input:
        
        # Don't bother with alignment if a default value isn't even given or the user enters on a newline
        if (default_value is not None) and (not response_on_newline):
            shift_length = len(prompt_message) - len("(default: ")
            default_shift = max(0, shift_length)
            prompt_shift = max(0, -shift_length)
            default_msg = " " * default_shift + default_msg
            prompt_message = " " * prompt_shift + prompt_message
    
    # Build full message string
    full_message = "".join([prefix_1, default_msg, prompt_message, suffix_1])

    # Get user input or use default if nothing is provided (or skip prompt and use default in debug mode)
    user_response = input(full_message).strip() if not debug_mode else default_value
    user_selected_default = (user_response == "")
    if user_selected_default:
        user_response = default_value
        
    # Convert response in function for convenience (if desired!)
    if return_type is not None:
            user_response = return_type(user_response) if user_response is not None else None
        
    # Print default response for clarity
    if user_selected_default and (user_response is not None):
        default_selection_str = "--> {}".format(user_response)
        final_shift = max(0, prompt_message.index(":") - len("--> ") + 2)
        shifted_str = " " * final_shift + default_selection_str
        print(Color(shifted_str).cyan.bold.italic)
        
    return user_response

# .....................................................................................................................

def cli_confirm(confirm_text, 
                default_response = True, 
                true_indicator = "y",
                false_indicator = "n",
                append_default_indicator = True, 
                response_on_newline = False,
                prepend_newline = True,
                echo_selection = True,
                debug_mode = False):
    
    '''
    Function for providing a yes/no prompt with a default response
    Inputs:
        confirm_text -> String. Text to be printed out, asking for user confirmation
        
        default_response -> Boolean. If the user does not enter a value, the default will be chosen
        
        true_indicator -> String. Indicator for how the user enters yes/True
        
        false_indicator -> String. Indicator for the user enters no/False
        
        append_default_indicator -> Boolean. If true, the true/false indicators will be appended to the 
                                    provided confirm_text. Both entries will be in parenthesis, with the
                                    default response being surrounded by square brackets.
                                    For example "Confirm? ([y]/n)"
                                    
        response_on_newline -> Boolean. If true, the users response will appear on the next line, below the prompt
        
        prepend_newline -> Boolean. If true, a newline will be printed out before the prompt
        
        echo_selection -> Boolean. If true, the selected result will be printed underneath the prompt
        
        debug_mode -> Boolean. If true, the default response will be made automatically, with no user input.
    '''
    
    # Set up convenient prompt add-ons
    prefix_1 = "\n" if prepend_newline else ""
    true_default_indicator = " ([{}]/{}) ".format(true_indicator, false_indicator)
    false_default_indicator = " ({}/[{}]) ".format(true_indicator, false_indicator)
    default_indicator = true_default_indicator if default_response else false_default_indicator
    suffix_1 = default_indicator if append_default_indicator else ""
    suffix_2 = "\n" if response_on_newline else ""
    
    # Build full display message
    full_message = "".join([prefix_1, confirm_text, suffix_1, suffix_2])
    
    # Update confirmation based on user input (or skip prompt and use default to speed things up in debug mode!)
    clean_response_func = lambda response: response.strip().lower()
    debug_response = clean_response_func(true_indicator if default_response else false_indicator)
    user_response = clean_response_func(input(full_message)) if not debug_mode else debug_response
    confirm_response = default_response
    if default_response:
        if user_response == clean_response_func(false_indicator):
            confirm_response = False
    else:
        if user_response == clean_response_func(true_indicator):
            confirm_response = True
    
    # Print selection for clarity
    if echo_selection:
        print_result = true_indicator if confirm_response else false_indicator
        color_wrap = Color().green.bold.italic if confirm_response else Color().red.bold.italic
        full_str = "  --> {}".format(print_result)
        print(color_wrap(full_str))
    
    return confirm_response

# .....................................................................................................................

# ---------------------------------------------------------------------------------------------------------------------
#%% RANGER functions

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
    from shutil import which
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

def ranger_file_select(start_dir = "~/Desktop", temp_file_path = "~/choosefile_ranger"):
    
    # First make sure ranger exists, before trying to use it for file selection!
    if not ranger_exists():
        ranger_missing_message(quit_after_message = True)
        
    import subprocess
        
    # Build actual pathing
    launch_path = os.path.expanduser(start_dir)
    launch_path = launch_path if os.path.exists(launch_path) else "/"
    choosefile_path = os.path.expanduser(temp_file_path)
    
    # Run ranger
    run_commands = ["ranger", launch_path, "--choosefile", choosefile_path]
    subprocess.run(run_commands)
    
    # Make sure the choosefile is there so we can read it
    if not os.path.exists(choosefile_path):
        raise FileNotFoundError("RANGER ERROR: missing choosefile")
    
    # Read the path in choosefile and then delete the choosefile itself!
    with open(choosefile_path, "r") as in_file:
        selected_file_path = in_file.read()
    os.remove(choosefile_path)
    
    # Make sure the selected file path is valid
    if not os.path.exists(selected_file_path):
        raise FileNotFoundError("RANGER ERROR: selected file path is invalid ({})".format(selected_file_path))
    
    return selected_file_path

# .....................................................................................................................
    
def ranger_multifile_select(start_dir = "~/Desktop", temp_file_path = "~/choosefiles_ranger", sort_output = True):
    
    # First make sure ranger exists, before trying to use it for file selection!
    if not ranger_exists():
        ranger_missing_message(quit_after_message = True)
        
    import subprocess
        
    # Build actual pathing
    launch_path = os.path.expanduser(start_dir)
    choosefile_path = os.path.expanduser(temp_file_path)
    
    # Run ranger
    run_commands = ["ranger", launch_path, "--choosefiles", choosefile_path]
    subprocess.run(run_commands)
    
    # Make sure the choosefile is there so we can read it
    if not os.path.exists(choosefile_path):
        raise FileNotFoundError("RANGER ERROR: missing choosefile")
    
    # Read the path in choosefile and then delete the choosefile itself!
    with open(choosefile_path, "r") as in_file:
        select_file_paths_str = in_file.read()
        selected_file_paths_list = sorted(select_file_paths_str.splitlines())
    os.remove(choosefile_path)
    
    # Make sure the selected file path is valid
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
    
    subprocess.run("cls")
    
    # Test cli select from lists
    '''
    desktop_path = os.path.expanduser("~/Desktop")
    a,b,c = cli_file_list_select(desktop_path)    
    x,y,z = cli_folder_list_select(desktop_path)
    '''
    
    # Example of colored text
    reg = Color().green
    print(reg("Hello"), Color("world").black.red_bg.double_underline)
    
    # Problems with using Color and join!
    print(" ".join([Color("ABC").green, Color("XYZ").red.str]))
    
    # Text cli prompts
    cli_prompt_with_defaults("Please enter a float", default_value= 123.456)
    cli_prompt_with_defaults("Good", default_value = "yes")
    
    # Test cli confirm
    cli_confirm("True or not?", default_response = True, true_indicator = "Correct")

# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap

