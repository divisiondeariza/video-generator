#!/usr/bin/env python3
# in this file we will extract frames from a youtube video, create equally separated captions and generate frames using these timestamps and rife interpolation

import os, sys, re
from captions import get_captions, get_equally_separated_captions
from extract_video_frames import extract_frames_from_yt_video
import cv2, torch
from rife_interpolate import get_image_for_interpolation, resize_frames_for_interpolation, generate_frames

if __name__ == "__main__":
    #url = sys.argv[1]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    frames_path = 'frames'
    url = 'https://www.youtube.com/watch?v=IyJFBVm3Qlg'
    timestamps = get_captions(url)
    timestamps = get_equally_separated_captions(timestamps, 1)
    timestamps = [{'start_time': timestamp['start_time'], 
                   'end_time': timestamp['end_time'], 
                   'text': f'{index:04d}_0000'} 
                   for index, timestamp in enumerate(timestamps)]
    extract_frames_from_yt_video(timestamps, url, frames_path)
    for filename0, filename1 in zip(sorted(os.listdir(frames_path)), sorted(os.listdir(frames_path))[1:]):
        img0 = cv2.imread('frames/' + filename0, cv2.IMREAD_UNCHANGED)
        img1 = cv2.imread('frames/' + filename1, cv2.IMREAD_UNCHANGED)
        img0 = get_image_for_interpolation(img0, device)
        img1 = get_image_for_interpolation(img1, device)
        img0, img1 = resize_frames_for_interpolation(img0, img1)
        frames = generate_frames(img0, img1, 2)
        for index, frame in enumerate(frames):
            n, c, h, w = img0.shape
            start_frame_name = int(filename0.split(".")[0].split("_")[0])
            # save the image in frames like 0000_0000.png if it was interpolated between 0000.png and 0001.png, 0000_0001.png if it was interpolated between 0000.png and 0001.png, etc.
            output_name = "{:04d}_{:04d}.png".format(start_frame_name, index + 1)
            ffmpeg_command = (frame[0] * 255).byte().numpy().transpose(1, 2, 0)[:h, :w]
            cv2.imwrite('frames/{}'.format(output_name), ffmpeg_command)
