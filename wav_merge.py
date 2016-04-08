"""
Python program for merging .wav files
USAGE: (python) wav_merge.py <directory_name/path>
Note: files must be named such that they will automatically sort correctly. I.e. "01, 02, 03, .., 10, 11" so that
    sorting doesn't go: "1, 10, 11, 2, 3, 4, ..."
"""

import sys
import os
import re
import pydub


def main(directory):
    combined = merge(directory)
    combined.export("{}/combined.wav".format(directory), format="wav")
    print "\nDONE!\nmerged wav file is located in the directory you specified, and is named 'combined.wav'."
    return


def merge(dir_name):
    """
    Merges all .wav files in a given directory.
    :param dir_name: name of directory to look in (directory must be under same directory as script)
    :return: combined .wav object
    """
    dir_list = [file for file in os.listdir(dir_name) if file.endswith(".wav")]
    wavs = [pydub.AudioSegment.from_wav("{}/{}".format(dir_name, fname)) for fname in dir_list]
    combined = reduce((lambda x, y: x + y), wavs)
    return combined


if __name__ == "__main__":
    try:
        dir_name = re.sub(r'^(/|\\)', r'', sys.argv[1])
    except IndexError:
        sys.exit("\nERROR: Please specify directory of .eaf files to merge.")
    main(dir_name)
