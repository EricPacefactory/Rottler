#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 16:04:54 2018

@author: eo

"""

import cv2
import numpy as np
from time import perf_counter

# ---------------------------------------------------------------------------------------------------------------------
#%% Define classes

class SimpleWindow:
    
    windowCount = 0
    
    def __init__(self, name=None, x=None, y=None, emptyWH = None, timelapse=1, enabled=True):
        
        # Store window name to use as a reference
        self._name = name if name is not None else "Frame - {}".format(self._updateCount())
        
        # Record timelapsing info
        self._timelapse = timelapse
        self._framecount = np.int32(-1)
        
        # Store initial x/y positions
        self._x = int(x) if x is not None else None
        self._y = int(y) if y is not None else None
        
        # Allocate storage for trackbar referencing
        self._trackbars = {}
        
        # Create and move the window, as long as this display is enabled
        if enabled:
            self._createWindow()
        
        else:
            # Blowout functions if this window is disabled
            def blankFunc(*args, **kwargs): return None
            
            # Delete functionality rather than including 'if(enabled):' in every function. Kind of hacky
            self.attachCallback = blankFunc
            self.move = blankFunc
            self.imshow = blankFunc
            self.addTrackbar = blankFunc
            self.readTrackbar = blankFunc
            self.reset = blankFunc
            self.restart = blankFunc
            self.close = blankFunc
            self.exists = blankFunc
            
        # Fill in initial empty image, if dimensions are provided
        if emptyWH:
            self.imshow(np.zeros((emptyWH[1], emptyWH[0], 3), dtype=np.uint8))
        
    # ................................................................................................................. 
        
    def attachCallback(self, mouse_callback, callback_data = {}):
        
        cv2.setMouseCallback(self._name, mouse_callback, callback_data)
       
    # ................................................................................................................. 
    
    def move(self, x, y):
        cv2.moveWindow(self._name, x, y)
        self._x = x
        self._y = y
        
    # ................................................................................................................. 
        
    def imshow(self, frame):
        
        # Check if the window exists (by looking for window properties)
        windowExists = self.exists()
        
        # Update frame count, used for timelapsing
        self._framecount += 1
        
        # Skip display update if timelapsing
        if (self._framecount % self._timelapse) != 0:
            return windowExists
        
        # Don't do anything if a valid frame isn't supplied
        if frame is None:
            return windowExists
        
        # Only update showing if the window exists
        if windowExists:
            cv2.imshow(self._name, frame)
        
        return windowExists
    
    # ................................................................................................................. 
    
    def addTrackbar(self, bar_name, start_value, max_value=100):
        
        maximum_value = int(max_value)
        starting_value = min(int(start_value), maximum_value)
        
        cv2.createTrackbar(bar_name, self._name, starting_value, maximum_value, lambda x: None)
        self._trackbars[bar_name] = starting_value
    
    # ................................................................................................................. 
    
    def readTrackbar(self, bar_name):
        
        # Get the trackbar value and check if it changed
        trackbar_value = cv2.getTrackbarPos(bar_name, self._name)
        trackbar_changed = self._trackbars[bar_name] != trackbar_value
        
        # Record the new (possible same) trackbar value
        self._trackbars[bar_name] = trackbar_value
        
        return trackbar_changed, trackbar_value
    
    # ................................................................................................................. 
    
    def setTrackbar(self, bar_name, bar_value, store_new_setting = True):
        cv2.setTrackbarPos(bar_name, self._name, bar_value)
        
        # Store the new value so we don't interpret it as a change on the next trackbar read
        if store_new_setting:
            self._trackbars[bar_name] = cv2.getTrackbarPos(bar_name, self._name)        
    
    # .................................................................................................................    
    
    def reset(self):
        self._createWindow()    # Similar to restart, but will re-position open windows as well
    
    # .................................................................................................................    
    
    def restart(self):
        if not self.exists(): self._createWindow()
    
    # .................................................................................................................    
    
    def close(self):
        if self.exists(): cv2.destroyWindow(self._name)
        
    # .................................................................................................................  
    
    def exists(self):
        return cv2.getWindowProperty(self._name, cv2.WND_PROP_AUTOSIZE) > 0
        #return cv2.getWindowProperty(self._name, cv2.WND_PROP_ASPECT_RATIO) > 0 # Doesn't work on mac
    
    # ................................................................................................................. 
    
    def _createWindow(self):
        
        # Create window
        cv2.namedWindow(self._name)#, flags = cv2.WINDOW_NORMAL)
            
        # Re-position the window if x/y positions are specified
        if (self._x is not None) and (self._y is not None):
            self.move(self._x, self._y)
                
    # ................................................................................................................. 
    
    @classmethod
    def _updateCount(cls):
        cls.windowCount +=1
        return cls.windowCount
        
      
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
        
class TimebarWindow(SimpleWindow):
    
    def __init__(self, name=None, x=None, y=None,  timelapse=1, enabled=True):
        
        super().__init__(name, x, y, timelapse, enabled)

        self._total_frames = None
        self._frame_idx = 0
        self.videoObj = None
        self._timebar_name = "Frame:"
        self._paused = False
        self._pause_frame = None
        self.keyPress = None
        
    # .................................................................................................................  
    
    def addTimebar(self, videoObj_ref, start_frame = 0):
        self._total_frames = int(videoObj_ref.get(cv2.CAP_PROP_FRAME_COUNT))
        cv2.createTrackbar(self._timebar_name, self._name, start_frame, self._total_frames, lambda x: None)
        
    # .................................................................................................................  
    
    def get_frame(self, videoObj_ref, frame_delay = 10, pause_delay = 10):
        
        # Set output defaults
        request_break = False
        request_continue = False
        new_frame = self._pause_frame        
        
        if self._paused:
            request_continue = True
            frame_delay = pause_delay
        else:
            (received_frame, new_frame) = videoObj_ref.read()
            request_break = not received_frame
            self._frame_idx = int(videoObj_ref.get(cv2.CAP_PROP_POS_FRAMES))
            cv2.setTrackbarPos(self._timebar_name, self._name, self._frame_idx)
            
        # Get basic keypresses
        break_by_key, self.keyPress = breakByKeypress(frame_delay)
        request_break |= break_by_key
        
        # Pause with spacebar
        if self.keyPress == 32:
            
            # Pause/unpause with spacebar
            self._paused = not self._paused
            
            # Store a copy of the current frame if we just paused
            if self._paused:
                self._pause_frame = new_frame.copy()
                request_continue = True
                
        # Skip forward/backward with +/- keys
        if self.keyPress == 45:
            vidFPS = videoObj_ref.get(cv2.CAP_PROP_FPS)
            backward_index = max(0, self._frame_idx - int(4*vidFPS))
            videoObj_ref.set(cv2.CAP_PROP_POS_FRAMES, backward_index)
            request_continue = True
        if self.keyPress == 61:
            vidFPS = videoObj_ref.get(cv2.CAP_PROP_FPS)
            forward_index = min(self._total_frames, self._frame_idx + int(4*vidFPS))
            videoObj_ref.set(cv2.CAP_PROP_POS_FRAMES, forward_index)
            request_continue = True
        
        return request_break, request_continue, new_frame
        
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
        
class Slider_Control:
    
    # ................................................................................................................. 
    
    def __init__(self, 
                 name = "Value",
                 initial_value = 0,
                 max_value = 100, 
                 slider_to_value_func = None,
                 value_to_slider_func = None,
                 window_reference = None):
        
        
        # Store custom slider-to-value mapping (if provided)
        self._slider_to_value_func = lambda x: x
        if slider_to_value_func is not None:
            self._slider_to_value_func = slider_to_value_func
        
        # Store custom value-to-slider mapping (if provided)
        self._value_to_slider_func = lambda x: x
        if value_to_slider_func is not None:
            self._value_to_slider_func = value_to_slider_func
            
        # Store useful slider variables
        self._name = name
        self._initial_slider_value = self._value_to_slider_func(initial_value)
        self._max_slider_value = self._value_to_slider_func(max_value)
        self._window_ref = window_reference
        
        # Set up value storage
        self._slider_value = self._initial_slider_value
        
        # Set window reference if provided
        self._update_window_ref(window_reference)
        
    # ................................................................................................................. 
        
    def trackbar_config(self, window_reference = None):   
        
        # Make sure the window reference is configured
        self._update_window_ref(window_reference)
        
        # Function for easily configuring a SimpleWindow (from eolib)        
        trackbar_config = {"bar_name": self._name,
                           "start_value": self._initial_slider_value,
                           "max_value": self._max_slider_value}
            
        return trackbar_config
    
    # ................................................................................................................. 
    
    def update_from_trackbar(self):
            
        # Assume the trackbar was set up with trackbar config
        val_changed, new_val = self._window_ref.readTrackbar(self._name)
        if val_changed:
            self._slider_value = new_val
            
        return val_changed
    
    # ................................................................................................................. 
    
    def update_slider_directly(self, new_slider_value):
        self._slider_value = new_slider_value
        
    # ................................................................................................................. 
    
    def update_value_directly(self, new_value):
        self.slider_value = self.value_to_slider_func(new_value)
    
    # ................................................................................................................. 
    
    def report_slider_value(self):
        return self._slider_value
    
    # ................................................................................................................. 
    
    def report(self):
        return self._slider_to_value_func(self._slider_value)
    
    # ................................................................................................................. 
    
    def _update_window_ref(self, window_reference = None):
        
        # Update window reference, if one is supplied
        if window_reference is not None:
            self._window_ref = window_reference
            
    # ................................................................................................................. 
    
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================


class Process_Timer:
    
    def __init__(self, frameWH = (500, 30), alpha = 0.95):
        
        # Create a blank image to draw in to        
        self._empty_frame = np.zeros((frameWH[1], frameWH[0], 3), dtype=np.uint8)
        
        # Allocate space for timing variables
        self._start_time = cv2.getTickCount()
        self._end_time = cv2.getTickCount()
        self.proc_time_sec = 0.0
        
        # Store averaging parameters
        self.alpha = max(min(1.0, alpha), 0.0)
        self._inv_alpha = 1 - self.alpha
        
        # Set up timing text aesthetics
        self.text_config = {"org": (10, 20),
                            "fontFace": cv2.FONT_HERSHEY_SIMPLEX,
                            "fontScale": 0.5,
                            "color": (200, 200, 200),
                            "thickness": 1,
                            "lineType": cv2.LINE_AA}
    
    # .................................................................................................................
    
    def configure_text(self, new_text_config):        
        self.text_config = {**self.text_config, **new_text_config}
    
    # .................................................................................................................
    
    def start(self):
        self._start_time = perf_counter()
    
    # .................................................................................................................
    
    def end(self):
        self._end_time = perf_counter()
        
        # Average the process time with previous timing
        self.proc_time_sec = self.alpha*self.proc_time_sec + self._inv_alpha*(self._end_time - self._start_time)
        
    # .................................................................................................................
    
    def draw(self):
        disp_frame = self._empty_frame.copy()
        timing_string = "Timing (ms): {:.3f}".format(1000*self.proc_time_sec)
        return cv2.putText(img = disp_frame, text = timing_string, **self.text_config)
    
    # .................................................................................................................

    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================


class Progress_Bar:
    
    # .................................................................................................................
    
    def __init__(self, total_iterations, 
                 window_label="Progress", 
                 bar_color = (85, 75, 7), 
                 bg_color = (20, 20, 20),
                 displayWH = (500, 80), 
                 barWH = (400, 40),
                 update_rate = 1,
                 center_on_start = True,
                 enable_display = True):
        
        # Store iteration variables
        self.current_iteration = 0
        self.total_iterations = total_iterations
        
        # Store other aesthetic variables
        self.window_label = window_label
        self.bar_color = bar_color
        self.displayWH = displayWH
        self.barWH = barWH
        self.update_rate = update_rate
        
        # Calculate the location/drawing points for the progress bar
        half_width = (displayWH[0] - barWH[0]) / 2
        half_height = (displayWH[1] - barWH[1]) / 2
        self.bar_tl = (int(half_width), int(half_height))
        self.bar_br = (int(half_width + barWH[0]), int(half_height + barWH[1]))
        
        # Create the initial empty image to draw in to
        self.base_image = np.full((displayWH[1], displayWH[0], 3), bg_color, dtype=np.uint8)
        
        # Finally, create progress bar window
        self.enable_display = enable_display
        if enable_display:
            self.prog_window = SimpleWindow(window_label)
            self.prog_window.imshow(self.base_image)
            
            # Center the progress bar (if desired)
            if center_on_start:
                center_window(self.prog_window, frameWH=displayWH)
    
    # .................................................................................................................
    
    def update(self, run_waitKey = True):
        
        # Auto increment the iterations
        self.current_iteration += 1
        
        # Don't do anything if there is no display
        if not self.enable_display:
            return True
        
        # Don't bother doing anything if the window doesn't exist
        if not self.prog_window.exists():
            return False
        
        # Only update the image based on the update rate (i.e. 'timelapsed')
        if (self.current_iteration % self.update_rate) == 0:
            frame_image = self._draw_progress_bar(self.base_image)
            final_image = self._draw_border(frame_image)
            self.prog_window.imshow(final_image)
            
            if run_waitKey:
                cv2.waitKey(1)
            
        return True
        
    # .................................................................................................................
    
    def _draw_progress_bar(self, in_image):
        progress_width = min((self.current_iteration / self.total_iterations), 1) * self.barWH[0]
        prog_draw_x = int(round(self.bar_tl[0] + progress_width))
        prog_br = (prog_draw_x, self.bar_br[1])
        return cv2.rectangle(in_image, self.bar_tl, prog_br, self.bar_color, -1, cv2.LINE_4)
    
    # .................................................................................................................
    
    def _draw_border(self, in_image):             
        return cv2.rectangle(in_image, self.bar_tl, self.bar_br, (200, 200, 200), 1, cv2.LINE_4)
    
    # .................................................................................................................
    
    # .................................................................................................................
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================

    
# ---------------------------------------------------------------------------------------------------------------------
#%% Define functions
    
def breakByKeypress(frame_delay=1, break_on_q = True, break_on_esc = True, break_on_enter = False):
    
    # Get keypress
    keyPress = cv2.waitKey(frame_delay) & 0xFF
    
    # Check for target key presses
    q_key_pressed = (keyPress == ord('q')) if break_on_q else False
    esc_key_pressed = (keyPress == 27) if break_on_esc else False
    break_key_pressed = (keyPress == 13) if break_on_enter else False
    
    # Check if q or Esc where pressed, in which return a signal to break execution loop
    requestBreak = q_key_pressed | esc_key_pressed | break_key_pressed
    
    return requestBreak, keyPress 

# .....................................................................................................................

def arrowKeys(keypress):
    
    # Key reference (on linux at least)
    # left arrow  = 81
    # up arrow    = 82
    # right arrow = 83
    # down arrow  = 84
    
    arrowPressed = (80 < keypress < 85)
    if arrowPressed:
        return (arrowPressed, (int(keypress == 83) - int(keypress == 81), int(keypress == 84) - int(keypress == 82)))
    else:
        return (arrowPressed, (0, 0))
    
# .....................................................................................................................
        
def plusminusKeys(keyPress):
    minus_pressed = (keyPress == 45) or (keyPress == 173)
    plus_pressed = (keyPress == 61) or (keyPress == 171)
    plusminusPressed = plus_pressed or minus_pressed
    return plusminusPressed, int(plus_pressed) - int(minus_pressed)

# .....................................................................................................................
    
def displayIsAvailable():
    
    import os
    # Assume we're not running headless if using windows
    if "nt" in os.name:
        return True
    
    # Linux/Mac check
    return "DISPLAY" in os.environ

# .....................................................................................................................

def displayDimensionsWH(verbose = True):
    
    # Figure out which operating system we're using so we can get the display dimensions correctly
    using_os = check_os()
    
    if using_os["linux"]:
        return _displayWH_linux(verbose)
    
    if using_os["mac"]:
        return _displayWH_mac(verbose)
    
    if using_os["windows"]:
        return _displayWH_windows(verbose)
    
    # If os checks fail, just return a standard resolution
    print("")
    print("Trying to set display dimensions...")
    print("  Operating system not recognized!")
    print("  Assuming display dimensions of 1280 x 720")
    return (1280, 720)

# .....................................................................................................................

def _displayWH_linux(verbose = True):
    
    import subprocess
    
    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    
    def extract_dimensions(dim_string, bound_left, bound_right):

        # Try to pick off a string of the format 'widthxheight'
        clean_string = dim_string.replace(" ", "")                                  # Get rid of spaces
        pixel_string = clean_string.split(bound_left)[1].split(bound_right)[0]      # Split by boundaries
        
        return [int(eachStrNum) for eachStrNum in pixel_string.split("x")]  # Convert dimension strings to integers
    
    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    # Try xdpyinfo, since it has a clear representation of the dimensions
    
    try:
        
        dimension_string = subprocess.check_output(["xdpyinfo | grep dimensions"], shell=True).decode()
        # Example return:
        # '  dimensions:    1920x1080 pixels (483x272 millimeters)\n'
        
        dimensions = extract_dimensions(dimension_string, 
                                        bound_left="dimensions:", 
                                        bound_right="pixels")
    # Ignore errors
    except Exception: pass
    
    # If no exception occurs, assume we got good dimensions
    else: return dimensions
    
    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    # Try using xrandr if xdpyinfo failed
    
    try:
        
        subprocess.check_output(["xrandr | grep ' connected'"], shell=True).decode()
        # Example return
        # 'HDMI-1 connected 1920x1080+0+0 (normal left inverted right x axis y axis) 480mm x 270mm\n'
        
        dimensions = extract_dimensions(dimension_string, 
                                        bound_left="connected:", 
                                        bound_right="+")
    # Ignore errors
    except Exception: pass    

    # If no exception occurs, assume we got good dimensions
    else: return dimensions
    
    # . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
    # Return an assumed default 
    
    dimensions = (1280, 720)
    if verbose:
        print("")
        print("Couldn't find screen dimensions! Using default: {} x {}".format(*dimensions))
    
    return dimensions

# .....................................................................................................................

def _displayWH_mac(verbose = True):
    if verbose:
        print("")
        print("Can't figure out display dimensions on mac...")
        print("  Assuming 1280 x 720")
    return (1280, 720)

# .....................................................................................................................

def _displayWH_windows(verbose = True):
    
    try:
        # Windows magic for getting screen size
        import ctypes
        user32 = ctypes.windll.user32
        
        # More magic
        disp_width = user32.GetSystemMetrics(0)
        disp_height= user32.GetSystemMetrics(1)
        dimensions = (disp_width, disp_height)
        
    except Exception as err:
        
        dimensions = (1280, 720)
        if verbose:
            print("")
            print("Error getting display dimensions:")
            print(err)
    
    return dimensions

# .....................................................................................................................
    
def arrange_windows(rows, cols, window_list, padding_tlbr = [20, 20, 20, 20]):
    
    # Get screen dimensions
    windowWH = displayDimensionsWH(verbose=False)
    
    # Try to figure out the padding settings
    try:
        if type(padding_tlbr) in [list, tuple]:
            pad_top = padding_tlbr[0]
            pad_left = padding_tlbr[1]
            pad_bot = padding_tlbr[2]
            pad_right = padding_tlbr[3]
        else:
            pad_top = padding_tlbr
            pad_left = padding_tlbr
            pad_bot = padding_tlbr
            pad_right = padding_tlbr
    except:
        pad_top = 0
        pad_left = 0
        pad_bot = 0
        pad_right = 0
    
    # Figure out how much horizontal and vertical space is available for tiling windows
    spaceW = windowWH[0] - pad_left - pad_right
    spaceH = windowWH[1] - pad_top - pad_bot
    
    # Build a list of (tiled) window xy positions
    xy_pos = []
    for row_idx in range(rows):        
        yy = pad_top + row_idx*(spaceH/rows)   
        
        for col_idx in range(cols):        
            xx = pad_left + col_idx*(spaceW/cols)            
            xy_pos.append((xx,yy))
    
    # Move each window onto tile position
    for idx, eachWindow in enumerate(window_list):
        if eachWindow:
            x_loc, y_loc = xy_pos[idx]
            eachWindow.move(x = int(x_loc), y = int(y_loc))

# .....................................................................................................................
        
def center_window(window_ref, frameWH = None, video_obj_ref = None, offsetXY = (0, 0)):
    
    # Make sure at least one source of frame dimensions is given
    if frameWH is None and video_obj_ref is None:
        print("")
        print("Warning:")
        print("  Can't center window {}, since no frame dimension reference was given!".format(window_ref._name))
        window_ref.move(x = offsetXY[0], y = offsetXY[1])
        return
    
    # Get screen dimensions
    windowWH = displayDimensionsWH(verbose=False)
    
    # Find the screen center point
    center_x = windowWH[0]/2
    center_y = windowWH[1]/2
    
    # If a video capture object is provided, we can use that to figure out the frame sizing, instead of using frameWH 
    if video_obj_ref is not None and frameWH is None:
        vid_width = int(video_obj_ref.get(cv2.CAP_PROP_FRAME_WIDTH))
        vid_height = int(video_obj_ref.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frameWH = (vid_width, vid_height)
    
    # Find window center point, since positioning is relative to top-left corner of the window
    half_w = frameWH[0]/2
    half_h = frameWH[1]/2
    
    # Figure out how much to move the window so that it is centered (with possible offset)
    move_x = int(center_x + offsetXY[0] - half_w)
    move_y = int(center_y + offsetXY[1] - half_h)
    
    # Move the window!
    window_ref.move(x = move_x, y = move_y)
        
# .....................................................................................................................
        
def downscale_to_target(vidWH, targetWH):
    
    # Allocate outputs
    scaledWH = vidWH
    requires_downscaling = False
    
    # Get the scaling factor 
    scaleFractW = targetWH[0] / vidWH[0]
    scaleFractH = targetWH[1] / vidWH[1] 
    
    # If the video frame size is already smaller than the targetWH, don't do any downscaling
    if (scaleFractW > 1.0) and (scaleFractH > 1.0):
        return requires_downscaling, scaledWH
    
    # Video is larger than target is one/both dimensions, so scale it down by whichever dimension needs the most scaling
    requires_downscaling = True
    dimScale = min(scaleFractW, scaleFractH)
    scaledWH = (int(round(dimScale*vidWH[0])), int(round(dimScale*vidWH[1])))
    
    return requires_downscaling, scaledWH

# .....................................................................................................................
        
def check_os(target_os = None):
    
    import sys
    
    # Check operating systems
    is_windows = ("win32" == sys.platform) or ("win64" == sys.platform)
    is_mac = ("darwin" == sys.platform)
    is_linux = ("linux" == sys.platform)
    
    # Return all checks if a target system isn't specified
    if target_os is None:
        return {"windows": is_windows,
                "mac": is_mac,
                "linux": is_linux}
        
    # Make sure the target os is a valid choice
    target_os = target_os.lower()
    if target_os not in ["windows", "mac", "linux"]:
        raise NameError("Target OS not recognized! Must be 'windows', 'mac' or 'linux'")
    
    # Return target check
    if target_os == "windows":
        return is_windows    
    if target_os == "mac":
        return is_mac    
    if target_os == "linux":
        return is_linux

# .....................................................................................................................

# .....................................................................................................................

# .....................................................................................................................

# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap


if __name__ == "__main__":
    
    
        
    import subprocess
    
    #gg = subprocess.check_output(["which xpydrinfo"], shell=True).decode()
    gg = subprocess.call(["which", "xrandr"]) #  .check_output(["which xpydrinfo"], shell=True).decode()

    
    '''
    video_source = "/home/eo/Desktop/PythonData/Shared/videos/pl_part1_rot720.mp4"
    videoObj = cv2.VideoCapture(video_source)
    
    
    winTest = TimebarWindow("TestTimebar")#, videoObj_ref = videoObj)
    winTest.addTimebar(videoObj)
    
    center_window(winTest, video_obj_ref = videoObj)
    
    while True:
        
        reqBreak, reqContinue, inFrame = winTest.get_frame(videoObj)
        if reqBreak: break
        if reqContinue: continue
        
        #(rec, inFrame) = videoObj.read()
        #if not rec: break
        
        winTest.imshow(inFrame)
        #cv2.imshow("Frame", inFrame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27: break
        
        if key == 32:
            winTest.pause(inFrame)
        
    
    
    pass
    videoObj.release()
    cv2.destroyAllWindows()
    '''





    