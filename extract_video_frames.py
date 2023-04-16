#!/usr/bin/env python3

import os, sys, re
from captions import get_captions, get_timestamps

#write a method that extracts the frames from the youtube video given a list of timestamps and saves them in a folder
#
def extract_frames_from_yt_video(timestamps, url):
    """
    Extract frames from a YouTube video at the specified timestamps.
    
    Args:
        timestamps (list): A list of tuples containing the start time, end time, and text of each caption.
        url (str): URL of the video for which frames are to be extracted.
    
    Returns:
        None
    
    Raises:
        None
    """
    #create a folder for the frames
    if not os.path.exists('frames'):
        os.mkdir('frames')
    
    #download the video and stores the name of the file, uses the format mp4
    os.system('yt-dlp --verbose -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4 --output "frames/%(title)s.%(ext)s" ' + url)

    #gets the name of the file
    filename = os.listdir('frames')[0]
    #extract the frames
    extract_video_frames(timestamps, 'frames/' + filename)

def extract_video_frames(timestamps, filename):
    for timestamp in timestamps:
        #convert the timestamps to hh:mm:ss format
        start_time = timestamp['start_time'].strftime('%H:%M:%S')
        end_time = timestamp['end_time'].strftime('%H:%M:%S')
        text = timestamp['text'].replace(' ', '_')
        #creates a suitable filename from text removing all not alphanumeric characters
        frame_name = re.sub(r'\W+', '_', text)
        os.system(f'ffmpeg -i "{filename}" -ss  {str(start_time)} -to {str(end_time)} -vf fps=1/1 frames/{text}.jpg')


if __name__ == "__main__":
    #url = sys.argv[1]
    url = 'https://www.youtube.com/watch?v=IyJFBVm3Qlg'
    timestamps = get_captions(url)
    extract_frames_from_yt_video(timestamps, url)