"""
Python program for merging .wav files
USAGE: (python) wav_merge.py -d "directory_name"
Note: files must be named such that they will automatically sort correctly. I.e. "01, 02, 03, .., 10, 11" so that
    sorting doesn't go: "1, 10, 11, 2, 3, 4, ..."
"""

import os
import argparse
import pydub

def main():
    parser =  argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", action="store", dest="dir", help="directory of .wav files to merge. (will "
                                                                          "ignore other filetypes in directory")
    options = parser.parse_args()
    combined = merge(options.dir)
    combined.export("{}/combined.wav".format(options.dir), format="wav")

def merge(dir_name):
    """
    Merges all .wav files in a given directory.
    :param dir_name: name of directory to look in (directory must be under same directory as script)
    :return: combined .wav object
    """
    dir_list = [file for file in os.listdir(dir_name) if file.endswith(".wav")]
    wavs = [pydub.AudioSegment.from_wav("{}/{}".format(dir_name,fname)) for fname in dir_list]
    combined = reduce( (lambda x,y: x + y), wavs)
    return combined

if __name__ == "__main__":
    main()