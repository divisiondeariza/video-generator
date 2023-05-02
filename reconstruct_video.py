#!/usr/bin/env python3
# in this file we will extract frames from a youtube video, create equally separated captions and generate frames using these timestamps and rife interpolation

import os, sys, re
from captions import get_captions, get_equally_separated_captions
from extract_video_frames import extract_frames_from_yt_video
import torch
from rife_interpolate import generate_frames_for_dir

if __name__ == "__main__":
    #url = sys.argv[1]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    frames_path = 'frames'
    url = 'https://www.youtube.com/watch?v=IyJFBVm3Qlg'
    timestamps = get_captions(url)
    timestamps = get_equally_separated_captions(timestamps, 0.2)
    timestamps = [{'start_time': timestamp['start_time'], 
                   'end_time': timestamp['end_time'], 
                   'text': f'{index:04d}_0000'} 
                   for index, timestamp in enumerate(timestamps)]
    extract_frames_from_yt_video(timestamps, url, frames_path)
    generate_frames_for_dir(device, frames_path, n=4)

        
