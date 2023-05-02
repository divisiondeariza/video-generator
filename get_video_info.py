# This script is used to get the video information from the video file and prints every frame's timestamp and the corresponding text.

# Path: get_video_info.py
# Compare this snippet from reconstruct_video.py:
# #!/usr/bin/env python3
import cv2, os, sys, json
from tqdm import tqdm
import subprocess

# uses ffmpeg to save frames given a list of timestamps
def save_frames(timestamps, video_path, output_dir):
    for index, timestamp in enumerate(tqdm(timestamps)):
        # save frame as JPEG file with index as filename as 0001.jpg is 1, 0002.jpg is 2, etc.
        #filename formats the index to have 4 digits, e.g. 0001.jpg, 0002.jpg, etc.
        filename = f"{output_dir}/{str(index).zfill(4)}.jpg"
        command = ['ffmpeg', '-y', '-i', video_path, '-ss', str(timestamp), '-vframes', '1', filename]
        subprocess.run(command)



if __name__ == "__main__":
    # Execute FFmpeg command to extract keyframe timestamps
    result = subprocess.run(['ffprobe', '-i', 'input.mp4', '-select_streams', 'v', '-show_entries', 'frame=pkt_pts_time,pict_type,coded_picture_number', '-of', 'json'], capture_output=True, text=True)

    # Parse FFmpeg output and transform into list of dicts
    keyframes = []

    data = json.loads(result.stdout.replace('\n', ''))

    for frame in data['frames']:
        if frame['pict_type'] in ['I', 'P']:
            keyframe = {"index": frame['coded_picture_number'], "timestamp": float(frame['pkt_pts_time'])}
            keyframes.append(keyframe)
    print(keyframes)

    # Get list of the closest keyframe timestamps to a list of timestamps

    #timestamp is a list of thirds of seconds until the end of the video
    delta = 1/3
    timestamps = [i*delta for i in range(int(keyframes[-1]['timestamp']/delta))]
    closest_keyframes = [min(keyframes, key=lambda x: abs(x['timestamp'] - timestamp)) for timestamp in timestamps]

    # extract frames from video corresponding to the closest keyframes
    dir_name = 'output'
    save_frames([keyframe['timestamp'] for keyframe in closest_keyframes], 'input.mp4', dir_name)

    # reconstruct video from frames using ffmpeg    
    # Get the list of filenames in the output directory
    filenames = sorted(['output/' + f for f in os.listdir('output') if f.endswith('.jpg')], key=lambda x: float(x.replace('output/', '').replace('.jpg', '')))

    # Construct the FFmpeg command

    # creates a list of lists and then flattens it
    filelist = [['-i',filename] for filename in filenames]
    filelist = [item for sublist in filelist for item in sublist] # flatten list of lists
    command = ['ffmpeg', '-y', '-framerate', '30'] + filelist + ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-i', 'output.mp4']
    
    # Run FFmpeg command
    subprocess.run(command)

    # remove frames and keep only the reconstructed video
    # os.system(f"rm -r {dir_name}/*.jpg")
    # to recosntruct the video from the frames, use the following command:
    # considering that the frames are named 0.3.jpg, 0.6.jpg, 0.96.jpg, etc.
    # ffmpeg -framerate 30 -i %d.jpg -c:v libx264 -pix_fmt yuv420p output.mp4
