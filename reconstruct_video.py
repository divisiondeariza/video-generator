#!/usr/bin/env python3
# in this file we will extract frames from a youtube video, create equally separated captions and generate frames using these timestamps and rife interpolation

from captions import get_captions, get_equally_separated_captions
from extract_video_frames import extract_frames_from_yt_video
import torch
from rife_interpolate import generate_frames_for_dir
from generate_descriptions import generate_image_descriptions_safely
from tqdm import tqdm

import openai
# gets the api key from a file called api_key.txt
with open('api_key.txt', 'r') as f:
    api_key = f.read()

openai.api_key = api_key

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    frames_path = 'frames'
    url = 'https://www.youtube.com/watch?v=IyJFBVm3Qlg'
    timestamps = get_captions(url)
    for timestamp in tqdm(timestamps, desc = 'Generating descriptions'):
        timestamp['description'] = generate_image_descriptions_safely(timestamp['text'], 
                                                               'gpt-3.5-turbo')
    timestamps = get_equally_separated_captions(timestamps, 0.2)
    for index, timestamp in enumerate(timestamps):
        timestamp.update({'frame_name': f'{index:04d}_0000'}) 
    extract_frames_from_yt_video(timestamps, url, frames_path)
    generate_frames_for_dir(device, frames_path, n=2)

# for generating a video withput overwritng frames, use the following command:
# ffmpeg -framerate 30 -pattern_type glob -i 'frames/*_*.png' -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p output.mp4
