#!/usr/bin/env python3
# Description: Extract captions from YouTube videos using the yt-dlp library.
import os, re, sys
from bs4 import BeautifulSoup
import webvtt
from datetime import datetime, timedelta
import numpy as np

  
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
    if not os.path.exists('subs'):
        os.mkdir('subs')

    os.system('yt-dlp --verbose --write-auto-sub --skip-download --sub-format srt --output "subs/%(title)s.%(ext)s" ' + url)

    file_name = os.listdir('subs')[0]
    timestamp = []
    for caption in webvtt.read('subs/' + file_name):
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
        #start_time is a timedelta object created from an string with format '%H:%M:%S.%f'  
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
    spaced_captions = [{'start_time': timestamps_list[i], 'end_time': timestamps_list[i+1], 'text': ''} for i in range(len(timestamps_list) - 1)]
    for spaced_caption in spaced_captions:
        #find the two texts in captions that are closest to the start time of the caption
        #and add them to the text of the caption
        for i in range(len(captions) - 1):
            if captions[i]['start_time'] <= spaced_caption['start_time'] <= captions[i+1]['start_time']:
                text = captions[i]['text'] + ' ' + captions[i+1]['text']
                break
        else:
            #if the start time of the caption is not between the start times of any two captions in captions
            #then the text of the caption is the text of the caption that is closest to the start time of the caption
            if spaced_caption['start_time'] < captions[0]['start_time']:
                text = captions[0]['text']

            #get the longest phrase that is contained in both texts
        for phrase in text.split('.'):
            if len(phrase) > len(spaced_caption['text']):
                spaced_caption['text'] = phrase
    return spaced_captions

if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=6ZfuNTqbHE8'
    captions = get_captions(url)
    spaced_captions = get_equally_separated_captions(captions, 10)
    for caption in captions:
        print(caption['text'])
    for caption in spaced_captions:
        print(caption['text'])


