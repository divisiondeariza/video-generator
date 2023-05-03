#!/usr/bin/env python3
# Description: Extract captions from YouTube videos using the yt-dlp library.
import os, re, sys
from bs4 import BeautifulSoup
import webvtt
from datetime import datetime, timedelta
import numpy as np
import subprocess
from yt_dlp import YoutubeDL
from io import StringIO

def get_raw_timestamps(url):
    """
    Extract timestamps with text from a VTT file.

    Args:
        url (str): URL of the video for which subtitles are to be extracted.

    Returns:
        list: A list of tuples containing the start time, end time, and text of each caption.

    Raises:
        None
    """

    # this is equivalent to the command above
    ydl_opts = {'writeautomaticsub': True, 'skip_download': True, 'subtitlesformat': 'srt'}
    with YoutubeDL(ydl_opts) as ydl:
        #to get the srt captions as a string
        subtitles_list = ydl.extract_info(url, download=False)['automatic_captions']['en']
        # Now find the vtt subtitles in the list using the extension and a lambda function
        vtt_subtitles_url = list(filter(lambda x: x['ext'] == 'vtt', subtitles_list))[0]['url']
        # Download the vtt subtitles using the url and store them in a variable
        vtt_subtitles = ydl.urlopen(vtt_subtitles_url).read().decode('utf-8')

    timestamp = []
    # Iterate through the captions in the vtt file with all the subtitles in the vtt_subtitles variable
    subtitles_buffer = StringIO(vtt_subtitles)
    for caption in webvtt.read_buffer(subtitles_buffer):
        # Replace \n with spaces
        caption_text = re.sub(r'\n', ' ', caption.text).strip()
        timestamp.append((caption.start, caption.end, caption_text))
    
    return timestamp

#write a function that takes the results from the get_timestamps function and transform timestamps in datetimes
def get_timestamps(timestamps):
    """
    Convert timestamps to datetime objects.

    Args:
        timestamps (list): A list of tuples containing the start time, end time, and text of each caption.

    Returns:
        list: A list of tuples containing the start time, end time, and text of each caption as datetime objects.

    Raises:
        None
    """
    datetime_timestamps = []
    for timestamp in timestamps:
        start_time = get_timedelta_from_string(timestamp[0])
        end_time = get_timedelta_from_string(timestamp[1])
        datetime_timestamps.append((start_time, end_time, timestamp[2]))

    return datetime_timestamps

def get_timedelta_from_string(string):
    """
    Convert a string with format '%H:%M:%S.%f' to a timedelta object.

    Args:
        string (str): A string with format '%H:%M:%S.%f'.

    Returns:
        datetime.timedelta: A timedelta object.

    Raises:
        None
    """
    return datetime.strptime(string, '%H:%M:%S.%f') - datetime.strptime('00:00:00.000', '%H:%M:%S.%f')

def filter_adjacent_texts(timestamps):
    """
    Filter out captions whose text is fully contained within the text of adjacent captions.

    Args:
        timestamps (list): A list of tuples containing the start time, end time, and text of each caption.

    Returns:
        list: A list of tuples containing the start time, end time, and text of each caption that is not fully contained within the text of adjacent captions.

    Raises:
        None
    """
    filtered_timestamps = []

    # Iterate through the timestamps list, excluding the first and last elements
    for i in range(1, len(timestamps) - 1):
        current_text = timestamps[i][2]
        prev_text = timestamps[i-1][2]
        next_text = timestamps[i+1][2]

        # Check if the current text is fully contained within the text of adjacent captions
        if (current_text not in prev_text 
            and current_text not in next_text):
            filtered_timestamps.append(timestamps[i])

    #filters out the timestamps that are not fully contained within the text of adjacent captions
    i = 1
    while i < len(filtered_timestamps) - 1:
        current_text = filtered_timestamps[i][2]
        prev_text = filtered_timestamps[i-1][2]
        next_text = filtered_timestamps[i+1][2]

        if (current_text in prev_text + " " + next_text):
            filtered_timestamps.pop(i)
        else:
            i += 1


    # Include the first and last timestamps in the filtered list
    if timestamps[0][2] not in filtered_timestamps[0][2]:
        filtered_timestamps.insert(0, timestamps[0])
    filtered_timestamps.append(timestamps[-1])

    return filtered_timestamps

#make a function that filters timestamps with filter_adjacent_texts until the list is not changed anymore or after n attempts
def filter_timestamps(timestamps, n=10):
    """
    Filter out captions whose text is fully contained within the text of adjacent captions.

    Args:
        timestamps (list): A list of tuples containing the start time, end time, and text of each caption.

    Returns:
        list: A list of tuples containing the start time, end time, and text of each caption that is not fully contained within the text of adjacent captions.

    Raises:
        None
    """
    filtered_timestamps = filter_adjacent_texts(timestamps)
    for i in range(n):
        if filtered_timestamps == timestamps:
            break
        timestamps = filtered_timestamps
        filtered_timestamps = filter_adjacent_texts(timestamps)

    return filtered_timestamps


def get_captions(url):
    """
    Extract timestamps with text from a VTT file.

    Args:
        url (str): URL of the video for which subtitles are to be extracted.

    Returns:
        list: A list of tuples containing the start time, end time, and text of each caption.

    Raises:
        None
    """
    timestamps = get_timestamps(filter_timestamps(get_raw_timestamps(url)))
    captions = []
    for timestamp in timestamps:
        captions.append(timestamp[-1])

    #returns the results in form of a list of dicts with keys start_time, end_time and text
    return [{'start_time': timestamp[0], 
             'end_time': timestamp[1], 
             'text': timestamp[2]} 
             for timestamp in timestamps]

def get_equally_separated_captions(captions, delta_seconds):
    #creates a list of captions equally spaced by delta_seconds
    #create a timedelta objects from delta_seconds
    total_seconds = (captions[-1]['end_time'] - captions[0]['start_time']).total_seconds()
    timestamps_list = list(np.arange(0, total_seconds, delta_seconds)) + [total_seconds]
    timestamps_list = [timedelta(seconds = timestamp) for timestamp in timestamps_list]
    spaced_captions = [{'start_time': timestamps_list[i], 
                        'end_time': timestamps_list[i+1]} for i in range(len(timestamps_list) - 1)]
    # add the rest of the elements to the closests spaced_captions elements
    
    for spaced_caption in spaced_captions:
        for caption in captions:
            if (spaced_caption['end_time'] < caption['end_time']):
                # adds all elements on the same spaced_caption except start_time and end_time
                spaced_caption.update({key: caption[key] for key in caption.keys() if key not in ['start_time', 'end_time']})
                break
    return spaced_captions

if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=6ZfuNTqbHE8'
    captions = get_captions(url)
    spaced_captions = get_equally_separated_captions(captions, 0.2)
    for caption in captions:
        print(caption['text'])
    for caption in spaced_captions:
        print(caption['text'])


