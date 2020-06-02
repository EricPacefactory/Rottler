#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 31 15:42:22 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports


import os
import datetime as dt

from subprocess import run as subproc_run

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


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


class Datetime_Input_Parser:
    
    # Store date & time separator characters
    date_separator = "/"
    time_separator = ":"
    date_time_separator = " "
    
    # Store datetime string formatting codes
    date_format = "%Y/%m/%d"
    time_format = "%H:%M:%S"
    datetime_format = "%Y/%m/%d %H:%M:%S"
    
    # .................................................................................................................
    
    def __init__(self):
        class_name = self.__class__.__name__
        raise TypeError("This class isn't meant to be instantiated! ({})".format(class_name))
    
    # .................................................................................................................
    
    @classmethod
    def set_separators(cls, date_separator = "/", time_separator = ":", date_time_separator = " "):
        
        # Store updated separators
        cls.date_separator = date_separator
        cls.time_separator = time_separator
        cls.date_time_separator = date_time_separator
        
        # Re-build date/time formatting strings
        cls.date_format = "%Y{}%m{}%d".format(cls.date_separator, cls.date_separator)
        cls.time_format = "%H{}%M{}%S".format(cls.time_separator, cls.time_separator)
        cls.datetime_format = "{}{}{}".format(cls.date_format, cls.date_time_separator, cls.time_format)        

    # .................................................................................................................
    
    @classmethod
    def cli_prompt_start_end_datetimes(cls, bounding_start_dt, bounding_end_dt,
                                       start_dt_prompt = "Enter start time: ",
                                       end_dt_prompt = "  Enter end time: ",
                                       print_help_before_prompt = True,
                                       always_show_date = False,
                                       debug_mode = False):
        
        # Provide feedback if needed
        if print_help_before_prompt:
            cls.print_dt_str_input_help()
        
        # Round bounding times to nearest second, since user input only accepts seconds
        rounded_start_dt = bounding_start_dt.replace(microsecond = 0)
        rounded_end_dt = (bounding_end_dt + dt.timedelta(microseconds = 999999)).replace(microsecond = 0)
        
        # Decide how to display the default date/times
        different_dates = (rounded_start_dt.date() != rounded_end_dt.date())
        show_dates = (always_show_date or different_dates)
        default_display_format = cls.datetime_format if show_dates else cls.time_format
        
        # Provide user with start date/time prompt
        default_start_str = rounded_start_dt.strftime(default_display_format)
        start_str = cli_prompt_with_defaults(start_dt_prompt, default_start_str, debug_mode = debug_mode)
        
        # Provide user with end date/time prompt
        default_end_str = rounded_end_dt.strftime(default_display_format)
        end_str = cli_prompt_with_defaults(end_dt_prompt, default_end_str, debug_mode = debug_mode)
        
        # Parse user inputs to generate output datetimes
        user_start_dt, user_end_dt = cls.parse_user_datetimes(start_str, end_str, rounded_start_dt, rounded_end_dt)
        
        # Add timezone info back into results
        user_start_dt = user_start_dt.replace(tzinfo = rounded_start_dt.tzinfo)
        user_end_dt = user_end_dt.replace(tzinfo = rounded_end_dt.tzinfo)
        
        return user_start_dt, user_end_dt

    # .................................................................................................................

    @classmethod
    def parse_user_datetimes(cls, user_start_str, user_end_str, bounding_start_dt, bounding_end_dt):
        
        # Clean user inputs
        clean_start_str = user_start_str.strip()
        clean_end_str = user_end_str.strip()
        
        # Check if either time is using relative timing
        start_is_pos_relative = (clean_start_str[0] == "+")
        start_is_neg_relative = (clean_start_str[0] == "-")
        end_is_pos_relative = (clean_end_str[0] == "+")
        end_is_neg_relative = (clean_end_str[0] == "-")
        start_is_relative = (start_is_pos_relative or start_is_neg_relative)
        end_is_relative = (end_is_pos_relative or end_is_neg_relative)
        
        # Further cleaning to remove relative indicators
        abs_start_str = clean_start_str[1:] if start_is_relative else clean_start_str
        abs_end_str = clean_end_str[1:] if end_is_relative else clean_end_str
        
        # Split dates and times (if present)
        start_split_date_time = cls.split_date_and_time_strs(abs_start_str)
        end_split_date_time = cls.split_date_and_time_strs(abs_end_str)
        
        # Create initial absolute and delta times
        start_dt = bounding_start_dt
        end_dt = bounding_end_dt
        start_delta = dt.timedelta(0)
        end_delta = dt.timedelta(0)
        
        # Generate relative/absolute start times
        if start_is_relative:
            start_delta = cls.build_time_delta(*start_split_date_time)
        else:
            start_dt = cls.complete_missing_datetime(bounding_start_dt, *start_split_date_time)
            
        # Generate relative/absolute end times
        if end_is_relative:
            end_delta = cls.build_time_delta(*end_split_date_time)
        else:
            end_dt = cls.complete_missing_datetime(bounding_end_dt, *end_split_date_time)
        
        # Apply relative timing if needed (order of checks is important!)
        #   (+) start -> add to start bounding time
        #   (-) start -> subtract off end time
        #   (+) end -> add to start time
        #   (-) end -> subtract off end bounding time
        if end_is_neg_relative:
            end_dt = bounding_end_dt - end_delta
        if start_is_pos_relative:
            start_dt = bounding_start_dt + start_delta
        if start_is_neg_relative:
            start_dt = end_dt - start_delta
        if end_is_pos_relative:
            end_dt = start_dt + end_delta
        
        # Make sure we don't return a start dt ahead of the end dt!
        if end_dt < start_dt:
            same_dates = (start_dt.date() == end_dt.date())
            display_format = cls.time_format if same_dates else cls.datetime_format
            start_dt_str = start_dt.strftime(display_format)
            end_dt_str = end_dt.strftime(display_format)
            err_msg_list = ["The provided start time occurs after the provided end time!",
                            "                Start: {}".format(start_dt_str),
                            "                  End: {}".format(end_dt_str)]
            raise AttributeError("\n".join(err_msg_list))
        
        return start_dt, end_dt

    # .................................................................................................................

    @classmethod
    def split_date_and_time_strs(cls, datetime_str):
        
        '''
        Helper function which takes in a date/time/datetime string and outputs the date and time components separately
        If a date/time isn't present, the function will output None.
        
        Inputs:
            datetime_str: (String) -> A date or time or datetime string. 
                                      Dates should be in format YYYY/mm/dd
                                      Times should be in format HH:MM:SS
                                      If both date and time are present, they should be separated by a space
                                      (the date should always be first!)
                                  
        Outputs:
            output_date_str, output_time_str
        '''
        
        # Initialize outputs
        output_date_str = None
        output_time_str = None
        
        # Assume date and time are separated by a space (by default), so try to split by that
        clean_time_str = datetime_str.strip()
        split_date_time = clean_time_str.split(cls.date_time_separator)
        
        # Check if we have two entries (date & time), one entry (only date or time) or some other amount (not valid)
        num_entries = len(split_date_time)
        have_date_and_time = (num_entries == 2)
        have_date_or_time = (num_entries == 1)
        
        # Catch errors
        if not (have_date_and_time or have_date_or_time):
            raise AttributeError("Couldn't parse date and time from: {}".format(clean_time_str))
            
        # If only one entry is provided, we have to decide if it is time or date
        if have_date_or_time:
            is_date = (cls.date_separator in clean_time_str)
            output_date_str = clean_time_str if is_date else None
            output_time_str = None if is_date else clean_time_str
        
        # If both entries are provided, just split them
        if have_date_and_time:
            output_date_str, output_time_str = split_date_time
        
        return output_date_str, output_time_str

# .....................................................................................................................

    @classmethod
    def complete_missing_datetime(cls, base_datetime, date_str, time_str):
        
        # Break apart date and time strings into individual numbers we can use to build a datetime object
        num_years, num_months, num_days = cls.parse_dt_triplet_str(date_str, cls.date_separator)
        num_hours, num_minutes, num_seconds = cls.parse_dt_triplet_str(time_str, cls.time_separator)
        
        # Replace components that are non-None in absolute datetime
        replace_if_not_none = lambda replace, base: int(base if replace is None else replace)
        abs_year = replace_if_not_none(num_years, base_datetime.year)
        abs_month = replace_if_not_none(num_months, base_datetime.month)
        abs_day = replace_if_not_none(num_days, base_datetime.day)
        abs_hour = replace_if_not_none(num_hours, base_datetime.hour)
        abs_min = replace_if_not_none(num_minutes, base_datetime.minute)
        abs_sec = replace_if_not_none(num_seconds, base_datetime.second)
        
        # Build absolute datetime
        absolute_datetime = dt.datetime(year = abs_year, month = abs_month, day = abs_day,
                                        hour = abs_hour, minute = abs_min, second = abs_sec,
                                        tzinfo = base_datetime.tzinfo)
        
        return absolute_datetime

    # .................................................................................................................

    @classmethod
    def build_time_delta(cls, date_str, time_str):
        
        # Break apart date and time strings into individual numbers we can use to build a timedelta object
        num_years, num_months, num_days = cls.parse_dt_triplet_str(date_str, cls.date_separator)
        num_hours, num_minutes, num_seconds = cls.parse_dt_triplet_str(time_str, cls.time_separator)
        
        # Create all the timedelta components (use a value of zero if not provided)
        use_zero_if_none = lambda value: 0 if value is None else value
        del_years = use_zero_if_none(num_years)
        del_months = use_zero_if_none(num_months)
        del_days = use_zero_if_none(num_days)
        del_hours = use_zero_if_none(num_hours)
        del_minutes = use_zero_if_none(num_minutes)
        del_seconds = use_zero_if_none(num_seconds)
        
        # Error if we get relative years/months, since these can be ambiguous
        have_months = (del_months > 0)
        have_years = (del_years > 0)
        if have_months:
            err_msg = "Can't specify relative months, since this can result in undefined dates! Use days instead."
            raise TypeError(err_msg)
        if have_years:
            err_msg = "Can't specify relative years, since this can result in undefined dates! Use days instead."
            raise TypeError(err_msg)
        
        # Build timedelta
        absolute_datetime = dt.timedelta(days = del_days, 
                                         hours = del_hours, minutes = del_minutes, seconds = del_seconds)
        
        return absolute_datetime

    # .................................................................................................................

    @classmethod
    def print_dt_str_input_help(cls):
        
        # Build an example datetime
        example_dt = dt.datetime.now()
        example_dt_str = example_dt.strftime(cls.datetime_format)
        
        print("", 
              "Times should be entered in the format:",
              "  {}".format(example_dt_str),
              "",
              "Any missing components (for example, the year or full date)",
              "will be replaced with the provided default value(s).",
              "",
              "Times can alternatively be entered as relative values by using",
              "a plus (+) or minus (-) sign in front of the time.",
              "",
              "Notes on relative times:",
              "  Plus  (+) start times will be interpretted relative to the default start time.",
              "  Minus (-) start times will be interpretted relative to the provided end time.",
              "  Plus  (+) end   times will be interpretted relative to the provided start time.",
              "  Minus (-) end   times will be interpretted relative to the default end time.", 
              "  Cannot use relative years or months!",
              sep = "\n")
        
        return


    # .................................................................................................................

    @staticmethod
    def parse_dt_triplet_str(date_or_time_str, entry_separator):
        
        # Initialize outputs
        entry_0 = None
        entry_1 = None
        entry_2 = None
        
        # Don't do anything in the case of non-inputs
        if date_or_time_str is None:
            return entry_0, entry_1, entry_2
        
        # Split date or time components apart 
        # ("2020/01/05" -> ["2020", "01", "05"], using entry_separator = "/")
        # ("15:04:22" -> ["15", "04", "22"]), using entry separator = ":")
        str_list = date_or_time_str.split(entry_separator)
        
        # Catch cases with weird number of entries
        num_entries = len(str_list)
        if num_entries not in {1, 2, 3}:
            raise AttributeError("Error splitting entries: {} with {}".format(date_or_time_str, entry_separator))
            
        # Handle different input cases manually
        if num_entries == 1:
            entry_2 = float(str_list[0])
        elif num_entries == 2:
            entry_1 = int(str_list[0])
            entry_2 = float(str_list[1])
        elif num_entries == 3:
            entry_0 = int(str_list[0])
            entry_1 = int(str_list[1])
            entry_2 = float(str_list[2])    
        
        return entry_0, entry_1, entry_2
    
    # .................................................................................................................
    
    @staticmethod
    def limit_start_end_range(start_dt, end_dt, max_timedelta_hours = 1,
                              return_same_end_dt = True):
        
        ''' Helper function which limits the time range between the given start and end times '''
        
        # Check if the start-to-end times exceed the max allowed range
        start_end_delta = (end_dt - start_dt)
        limited_timedelta = dt.timedelta(hours = max_timedelta_hours)
        need_to_limit = (start_end_delta > limited_timedelta)
        
        # If the times are already within limits, we're good!
        if not need_to_limit:
            return start_dt, end_dt
        
        # If we get here, the times exceed the max range, so decide how to fix things...
        if return_same_end_dt:
            limited_end_dt = end_dt
            limited_start_dt = end_dt - limited_timedelta
        else:
            limited_start_dt = start_dt
            limited_end_dt = start_dt + limited_timedelta
        
        return limited_start_dt, limited_end_dt
    
    # .................................................................................................................
    
    @classmethod
    def print_start_end_time_range(cls, selected_start_dt, selected_end_dt):
        
        '''
        Helper function which prints out a selected start/end datetime.
        Intended for use with the results from calling cli_prompt_start_end_datetimes(...) function
        '''
        
        # Convert datetimes to string format for printing
        start_dt_str = dt.datetime.strftime(selected_start_dt, cls.datetime_format)
        end_dt_str = dt.datetime.strftime(selected_end_dt, cls.datetime_format)
        
        # Print indicator of start/end timing
        print("",
              "--- Selected time range ---",
              "",
              "  {} (start)".format(start_dt_str),
              "  {} (end)".format(end_dt_str),
              sep = "\n")
        
        return

    # .................................................................................................................
    # .................................................................................................................

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
        subproc_run("clear")
        clear_worked = True
    except:
        pass
    
    # Clearing can fail on Windows, so try another clear command if needed
    if not clear_worked:
        try:
            subproc_run("cls")
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
# .....................................................................................................................


# ---------------------------------------------------------------------------------------------------------------------
#%% Datetime parsing functions

# ---------------------------------------------------------------------------------------------------------------------
#%% Demo
    
if __name__ == "__main__":
    
    clear_terminal()
    
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
    
    # Test datetime parser
    sdt = dt.datetime(2020, 3, 11, 11, 5, 0, 1)
    edt = dt.datetime(2020, 3, 11, 14, 0, 0, 1)
    start_dt, end_dt = Datetime_Input_Parser.cli_prompt_start_end_datetimes(sdt, edt)
    
    print(start_dt.strftime(Datetime_Input_Parser.datetime_format))
    print(end_dt.strftime(Datetime_Input_Parser.datetime_format))

# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap

