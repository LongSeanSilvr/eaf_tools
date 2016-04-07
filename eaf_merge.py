"""
Python program for merging .eaf files
USAGE: (python) eaf_merge.py -d "/directory_name"
    Note: directory must be in same folder as script, as of 4_6_2016.
    Note: this program currently requires that all .eaf files to be merged are named identically to their corresponding
        .wav files (except for file extension), and that .eaf and .wav files reside in the same directory.
"""

import os
import pydub
import argparse
import re

# ======================================================================================================================
# Main Functions
# ======================================================================================================================
def main():
    dir_list = ["./{}/{}".format(dir_name, file) for file in os.listdir("./{}".format(dir_name)) if
                file.endswith(".eaf")]
    combined_eaf = reduce(merge, dir_list)
    write_eaf(combined_eaf)
    copy_pfsx(dir_list[0])
    return


def merge(xname, yname):
    print "Working on {}:".format(yname)
    (xtext, ytext) = read(xname, yname)
    ytext_ids_adjusted = get_y_adj(xtext, ytext)
    new_y_text = adjust_time(ytext_ids_adjusted, xname, yname)
    x_wth_y_annos = combine_annotations(xtext, new_y_text)
    combined_text = combine_time_slots(x_wth_y_annos, new_y_text)
    finished_text = adjust_media_reference(combined_text)
    print "done with {}\n".format(yname)
    return finished_text


# ======================================================================================================================
# Adjustment Functions
# ======================================================================================================================
def get_y_adj(xtext, ytext):
    print "\tAdjusting annotation IDs..."
    x_ts_max = max_id("ts", xtext)
    x_a_max = max_id("a", xtext)
    y_annos = extract_annos(ytext)
    y_annos_ts_adjusted = id_adjust("ts", x_ts_max, y_annos)
    y_annos_both_adjusted = id_adjust("a", x_a_max, y_annos_ts_adjusted)
    y_text_adjusted = adjust_text(y_annos, y_annos_both_adjusted, ytext)
    return y_text_adjusted


def adjust_text(orig, adjusted, text):
    orig_dict = {i: anno for i, anno in enumerate(orig)}
    new_dict = {i: anno for i, anno in enumerate(adjusted)}
    for i in sorted(new_dict.keys()):
        text = re.sub(orig_dict[i], new_dict[i], text)
    return text


def id_adjust(type, id_max, annos):
    annos_id_adjusted = []
    for anno in annos:
        toks = anno.split(" ")
        tok_adjs = []
        for tok in toks:
            tok_adj = tok
            if type == "ts":
                match = re.search(r'="ts(\d+)"', tok_adj)
            elif type == "a":
                match = re.search(r'="a(\d+)"', tok_adj)
            if match is not None:
                id_num = match.group(1)
                id_num_int = int(id_num)
                id_plus_max = str(id_num_int + id_max)
                tok_adj = re.sub(r'="ts{}"'.format(id_num), r'="ts{}"'.format(id_plus_max), tok)
            tok_adjs.append(tok_adj)
        anno_adj = " ".join(tok_adjs)
        annos_id_adjusted.append(anno_adj)
    return annos_id_adjusted


def adjust_time(ytext, xfilename, yfilename):
    print "\tAdjusting annotation timestamps..."
    global total_wavetime
    if total_wavetime == 0:
        x_duration = get_wav_duration(xfilename)
        total_wavetime = x_duration

    y_times = re.findall(r'TIME_VALUE="\d+"', ytext)
    time_correspondences = {}
    for time in y_times:
        y_ms = int(re.search(r'"(\d+)"', time).group(1))
        y_ms_adj = str(y_ms + total_wavetime)
        time_new = re.sub(r'\d+', y_ms_adj, time)
        time_correspondences[time] = time_new

    ytext_time_adj = ytext
    for k in time_correspondences.keys():
        ytext_time_adj = re.sub(k, time_correspondences[k], ytext_time_adj)

    y_duration = get_wav_duration(yfilename)
    total_wavetime += y_duration

    return ytext_time_adj

def get_wav_duration(filename):
    wav_name = re.sub(r'.eaf', r'.wav', filename)
    wav = pydub.AudioSegment.from_wav(wav_name)
    duration_s = wav.duration_seconds
    duration_ms = int(duration_s * 1000)
    return duration_ms

def adjust_media_reference(text):
    adjusted = re.sub(r'<MEDIA_DESCRIPTOR MEDIA_URL=".*" MIME_TYPE', r'<MEDIA_DESCRIPTOR MEDIA_URL="ASK_on_OPEN.wav" MIME_TYPE', text)
    adjusted = re.sub(r'RELATIVE_MEDIA_URL=".*"/>', r'RELATIVE_MEDIA_URL="./combined.wav"/>', adjusted)
    return adjusted

# ======================================================================================================================
# Combination Functions
# ======================================================================================================================
def combine_annotations(xtext, ytext):
    print "\tCombining annotations with master..."
    combinedtext = xtext
    tier_ids = re.findall(r'TIER_ID="(.*)"', ytext)
    y_tier_dict = {}
    for id in tier_ids:
        try:
            y_tier_dict[id] = re.search(r'TIER_ID="{}">(.*?)</TIER>'.format(id), ytext, re.DOTALL).group(1)
        except AttributeError: # guard against empty tiers
            continue
    for id in y_tier_dict:
        m = re.search(r'(TIER_ID="{}">.*?)(</TIER>)'.format(id), combinedtext, flags=re.DOTALL)
        if m is not None:
            match = m.group(1)
        combinedtext = re.sub(r'(TIER_ID="{}">.*?)(</TIER>)'.format(id), r'\1{}\2'.format(y_tier_dict[id]),
                              combinedtext, flags=re.DOTALL)
    return combinedtext


def combine_time_slots(xtext, ytext):
    print "\tCombining time-slots with master..."
    y_time_slots = re.search(r'<TIME_ORDER>(.*)</TIME_ORDER>', ytext, flags=re.DOTALL).group(1)
    combined = re.sub(r'(<TIME_ORDER>.*)(</TIME_ORDER>)', r'\1{}\2'.format(y_time_slots), xtext, flags=re.DOTALL)
    return combined


# ======================================================================================================================
# Data-Munge-ish functions
# ======================================================================================================================
def read(x, y):
    if '\n' in x:
        xtext = x
    else:
        with open(x) as f:
            xtext = f.read()
    with open(y) as f:
        ytext = f.read()
    return xtext, ytext


def extract_annos(text):
    anno_list = [x for x in text.split("\n") if re.search(r'="ts\d+"', x) is not None]
    return anno_list


def max_id(type, file_text):
    if type == "a":
        pat = r'="a(\d+)"'
    elif type == "ts":
        pat = r'="ts(\d+)"'
    id_list = re.findall(pat, file_text)
    numlist = [int(id) for id in id_list]
    max_id = max(numlist)
    return max_id

def copy_pfsx(eaf_file):
    pfsx_name = re.sub(r'.eaf','.pfsx',eaf_file)
    with open(pfsx_name, "rb") as f:
        pfsx_template = f.read()
    with open("./{}/{}".format(dir_name, "combined.pfsx"), "wb") as f:
        f.write(pfsx_template)
    return

def write_eaf(eaf_file):
    with open("./{}/{}".format(dir_name, "combined.eaf"), "wb") as f:
        f.write(eaf_file)
# ======================================================================================================================
# Run
# ======================================================================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", action="store", dest="dir", help="directory of .wav files to merge. (will "
                                                                              "ignore other filetypes in directory")
    options = parser.parse_args()
    dir_name = options.dir
    total_wavetime = 0
    main()
