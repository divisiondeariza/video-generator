#!/usr/bin/env python3

#import all necessary libraries and modules
import os, re, sys
from bs4 import BeautifulSoup
import webvtt
from datetime import datetime

  
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
        start_time = datetime.strptime(timestamp[0], '%H:%M:%S.%f')
        end_time = datetime.strptime(timestamp[1], '%H:%M:%S.%f')
        datetime_timestamps.append((start_time, end_time, timestamp[2]))

    return datetime_timestamps

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

#call the function and pass the url of the youtube video 
if __name__ == '__main__':
    #get the url from args when running the script
    url = sys.argv[1]
    timestamps = get_timestamps(filter_timestamps(get_raw_timestamps(url)))
    for timestamp in timestamps:
        print(timestamp[-1])
    print('Total number of timestamps: ' + str(len(timestamps)))


