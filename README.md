# Rottler

The rotate/timelapse/scaler script! Videos may be batch processed or individually processed, depending on user selections.

## Requirements

This script relies on a command line tool called [Ranger](https://github.com/ranger/ranger). On Ubuntu, this can be installed as follows:

```sudo apt install ranger```

In addition, this script assumes OpenCV (3+) is installed from source. Alternatively, OpenCV can be pip installed, but this may cause issues with recording. To pip install, use:

```pip3 install numpy opencv-python ```

See the **Recording** section below for help dealing with issues that may arise from this type of installation.

Lastly, this script provides a progress bar in the terminal using [tqdm](https://github.com/tqdm/tqdm). This can be pip installed:

```pip3 install tqdm ```

## Usage

This script is entirely command-line based. Launch using:

```python3 rottler_cli.py ```

The user is first prompted with a message about using ranger. The file system can be navigated with arrow keys in order to find a video (or videos) for applying rotation/timelapsing/scaling. 
As indicated by the terminal prompt, ```spacebar``` can be used to select multiple files (then pressing ```enter``` to confirm the selections). 

Following the file selection, the user is prompted with settings for the number of counter-clockwise (CCW) 90 degree rotations to apply (0 indicates no rotation), a timelapsing factor (0 or 1 indicates no timelapsing) and a scaling factor (1.0 indicates no scaling).

**Note 1:** The rotation/timelapse/scaling settings apply to all videos that were selected. If different videos need different settings, they will need to be run separately.

**Note 2:** Selection choices are saved (and then provided as defaults on the next run). Leaving an entry blank will result in selecting the default. Deleting the *selection_history.json* file (created on first run) will reset the defaults.

**Note 3:** Recorded files are saved in (automatically named) folders located in the same directory as the original video files. Currently this cannot be changed.

## Recording

After running the script once, a file named *recording_settings.json* will be created in the script directory. This file contains two settings that specify the video container and codec used when recording videos.

If OpenCV was pip installed, the default settings (*.mp4* & *avc1*) may not work! Additionally, there may not be an obvious error to warn of recording issues (instead, either there will not be a recorded file or the file will be empty/corrupt).

To avoid pip install issues, you may need to alter the recording settings. On Ubuntu 18.04, the following settings work with a pip install (as of July 4 :rocket:, 2019):

```
(recording_settings.json)

{
  "recording_ext": ".mp4",
  "codec": "avc1"
}
```

Note however that XVID will generate much larger (~5x) video files than avc1/X264. If XVID fails, MJPG may work, but generates even bigger (~10x) files.
If file size is an issue, it may be best to install OpenCV from source.
