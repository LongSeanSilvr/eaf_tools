"""
Program for pre-processing and spell checking ELAN .eaf files.
Author: Sean Simpson
Last Modified: 4/1/2016
"""

import re
import argparse
import enchant


# ======================================================================================================================
# Functions to replace nonstandard transcription conventions with standard conventions
# ======================================================================================================================
def pre_process(raw_text):
    """
    Applies any preprocessing that might be needed. Add in any obvious preprocessing here.
    :param raw_text: string to process
    :return: processed string
    """
    proc_text = re.sub(r'\(+[lL]augh\w*\)+', r'{LG}', raw_text)
    proc_text = re.sub(r'(?i)\(*clears? +throat\w*\)*', r'{CG}', proc_text)
    proc_text = re.sub(r'\bcos\b', "'cause", proc_text)
    proc_text = re.sub(r'(<ANNOTATION_VALUE>.*\w-)(\w.*</ANNOTATION_VALUE>)', r'\1 \2', proc_text)
    proc_text = num_hyph(proc_text)
    return proc_text


def num_hyph(rawtext):
    tens = r'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety'
    ones = r'one|two|three|four|five|six|seven|eight|nine'
    hyphenated = re.sub("(?i)({})-? *({})".format(tens, ones), r'\1-\2', rawtext)
    return hyphenated


# ======================================================================================================================
# Annotation extractor
# ======================================================================================================================
def extract_annotations(eaf_file):
    """
    Iterates through a .eaf file line by line and pulls out all annotations
    :param eaf_file: string version of an elan eaf file
    :return: list of annotations (in str form)
    """
    annotation_list = []
    for line in eaf_file.split("\n"):
        annotation_pattern = re.search(r'<ANNOTATION_VALUE>(.*)</ANNOTATION_VALUE>', line)
        if annotation_pattern is not None:
            annotation_list.append(annotation_pattern.group(1))
    return annotation_list


# ======================================================================================================================
# Spell checker
# ======================================================================================================================
def spell_check(line_list):
    """
    Checks each string in a list of strings for misspelled words
    :param line_list: list of strings to check
    :return line_correspondences: dictionary in which keys are misspelled lines and values are corrected versions
    """
    line_correspondences = {}
    auto_replace = {}
    skip = []
    enchant_dict = enchant.Dict("en_us")
    for line in line_list:
        (fixed_line, auto_replace, skip) = fix_line(line, auto_replace, skip, enchant_dict)
        if line == fixed_line:
            continue
        else:
            line_correspondences.update({line: fixed_line})
    print "\nEND OF SPELL CHECK"
    return line_correspondences


# ======================================================================================================================
# Fix found typos
# ======================================================================================================================
def fix_line(line, auto_replace, skip, enchant_dict):
    """
    Checks each word in a given line against enchantDict. Replaces unrecognized words if desired. Returns corrected line
    and updated autoreplace & skip dictionaries.
    :param line: string to be corrected
    :param auto_replace: current version of dictionary with spelling mistakes and corrections to be automatically
    applied.
    :param skip: current version of skip-word list
    :param enchant_dict: enchant dictionary object (this is generated outside of the function, so the dictionary only
    has to be generated once)
    :return: tuple with 3 items: "line", "auto_replace", and "skip". "Line" is the corrected version of the
    checked line, "auto_replace" is the dictionary object of misspellings to automatically correct, including any
    updates, and "skip" is the updated list of skip-words
    """
    words = re.split(r'[^\w\'-]', line.strip(" "))
    for word in words:
        # skip if word is blank or an incompletion
        if (word == "") or ("-" in word) or (word in skip):
            continue
        # auto-replace if word is flagged as replace_all
        elif word in auto_replace:
            badreg = r'\b{word}\b'.format(word=word)
            line = re.sub(badreg, auto_replace[word], line)
        else:
            if not enchant_dict.check(word):
                choice = raw_input("\nError: {error} \nLine: {line} \nReplace (y/n)? ".format(error=word, line=line))
                if not re.match(r'n(o)?', choice, re.IGNORECASE):
                    print "Suggestions: "
                    suggestions = {str(i + 1): item for i, item in enumerate(enchant_dict.suggest(word)[:9])}
                    for k in sorted(suggestions.keys()):
                        print "\t{}: {}".format(k, suggestions[k])
                    selection = raw_input("Enter number of a replacement above, or type your own: ")
                    if selection in suggestions:
                        replacement = suggestions[selection]
                    elif re.match("^\d+$", selection):
                        replacement = raw_input("invalid selection, try again: ")
                    else:
                        replacement = selection
                    badreg = r'\b{word}\b'.format(word=word)
                    line = re.sub(badreg, replacement, line)
                    do_for_all = raw_input("Do this for all instances (y/n)? ")
                    if not re.match(r'n(o)?', do_for_all, re.IGNORECASE):
                        auto_replace.update({word: replacement})
                else:
                    skip_all = raw_input("skip all future instances (y/n)? ")
                    if not re.match(r'n(o)?', skip_all):
                        skip.append(word)
            else:
                pass
    return line, auto_replace, skip


# ======================================================================================================================
# Replace lines in text with corrected versions
# ======================================================================================================================
def replace_lines(replace_dict, replace_text):
    """
    Takes dictionary of mistakes keyed to dictionaries of replacements and containing lines, replaces the misspelled
    word with the given replacement in the containing line, and then replaces the original line with the fixed line in
    the text.
    :param replace_dict: a dictionary of form: replacements[bad_word]{fixed_word: containing_line}
    :param replace_text: the original text in which to search and replace lines.
    :return: fixed text
    """
    fixed_text = replace_text
    for k, v in replace_dict.iteritems():
        if re.search(k, fixed_text):
            fixed_text = re.sub(k, v, fixed_text)
        else:
            print "\nCould not process line: {line}".format(line=k)
    return fixed_text


# ======================================================================================================================
# Run
# ======================================================================================================================
parser = argparse.ArgumentParser()
parser.add_argument("file")
options = parser.parse_args()

fileName = options.file
with open(fileName, "rb") as f:
    text = f.read()

processed = pre_process(text)
annotations = extract_annotations(processed)
replacements = spell_check(annotations)
fixed = replace_lines(replacements, processed)

fileNameMod = re.sub(r'(.*)\.eaf', r'\1_mod.eaf', fileName)
with open(fileNameMod, "wb") as f:
    f.write(fixed)
print '\n\nDONE!'
