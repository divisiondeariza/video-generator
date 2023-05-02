#!/usr/bin/env python3
# in this file we will extract frames from a youtube video, create equally separated captions and generate frames using these timestamps and rife interpolation

from captions import get_captions, get_equally_separated_captions
from extract_video_frames import extract_frames_from_yt_video
import torch
from rife_interpolate import generate_frames_for_dir

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    frames_path = 'frames'
    url = 'https://www.youtube.com/watch?v=IyJFBVm3Qlg'
    timestamps = get_captions(url)
    timestamps = get_equally_separated_captions(timestamps, 0.2)
    timestamps = [{'start_time': timestamp['start_time'], 
                   'end_time': timestamp['end_time'], 
                   'frame_name': f'{index:04d}_0000',
                   'text': timestamp['text']}
                   for index, timestamp in enumerate(timestamps)]
    extract_frames_from_yt_video(timestamps, url, frames_path)
    generate_frames_for_dir(device, frames_path, n=2)

# for generating a video withput overwritng frames, use the following command:
# ffmpeg -framerate 30 -pattern_type glob -i 'frames/*_*.png' -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4