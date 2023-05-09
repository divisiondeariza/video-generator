# this script extrat the video frames from a video and reconstruct it
from extract_video_frames import extract_video_frames
import numpy as np
from datetime import timedelta
from PIL import Image
import torch
import os
from rife_interpolate import generate_frames_for_dir
from image_utils import get_canny_image, squarify_image
from video_utils import get_video_length


input_video = 'input.mp4'
output_video = 'output.mp4'
frames_path = 'frames'
output_path = 'imgs'

timestamps = []
total_seconds = get_video_length(input_video)
for i, seconds in enumerate(np.arange(0, total_seconds, 0.1)):
    timestamps.append({'start_time': timedelta(seconds=seconds), 
                       'end_time': timedelta(seconds=seconds + 0.1),
                       'frame_name': f'{i:04d}_0000'})


#extract the frames from the video
extract_video_frames(timestamps, input_video, frames_path)

for i, timestamp in enumerate(timestamps):
    image = Image.open(os.path.join(frames_path, 
                                         f"{timestamp['frame_name']}.png"))
    canny_image = get_canny_image(image)
    canny_image = squarify_image(canny_image, side=512)
    canny_image.save(os.path.join(output_path, 
                                  f"{timestamp['frame_name']}.png"))
    

#reconstruct the video
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
generate_frames_for_dir(device, output_path, n=2)

if __name__ == '__main__':
    print('Reconstructing video...')
    print(total_seconds)