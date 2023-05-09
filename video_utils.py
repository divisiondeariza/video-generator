# Description: This file contains functions that are used to process videos
import subprocess

def get_video_length(filename):
    #uses ffmpeg to get the length of the video
    video_length = subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filename}', shell=True, stderr=subprocess.STDOUT)
    return float(video_length)