"""
Script for automatically formatting list of unknown words from FAVE aligner into arpabet transcriptions
"""

import re, argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", action="store", dest="input")
    parser.add_argument("-o", "--output", action="store", dest="output")
    options = parser.parse_args()

    arpa_dict = scan_text(options.input)
    with open(options.output,"wb") as f:
        f.write(arpa_dict)
    return

def scan_text(in_file):
    with open(in_file,"rb") as f:
        in_text = f.read()
    lines = re.split(r'\r\n', in_text)
    arpa_lines = [arpa(line) for line in lines]
    arpa_text = "\n".join(arpa_lines)
    return arpa_text

def arpa(line):
    no_sugg = r'\S+\t\t\t.*'
    one_sugg = r'(\S+)\t(([^\s,]+ ?)+)\t\S+\t.*'
    multi_sugg = r'\S+\t(((\S+\s)+),)+((\S+\s)+)'

    one_match = re.match(one_sugg, line)
    if one_match:
        line = "{}\t{}".format(one_match.group(1),one_match.group(2))
    return line

if __name__ == "__main__":
    main()