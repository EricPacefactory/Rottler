#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 15:13:27 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports

import os
import cv2
import datetime as dt

# ---------------------------------------------------------------------------------------------------------------------
#%% Define classes

class Video_Recorder:
    
    # .................................................................................................................
    
    def __init__(self, save_path, recording_FPS, recording_WH = None, codec="X264", enabled = True):
            
        # Store inputs
        self.save_path = save_path
        self.fps = recording_FPS
        self.frameWH = recording_WH
        self.codec = codec
        self._disabled = (not enabled)
        self.video_quality = None
    
        # Create derived variables
        self.save_name = os.path.basename(save_path)
        self.save_name_only, self.save_extension = os.path.splitext(self.save_name)
        self._fourcc = cv2.VideoWriter_fourcc(*codec)
        self.video_writer = None
        
        # Store start time
        self.start_time = dt.datetime.now()
        self.end_time = None
        
        # Create frame counting variables for timelapsing
        self._frame_count = 0
        self._timelapse_factor = 1
        self._timelapse_enabled = False
        
        # Create initial recorder if a frame size is given
        if recording_WH is not None:
            self._create_video_writer()
        
    # .................................................................................................................
    
    def set_timelapse(self, timelapse_factor):  
        self._frame_count = 0
        self._timelapse_enabled = True
        self._timelapse_factor = timelapse_factor
        
    # .................................................................................................................
        
    def write(self, frame, auto_resize = True):
        # Mimic OpenCV writer function, but with size checks and built-in timelapsing
        
        # Handle disabled case
        if self._disabled:
            return False
        
        # Perform timelapsing if enabled
        if self._timelapse_enabled:
            if (self._frame_count % self._timelapse_factor) != 0:
                return False
        
        # If we haven't set the frame size yet, take the sizing info from the incoming frame
        if self.frameWH is None:
            frame_height, frame_width = frame.shape[0:2]
            self.frameWH = (frame_width, frame_height)
            self._create_video_writer()
        
        # If desired, automatically resize incoming frames if they don't match the target frame size
        if auto_resize:
            frame_height, frame_width = frame.shape[0:2]
            if self.frameWH[0] != frame_width or self.frameWH[1] != frame_height:
                frame = cv2.resize(frame, dsize = self.frameWH)
        
        # Write the current frame
        self.video_writer.write(frame)
        self._frame_count += 1
        
        # Return a value of true if a frame was recorded
        return True
        
    # .................................................................................................................
        
    def release(self):        
        if self.video_writer is not None:
            self.video_writer.release()
            self.end_time = dt.datetime.now()
        
    # .................................................................................................................
    
    def close(self):
        self.release()
        
    # .................................................................................................................
    
    def set_quality(self, quality_percent):
        #raise NotImplementedError("Quality settings do not appear to work properly yet...")
        self.video_quality = quality_percent
        if self.video_writer is not None:
            self.video_writer.set(cv2.VIDEOWRITER_PROP_QUALITY, quality_percent)
        else:
            raise AttributeError("Must setup video writer before setting the quality!")
        
    # .................................................................................................................
    
    def is_open(self):
        try:
            return self.video_writer.isOpened()
        except AttributeError:
            return False
       
    # .................................................................................................................
        
    def report_start(self, 
                     message = "Recording started",
                     report_time = True,
                     report_path = True, 
                     report_name = False, 
                     report_codec = True,
                     prepend_separator = True,
                     append_separator = True,
                     prepend_newline = True,
                     separator = "*" * 36,
                     report_disabled_warning = True,
                     disabled_message = "RECORDING DISABLED",
                     print_string = True,
                     return_string = False):
        
        # Handle case where recording is disabled
        if self._disabled:
            if not report_disabled_warning:
                return 
            message = disabled_message
        
        # Get starting time string
        time_now = dt.datetime.now()
        time_str = time_now.strftime("%Y/%m/%d %H:%M:%S")
            
        # Build output string based on function args
        add_str = lambda include, text, var: [text.format(var)] if include else []
        out_string_list = []
        out_string_list += add_str(prepend_newline, "", "")
        out_string_list += add_str(prepend_separator, separator, "")
        out_string_list += add_str(True, message, "")
        out_string_list += add_str(report_time, "  Time: {}", time_str)
        out_string_list += add_str(report_path, "  Path: {}", self.save_path)
        out_string_list += add_str(report_name, "  Name: {}", self.save_name)
        out_string_list += add_str(report_codec, "  Codec: {}", self.codec)
        out_string_list += add_str(append_separator, separator, "")
        str_to_print = "\n".join(out_string_list)
        
        # Only print to the terminal if desired
        if print_string:
            print(str_to_print)
            
        # Allow for a return, in case we want to log this info
        if return_string:
            return str_to_print
        
    # .................................................................................................................
    
    def report_end(self, 
                   message = "Recording finished!",
                   report_time = True,
                   report_path = False,
                   report_name = False,
                   report_codec = False,
                   prepend_separator = True,
                   append_separator = True,
                   prepend_newline = True,
                   separator = "*" * 36,
                   report_disabled_warning = False,
                   disabled_message = "RECORDING DISABLED",
                   print_string = True,
                   return_string = False):
        
        str_to_print = self.report_start(message, 
                                         report_time, 
                                         report_path, 
                                         report_name, 
                                         report_codec, 
                                         prepend_separator,
                                         append_separator, 
                                         prepend_newline, 
                                         separator, 
                                         report_disabled_warning, 
                                         disabled_message,
                                         print_string, 
                                         return_string)
        
        if return_string:
            return str_to_print
        
    # .................................................................................................................
    
    def find_valid_codec(self):
        
        # Function that should try making a few videos with various codecs to see which one works
        # (different systems may support different codecs!)
        raise NotImplementedError("Sorry, not done yet!")
        
    # .................................................................................................................
        
    def _create_video_writer(self, is_color = True):
        
        # Handle disabled case
        if self._disabled:
            return
    
    
        # Make sure the save pathing is ok
        os.makedirs(os.path.dirname(self.save_path), exist_ok = True)
        
        if self.frameWH is None:
            raise AttributeError("Frame size not set!")
            
        if self.codec is None:
            raise AttributeError("Codec not set")
            
        if self.fps is None:
            raise AttributeError("FPS not set")
        
        self.video_writer = cv2.VideoWriter(self.save_path,
                                             self._fourcc,
                                             self.fps,
                                             self.frameWH,
                                             is_color)
        
        # Only try to set the video quality if it was specified
        if self.video_quality is not None:
            self.set_quality(self.video_quality)
        
    # .................................................................................................................
    
    # .................................................................................................................
    
    # .................................................................................................................
    
    
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================

class Video_Reader:
    
    def __init__(self, source_path, close_immediately = False):
        
        # Get basic info about the video before opening
        self.video_source = source_path
        self.source_type_dict = get_video_source_type(source_path)        
        self.video_fullname, self.video_name_only, self.video_extension = get_video_naming(source_path)
        
        # Allocate storage for type specific info
        self.video_folder = None
        self.rtsp_info = None
        self.webcam_number = None
        
        # Extra checks/work for specific source types
        if self.source_type("file"):
            self.video_folder = os.path.dirname(source_path)
            
            # Check that source path is valid (if we're dealing with a file)
            if not os.path.exists(source_path):
                raise FileNotFoundError("Couldn't find video: {}".format(source_path))
                
        elif self.source_type("rtsp"):    
            self.rtsp_info = get_video_rtsp_info(source_path)
        
        elif self.source_type("webcam"):
            self.webcam_number = int(source_path)
            
        # Open the video
        self.video_object = cv2.VideoCapture(source_path)
        
        # Get the video info
        self.video_info = get_video_object_info(self.video_object)
        
        # Set up frame indexing variables
        self.frame_count = 0
        self.start_frame = 0
        self.end_frame = self.total_frames - 1
        
        # Release the video file right away, if desired (useful for just getting video info without leaving file open)
        if close_immediately:
            self.close(close_all_windows = False)
    
    # .................................................................................................................
    
    def __repr__(self):
        out_string = [""]
        out_string += ["********** Video Reader **********"]
        out_string += ["File: {}".format(self.video_fullname)]
        out_string += ["From: {}".format(self.video_folder)]
        out_string += ["Dimensions: {} x {}".format(*self.WH)]
        out_string += ["Framerate: {}".format(self.info("fps"))]
        out_string += ["Total Frames: {}".format(self.total_frames)]
        out_string += ["**********************************"]
        return "\n".join(out_string)
    
    # .................................................................................................................
    
    def __run__(self):
        return self.video_object
    
    # .................................................................................................................
    
    def read(self):
        
        '''
        Read frames, sequenctially, from the video source
        Returns:
            request_break (boolean), frame (np.array)
        '''
        
        received_frame, frame = self.video_object.read()
        request_break = (not received_frame)
        self.frame_count += 1
            
        return request_break, frame
    
    # .................................................................................................................
    
    def no_decode_read(self):
        
        ''' 
        Read frames without decoding.
        Use this if the frame may be discarded, so some cpu can be saved by avoiding the decoding process
        Once the frame is needed, call decode_read()
        '''
        
        # Read in a frame, but don't decode it
        received_frame = self.video_object.grab()
        request_break = (not received_frame)
        self.frame_count += 1
        
        return request_break
    
    # .................................................................................................................
    
    def decode_read(self):
        
        '''
        Function used to return the decoded result after calling no_decode_read()
        Calling no_decode_read() followed by decode_read() is equivalent to read(), 
        but if frames are being skipped, skipping the decode_read() call can speed things up considerably!
        '''
        
        received_frame, frame = self.video_object.retrieve()
        request_break = (not received_frame)
        self.frame_count += 1
        
        return request_break, frame
    
    # .................................................................................................................
    
    def get(self, property_code):
        return self.video_object.get(property_code)
    
    # .................................................................................................................
    
    def set(self, property_code, value):
        self.video_object.set(property_code, value)
    
    # .................................................................................................................
    
    def release(self):
        
        try:
            self.video_object.release()
            
        except Exception:
            print("")
            print("!" * 36)
            print("Error releasing video: {}".format(self.video_fullname))
            print("!" * 36)
        
    # .................................................................................................................
        
    def close(self, close_all_windows = True):
        
        self.release()
        
        try:
            if close_all_windows:
                cv2.destroyAllWindows()
        except Exception:
            print("")
            print("!" * 36)
            print("Error closing display windows: {}".format(self.video_fullname))
            print("!" * 36)
        
    # .................................................................................................................
        
    def reopen(self):
        
        # Close the video if it is currently open
        if self.is_open():
            self.close()
            
        # Re-open the video
        self.video_object = cv2.VideoCapture(self.video_source)
    
    # .................................................................................................................
    
    def set_current_frame(self, frame_index):
        self.video_object.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
    # .................................................................................................................
    
    def set_current_progress(self, progress_fraction):
        frame_index = int(round((self.total_frames - 1) * progress_fraction))
        self.video_object.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        
    # .................................................................................................................
    
    def get_current_frame(self):
        return int(self.video_object.get(cv2.CAP_PROP_POS_FRAMES))
    
    # .................................................................................................................
    
    def get_current_time_ms(self):
        return self.video_object.get(cv2.CAP_PROP_POS_MSEC)
    
    # .................................................................................................................
    
    def get_current_time_sec(self):
        return 1000*self.current_time_ms()
    
    # .................................................................................................................
    
    def get_current_progress(self):
        return self.current_frame() / (self.total_frames - 1)
    
    # .................................................................................................................
    
    def is_open(self):
        try:
            return self.video_object.isOpened()
        except AttributeError:
            return False
        
    # .................................................................................................................

    def info(self, *select):
        
        # Allow for list selections
        if len(select) > 1:
            return [self.info(each_entry) for each_entry in select]
        
        # Return all info if no selection is made or just a single value if 1 selection is given
        try:
            return self.video_info if len(select) < 1 else self.video_info[select[0]]
        except KeyError:
            print("")
            print("!" * 36)
            print("Unrecognized info key! ({})".format(select[0]))
            print("Valid key list:")
            for each_key in self.video_info.keys():
                print(" ", each_key)
            print("!" * 36)
            print("")
            return None
            
    # .................................................................................................................
    
    def source_type(self, target_type = None):
        try:
            return self.source_type_dict if target_type is None else self.source_type_dict[target_type]
        except KeyError:
            print("")
            print("!" * 36)
            print("Unrecognized source type key! ({})".format(target_type))
            print("Valid key list:")
            for each_key in self.source_type_dict.keys():
                print(" ", each_key)
            print("!" * 36)
            print("")
            return None
    
    # .................................................................................................................
        
    def break_by_keypress(self, frame_delay = 1,
                          break_on_q = True,
                          break_on_esc = True,
                          break_on_enter = False,
                          mask_keypress = True):
    
        # Get keypress
        keypress = cv2.waitKey(frame_delay) & 0xFF if mask_keypress else cv2.waitKey(frame_delay)
        
        # Check for target key presses
        q_pressed = (keypress == ord('q')) if break_on_q else False
        esc_pressed = (keypress == 27) if break_on_esc else False
        enter_pressed = (keypress == 13) if break_on_enter else False
        
        # Check for break requests
        request_break = any([q_pressed, esc_pressed, enter_pressed])
        
        return request_break, keypress 
    
    # .................................................................................................................
    
    def keypress_forward_backward(self, keypress, forward_keycode = 61, backward_keycode = 45, frames_to_skip = 100):
        
        # keycodes:
        # 45 -> - key
        # 61 -> = key
        
        # Rewind/fastforward with +/- keys
        if keypress == backward_keycode:
            self._rewind(frames_to_skip)
        if keypress == forward_keycode:
            self._fastforward(frames_to_skip)
        
    # .................................................................................................................
    
    @property
    def total_frames(self):
        return self.info("total_frames")
    
     # .................................................................................................................
    
    @property
    def fps(self):
        return self.info("fps")
    
    # .................................................................................................................
    
    @property
    def width(self):
        return self.info("width")
    
    # .................................................................................................................
    
    @property
    def height(self):
        return self.info("height")
    
    # .................................................................................................................
    
    @property
    def WH(self):
        return tuple(self.info("width", "height"))
    
    # .................................................................................................................
    
    @property
    def shape(self):
        return self.info("shape")
    
    # .................................................................................................................
    
    def _rewind(self, frames_to_skip):
        re_idx = self.get_current_frame() - frames_to_skip
        self.set_current_frame(re_idx)
    
    # .................................................................................................................
    
    def _fastforward(self, frames_to_skip):
        ff_idx = self.get_current_frame() + frames_to_skip
        self.set_current_frame(ff_idx)
    
    # .................................................................................................................
    
    # .................................................................................................................
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
    
class Video_Reader_Looping(Video_Reader):
    
    def __init__(self, video_source):
        
        super().__init__(video_source)
        
        
    # .................................................................................................................
    
    def read(self):
        
        # Get frame indexing
        current_frame = self.get_current_frame()
        jumped_frames = False
        
        # Reset play position
        if not (self.start_frame <= current_frame <= self.end_frame):
            self.set_current_frame(self.start_frame)
            jumped_frames = True
        
        # Keep trying to read frames until we're successful
        while True:
            received_frame, frame = self.video_object.read()
            if received_frame:
                break
            else:
                self.set_current_frame(self.start_frame)
                jumped_frames = True
        self.frame_count += 1
        
        return jumped_frames, frame
    
    # .................................................................................................................
    
    def keypress_loop_indices(self, keypress, start_keycode = 49, end_keycode = 50, reset_keycode = 48):
        
        # keycodes:
        # 48 -> 0 key (top row)
        # 49 -> 1 key
        # 50 -> 2 key
        
        # Store start/end frame indices if the 1/2 keys are pressed
        if keypress == start_keycode:
            self.set_start_frame(self.get_current_frame(), go_to_start_frame = False)
        if keypress == end_keycode:
            self.set_end_frame(self.get_current_frame())
        if keypress == reset_keycode:
            self.set_start_frame(0, go_to_start_frame = False)
            self.set_end_frame(self.total_frames - 1)
    
    # .................................................................................................................
    
    # .................................................................................................................
    
    # .................................................................................................................
    
    # .................................................................................................................
    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
        
'''
class Video_Reader_Threaded(Video_Reader):
    
    def __init__(self, video_source):
        
        pass
'''

    
# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
        

# ---------------------------------------------------------------------------------------------------------------------
#%% Define functions

# .....................................................................................................................

def get_video_naming(video_source, rtsp_name = "RTSP.stream", webcam_name = "Webcam.{}"):
    
    # First figure out what kind of source we're dealing with 
    source_type = get_video_source_type(video_source)
    
    # Allocate space for outputs
    full_filename = name_only = extension = ""
    
    if source_type["rtsp"]:
        # Make up a name
        full_filename = rtsp_name
    elif source_type["webcam"]:
        # Make up a name
        full_filename = webcam_name.format(video_source)
    elif source_type["file"]:
        # Straightforward
        full_filename = os.path.basename(video_source)
    else:
        # Don't know what we're dealing with, so assume it's some kind of file
        full_filename = os.path.basename(video_source)
    
    # Split the name and extension
    name_only, extension = os.path.splitext(full_filename)
    
    return full_filename, name_only, extension

# .....................................................................................................................
    
def get_video_source_type(video_source):
    
    # Store defaults
    is_rtsp = False
    is_webcam = False
    is_file = False
    is_unknown = True
    
    # Do simple source type checks
    is_rtsp = "rtsp://" in video_source.lower()
    is_webcam = type(video_source) is int
    
    # Check for file if we don't tag one of the easier types
    if not is_rtsp and not is_webcam:
        full_filename = os.path.basename(video_source)
        name_only, ext = os.path.splitext(full_filename)
        
        known_video_file_ext_list = [".avi", ".mp4", ".mpg", ".mpeg", ".mov", ".mkv", ".webm", "wmv"]
        is_file = ext.lower() in known_video_file_ext_list
        
    # Finally set unknown flag
    is_unknown = not any([is_rtsp, is_webcam, is_file])
    
    # Store results in dictionary for most compact reference
    source_type_dict = {"rtsp": is_rtsp,
                        "webcam": is_webcam,
                        "file": is_file,
                        "unknown": is_unknown}
    
    return source_type_dict

# .....................................................................................................................
    
def get_video_object_info(video_object):

    # Get basic video info
    total_frames = int(video_object.get(cv2.CAP_PROP_FRAME_COUNT))
    framerate = video_object.get(cv2.CAP_PROP_FPS)
    vid_width = int(video_object.get(cv2.CAP_PROP_FRAME_WIDTH))
    vid_height = int(video_object.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vid_channels = 3 # Probably
    vidHWC = (vid_height, vid_width, vid_channels)
    
    # Try to get the video codec
    fourcc = video_object.get(cv2.CAP_PROP_FOURCC)
    codec = int(fourcc).to_bytes(4, 'little').decode()
    codec = "unknown" if codec == "\x00\x00\x00\x00" else codec
    
    info_dict = {"total_frames": total_frames,
                 "fps": framerate,
                 "width": vid_width,
                 "height": vid_height,
                 "channels": vid_channels,
                 "shape": vidHWC,
                 "codec": codec}
    
    return info_dict

# .....................................................................................................................
    
def get_video_rtsp_info(video_source, error_if_not_rtsp = True):
    
    # Make sure we've got an rtsp video
    is_rtsp = "rtsp://" in video_source.lower()
    if not is_rtsp:
        if error_if_not_rtsp:
            raise TypeError("Video source is not RTSP: {}".format(video_source))
        return None
    
    # First remove the rtsp:// piece of the string
    rtsp_back = video_source[7:]
    
    # Next split the username/password from the ip/port/command
    if "@" in rtsp_back:
        user_pass, ip_port_cmd = rtsp_back.split("@")
    else:
        # If no @ sign found, assume there is no user/password
        user_pass = ":"
        ip_port_cmd = rtsp_back
        
    # Split ip and port/command
    ip, port_cmd = ip_port_cmd.split(":")
    
    # Split user/password if possible
    username_password_pair = user_pass.split(":")
    username = username_password_pair[0]
    password = "" if len(username_password_pair) < 2 else username_password_pair[1]
    
    # Split port and command, if possible
    port_command_pair = port_cmd.split("/")
    port = port_command_pair[0]
    command = "" if len(port_command_pair) < 2 else port_command_pair[1]
    
    # Build into dictionary for convenient access
    rtsp_info_dict = {"ip": ip,
                      "username": username,
                      "password": password,
                      "port": port,
                      "command": command}
    
    return rtsp_info_dict

# .....................................................................................................................
        

# ---------------------------------------------------------------------------------------------------------------------
#%% Demo
        
if __name__ == "__main__":
    
    import numpy as np
    
    # ********** Video writing example **********
    qualities = [5, 50, 100]
    framerate, length_seconds = 30, 10
    frame_width, frame_height, frame_channels = 640, 360, 3
    video_path = os.path.join(os.path.expanduser(os.path.join("~", "Videos")), "test_out.avi")
    write_source = os.path.join(video_path)
    
    print("Recording demo file: {}".format(write_source))
    vwriter = Video_Recorder(write_source, framerate)
    for k in range(length_seconds*framerate):
        rand_frame = np.random.randint(0, 255, (frame_height, frame_width, frame_channels), dtype=np.uint8)
        vwriter.write(rand_frame)
    vwriter.release()

    # ********** Video reading example **********
    vreader = Video_Reader(write_source)
    info = get_video_object_info(vreader.video_object)
    print(vreader)
    for k in range(vreader.total_frames):
        reqBreak, inFrame = vreader.read()
        if reqBreak:
            break
        cv2.imshow("Display", inFrame)
        cv2.waitKey(int(1000/vreader.fps))
    vreader.close()


# ---------------------------------------------------------------------------------------------------------------------
#%% Scrap


