#!/usr/bin/env python3
from captions import get_captions
import sys 


#call the function and pass the url of the youtube video 
if __name__ == '__main__':
    #get the url from args when running the script
    url = sys.argv[1]
    captions = get_captions(url)
    for caption in captions:
        print(caption['text'])
    print('Total number of timestamps: ' + str(len(captions)))


