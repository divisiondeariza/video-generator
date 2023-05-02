#!/usr/bin/env python3

import os, sys, re
from captions import get_captions, get_equally_separated_captions
from datetime import datetime
from tqdm import tqdm
import subprocess

#write a method that extracts the frames from the youtube video given a list of timestamps and saves them in a folder
#
def extract_frames_from_yt_video(timestamps, url, frames_path = 'frames'):
    """
    Extract frames from a YouTube video at the specified timestamps.
    
    Args:
        timestamps (list): A list of tuples containing the start time, end time, and text of each caption.
        url (str): URL of the video for which frames are to be extracted.
        frames_path (str): Path to the folder where the frames are to be saved.
    
    Returns:
        None
    
    Raises:
        None
    """
    #create a folder for the frames
    if not os.path.exists(frames_path):
        os.mkdir(frames_path)
    
    #download the video and stores the name of the file, uses the format mp4
    os.system(f'yt-dlp --quiet -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4 --output "{frames_path}/%(title)s.%(ext)s" {url} ')

    #gets the name of the file
    # finds the mp4 file in the folder
    filename = [filename for filename in os.listdir(frames_path) if filename.endswith('.mp4')][0]
    #extract the frames
    extract_video_frames(timestamps, frames_path + "/" + filename, frames_path)

def extract_video_frames(timestamps, filename, frames_path = 'frames'):
    for timestamp in tqdm(timestamps):
        #convert the timestamps to hh:mm:ss format
        start_time = (datetime(1,1,1) + timestamp['start_time']).strftime('%H:%M:%S.%f')
        #to add fractions of seconds use %H:%M:%S.%f
        end_time = (datetime(1,1,1) + timestamp['end_time']).strftime('%H:%M:%S.%f')
        frame_name = timestamp['frame_name']
        ffmpeg_command = f'ffmpeg -hide_banner -ss  {str(start_time)} -i "{filename}" -vframes 1  {frames_path}/{frame_name}.png 2>&1'
        output = subprocess.check_output(ffmpeg_command, shell=True, stderr=subprocess.STDOUT)

if __name__ == "__main__":
    #url = sys.argv[1]
    url = 'https://www.youtube.com/watch?v=IyJFBVm3Qlg'
    timestamps = get_captions(url)
    timestamps = get_equally_separated_captions(timestamps, 1)
    timestamps = [{'start_time': timestamp['start_time'], 
                   'end_time': timestamp['end_time'], 
                   'text': f'{index:04d}_0000'} 
                   for index, timestamp in enumerate(timestamps)]
    extract_frames_from_yt_video(timestamps, url, 'frames')

