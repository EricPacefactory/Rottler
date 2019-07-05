#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 14:11:17 2019

@author: eo
"""


# ---------------------------------------------------------------------------------------------------------------------
#%% Imports

import argparse
import os
import json
from time import perf_counter, sleep

# Warning if numpy isn't installed
try:
    import numpy as np
except ImportError:
    print("",
          "Couldn't import numpy!",
          "",
          "Need to install numpy to continue. Use:",
          "  pip3 install numpy",
          "", sep="\n")
    quit()

# Warning if OpenCV isn't installed
try:
    import cv2
except ImportError:
    print("",
          "Couldn't import OpenCV!",
          "",
          "Need to install OpenCV to continue.",
          "Ideally, OpenCV should be compiled on the system.",
          "However, a simpler method is to use a pip install:",
          "  pip3 install opencv-python",
          "",
          "Warning:",
          "A pip install of OpenCV may not have full recording",
          "capabilities!",
          "", sep="\n")
    quit()

# Warning if tqdm (cli progress bar) isn't installed
try:
    from tqdm import tqdm
    
except ImportError:
    print("",
          "Couldn't import cli progress bar module!",
          "",
          "Need to install tqdm. Use:",
          "  pip3 install tqdm", 
          "", sep="\n")
    quit()

from local.eolib.video.windowing import SimpleWindow
from local.eolib.video.read_write import Video_Reader, Video_Recorder
from local.eolib.utils.cli_tools import ranger_multifile_select, cli_prompt_with_defaults, cli_confirm

# ---------------------------------------------------------------------------------------------------------------------
#%% Define functions

# .....................................................................................................................

def parse_args():
    
    # Get existing/default recording settings so we can use them as defaults for the script arguments
    recording_settings = load_recording_settings()
    default_recording_ext = recording_settings.get("recording_ext")
    default_codec = recording_settings.get("codec")
    
    # Set up argument parsing
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--display", default = True, action = "store_false",
                    help = "Disable the output display. Gives a slight speed boost & prevents pop-up interruptions.")
    ap.add_argument("-x", "--extension", default = default_recording_ext, type = str,
                    help = "File extension of recorded videos (.avi, .mp4, .mkv, etc.). \
                            (Default: {})".format(default_recording_ext))
    ap.add_argument("-c", "--codec", default = default_codec, type = str,
                    help = "FourCC code used for recording (X264, XVID, MJPG, mp4v, etc.). \
                            (Default: {})".format(default_codec))
    
    # Get arg inputs into a dictionary
    args = vars(ap.parse_args())
    
    # Separate arg inputs for convenience
    arg_display = args.get("display")
    arg_codec = args.get("codec")
    arg_ext = args.get("extension")
    
    # Make sure the recording arguments are 'safe' (i.e. extension starts with a . and the codec has 4 characters)
    safe_ext = arg_ext if arg_ext[0] == "." else "." + arg_ext
    safe_codec = arg_codec if len(arg_codec) == 4 else arg_codec[0:4].zfill(4)
    
    # Check if recording arguments are different from defaults
    ext_changed = (safe_ext != default_recording_ext)
    codec_changed = (safe_codec != default_codec)
    update_recording_settings = (ext_changed or codec_changed)
    
    # Save recording settings (but only if the arguments were different from defaults!)
    save_recording_settings(safe_ext, safe_codec, overwrite_existing = update_recording_settings)
    
    return arg_display, safe_ext, safe_codec

# .....................................................................................................................

def load_json_data(load_file_name, default_dict):
    
    # Set up load pathing
    load_folder = os.path.dirname(os.path.realpath(__file__))
    load_path = os.path.join(load_folder, load_file_name)
    
    # Initialize storage for default/loaded data
    output_dict = default_dict.copy()
    load_data = {}
    
    if os.path.exists(load_path):
        with open(load_path, "r") as in_file:
            load_data = json.load(in_file)
            
    # Add loaded data into output dictionary (which overwrites default values, if needed)
    output_dict.update(load_data)
    
    return output_dict

# .....................................................................................................................

def save_json_data(save_file_name, new_data_dict, overwrite_existing = True):
    
    # Set up save pathing
    save_folder = os.path.dirname(os.path.realpath(__file__))
    save_path = os.path.join(save_folder, save_file_name)
    
    # Only save if the folder is valid (don't want to create any new folders...)
    if os.path.exists(save_folder):
        file_already_exists = os.path.exists(save_path)
        if not file_already_exists or (file_already_exists and overwrite_existing):
            with open(save_path, "w") as out_file:
                json.dump(new_data_dict, out_file, indent = 2)

# .....................................................................................................................

def load_recording_settings(file_name = "recording_settings.json"):
    
    default_settings = {"recording_ext": ".avi",
                        "codec": "X264"}
    
    return load_json_data(file_name, default_settings)

# .....................................................................................................................

def load_selection_history(file_name = "selection_history.json"):
    
    default_history = {"search_path": "~/Desktop",
                       "ccw_rotations": 1,
                       "timelapse_factor": 12,
                       "new_scaling_factor": 1.0}
    
    return load_json_data(file_name, default_history)

# .....................................................................................................................
    
def save_recording_settings(recording_ext, codec, overwrite_existing = False, file_name = "recording_settings.json"):
    
    new_recording_settings_data = {"recording_ext": recording_ext,
                                   "codec": codec}
    
    return save_json_data(file_name, new_recording_settings_data, overwrite_existing)

# .....................................................................................................................
    
def save_selection_history(new_search_path, new_ccw_rotations, new_timelapse_factor, new_scaling_factor,
                           file_name = "selection_history.json"):
    
    # Replace home pathing with '~' shortcut before saving
    home_path = os.path.expanduser("~")
    save_search_path = new_search_path.replace(home_path, "~")
    
    new_selection_history_data = {"search_path": save_search_path,
                                  "ccw_rotations": new_ccw_rotation,
                                  "timelapse_factor": new_timelapse_factor,
                                  "scaling_factor": new_scaling_factor}
    
    return save_json_data(file_name, new_selection_history_data)

# .....................................................................................................................

def get_rotation_mapping(frame_width, frame_height, rot_nx90 = 1):
    
    left_to_right_count = np.arange(0, frame_width, dtype=np.float32)
    top_to_bot_count = np.arange(0, frame_height, dtype=np.float32)
    
    lr_mesh, tb_mesh = np.meshgrid(left_to_right_count, top_to_bot_count)
    
    x_mapping = np.rot90(lr_mesh, rot_nx90)
    y_mapping = np.rot90(tb_mesh, rot_nx90)

    return x_mapping, y_mapping

# .....................................................................................................................
# .....................................................................................................................


# ---------------------------------------------------------------------------------------------------------------------
#%% Load defaults

# Get display & recording settings
display_enabled, recording_ext, codec = parse_args()

# Load selection history data to save the user some trouble
#   Contains keys: "search_path", "ccw_rotations", "timelapse_factor"
selection_history = load_selection_history()
default_search_path = os.path.expanduser(selection_history.get("search_path"))
default_rotation = selection_history.get("ccw_rotations", 0)
default_timelapse = selection_history.get("timelapse_factor", 1)
default_scale = selection_history.get("scaling_factor", 1.0)

# ---------------------------------------------------------------------------------------------------------------------
#%% Load file(s)

# Make sure we're using a valid starting directory
starting_dir = default_search_path if os.path.exists(default_search_path) else os.path.expanduser("~")
starting_dir = starting_dir if os.path.exists(starting_dir) else os.getcwd()

try:
    # Give the user some info about using ranger
    user_info_msgs = ["Select one or more files to record with rotation/timelapsing",
                      "  - Use spacebar to select multiple files",
                      "  - Press enter to confirm selection",
                      "",
                      "Press enter to continue..."]
    cli_confirm("\n".join(user_info_msgs), append_default_indicator = False)
    sleep(0.5)
    
    # Select files using ranger
    video_file_select_list = ranger_multifile_select(starting_dir)
    
except SystemExit:
    # Spyder debugging hack
    test_file = ""
    video_file_select_list = [test_file]
    test_files_exist = [os.path.exists(each_file) for each_file in video_file_select_list]
    if not all(test_files_exist):
        raise FileNotFoundError("Couldn't find test files!")

# Some feedback about selections
print("",
      "*" * 48, "",
      "Selected videos:",
      *["  {}".format(os.path.basename(each_file)) for each_file in video_file_select_list], 
      "", "*" * 48,
      sep="\n")

# ---------------------------------------------------------------------------------------------------------------------
#%% Get user input

# Set timelapsing factor & rotation amount
rotation_n90 = cli_prompt_with_defaults("Enter number of CCW 90deg rotations: ", default_rotation, return_type = int)
tl_factor = cli_prompt_with_defaults("             Enter timelapse factor: ", default_timelapse, return_type = int)
scale_factor = cli_prompt_with_defaults("               Enter scaling factor: ", default_scale, return_type = float)

# For readability, figure out how much rotation we're doing
rotation_angle_deg = (90 * rotation_n90) % 360
needs_rotating = abs(rotation_angle_deg) > 0
needs_resizing = abs(scale_factor - 1.0) > 0.001
scale_function = lambda frame, scaling: cv2.resize(frame, dsize = None, fx = scaling, fy = scaling)

# Update selection history
new_search_path = os.path.dirname(video_file_select_list[0])
new_ccw_rotation = rotation_n90
new_timelapse_factor = tl_factor
new_scaling_factor = scale_factor
save_selection_history(new_search_path, new_ccw_rotation, new_timelapse_factor, new_scaling_factor)


# ---------------------------------------------------------------------------------------------------------------------
#%% Recording loop

num_files = len(video_file_select_list)
t_start = perf_counter()
break_all_looping = False
for each_idx, each_file in enumerate(video_file_select_list):
    
    # Get file naming
    full_file_path = os.path.realpath(each_file)
    full_folder_path = os.path.dirname(full_file_path)
    file_name = os.path.basename(each_file)
    
    # Get video info
    vreader = Video_Reader(full_file_path)
    video_width, video_height = vreader.WH
    video_fps = vreader.fps
    video_frames = vreader.total_frames
    video_length_sec = video_frames * video_fps

    # Get mapping used to rotate the video
    x_map, y_map = get_rotation_mapping(video_width, video_height, rotation_n90)

    # Set up recording paths
    file_name_only, _ = os.path.splitext(file_name)
    rotation_name = "Rot_{}deg".format(rotation_angle_deg) if needs_rotating else None
    timelapse_name = "TL_x{}".format(tl_factor) if tl_factor > 1 else "TL_x1"
    scaling_name = "Scale_{}pct".format(int(100 * scale_factor)) if needs_resizing else None
    folder_name = "-".join(filter(None, [rotation_name, timelapse_name, scaling_name]))
    save_folder = os.path.join(full_folder_path, folder_name)
    save_name = "{}_TLx{}{}".format(file_name_only, tl_factor, recording_ext)
    save_path = os.path.join(save_folder, save_name)
    os.makedirs(save_folder, exist_ok = True)
    
    # Set up recorder
    vwriter = Video_Recorder(save_path, video_fps, None, codec = codec, enabled=True)

    # Set up frame/progress tracking
    proc_idx = 1 + each_idx
    proc_msg = "Processing ({}/{}): {} ({:.0f} seconds long)".format(proc_idx, num_files, file_name, video_length_sec)
    print("", proc_msg, sep="\n")
    cli_prog_bar = tqdm(total = video_frames, mininterval = 1)
    frame_count = -1
    
    # Set up display
    disp_window = SimpleWindow("Display", enabled = display_enabled)
    disp_window.move(20, 20)

    # Run video recording loop
    try:
        while True:
            
            # Grab video frame data, without decoding
            req_break = vreader.no_decode_read()
            if req_break:
                break
            
            # Keep track of frames for timelapsing and update cli progress bar
            frame_count += 1
            cli_prog_bar.update()
            
            # Only display/record data on timelapsed frames
            if frame_count % tl_factor == 0:
                
                # Now we need the frame, so decode the frame data
                req_break, frame = vreader.decode_read()
                if req_break:
                    break
                
                # Rotate (and potential scale) the incoming frame
                rot_frame = cv2.remap(frame, x_map, y_map, cv2.INTER_NEAREST) if needs_rotating else frame
                scaled_frame = scale_function(rot_frame, scale_factor) if needs_resizing else rot_frame
                
                # Record & display resulting frame
                vwriter.write(scaled_frame)
                win_exists = disp_window.imshow(scaled_frame)
                if win_exists:
                    cv2.waitKey(1)
                    
    except KeyboardInterrupt:
        break_all_looping = True

    # Clean up
    cli_prog_bar.close()
    vreader.close()
    vwriter.close()
    
    # Stop all video recording if needed
    if break_all_looping:
        break

t_end = perf_counter()


# ---------------------------------------------------------------------------------------------------------------------
#%% Final feedback

print("",
      "All done!",
      "Total processing time (sec): {:.3f}".format(t_end - t_start),
      "             Rotation (deg): {:.0f}".format(rotation_angle_deg),
      "           Timelapse factor: {:.0f}".format(tl_factor),
      "             Scaling factor: {:.3f}".format(scale_factor),
      "", sep="\n")
