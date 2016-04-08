# eaf_utils
This is a collection of python programs to help in reviewing and preparing ELAN .eaf transcription files. A brief descri
ption of each script is given below.

## eaf_spell_check.py
A basic spell checker for .eaf files. Especially useful if you are preparing transcriptions for forced alignment using 
FAVE or something like that. This program is meant to be run interactively in a terminal, and includes "replace all 
instances" and "skip all instances" functionality. 

* USAGE: (python) eaf_spell_check.py \<file_path\>
  
* SETUP:  
  * To use this spell-checker you will need to download and install the python wrapper for the enchant dictionary. Do 
  this by running the following command in a terminal:  
  ```pip install pyenchant```
  * Enchant only works with 32 bit python interpreters, so you will need to run eaf_spell_check.py using a 32 bit 
  python interpreter.
  
* NOTES:  
  * At this time, eaf_spell_check.py requires that the file to be checked either be in the same directory as the script 
  itself, or for an absolute path to be specified.
  * At this time, eaf_spell_check.py is only compatible with Windows operating systems.
  
* TASK LIST:  
  - [ ] create version of program compatible with UNIX-like operating systems
    
## eaf_merge.py
A tool for merging all .eaf files within a given directory. Especially useful if you need to merge a bunch of .eaf files
and don't want to use ELAN's built-in merge tool, which only lets you merge two .eaf files at a time.

* USAGE: (python) eaf_merge.py \<directory_name/path/>

* SETUP: 
  * This program debends on pydub. To install this package, enter the following command in a terminal:  
  ``` pip install pydub```
  * This program currently requires that all .eaf files in the directory to be merged have identically named 
  corresponding .wav files housed within the same directory. This is because the script needs to get the duration 
  of the corresponding .wav files to adjust the .eaf timestamps accordingly.
  
* NOTES:
  * NAME ALL FILES SO THAT THEY AUTOMATICALLY SORT CORRECTLY. This generally means name all files the same except for 
  an ordering number suffix (e.g. "file_01, file_02, ...")
  DO NOT forget to put zeros before single digit part numbers, or this script 
  will merge files in the following order: "file_1, file_10, file_11, file_2, file_3, file_4, ..., file_9"
  * Requires either that the directory to be merged is under the same directory as the script itself, or that an 
  absolute path to the directory to be merged be specified.
  * Stores the resulting .eaf file as "combined.eaf"
  * Currently only compatible with Windows operating systems.
  
* TASK LIST:  
  - [ ] create version of program compatible with UNIX-like operating systems

## wav_merge.py
A tool for merging all .wav files within a given directory. A bit quicker than merging multiple .wav files in Praat,
and a hell of a lot quicker than merging .wav files using Audacity.

* USAGE: (python) wav_merge.py \<directory_name/path/>

* SETUP: 
  * This program debends on pydub. To install this package, enter the following command in a terminal:  
  ``` pip install pydub```

* NOTES:
  * NAME ALL FILES SO THAT THEY AUTOMATICALLY SORT CORRECTLY. This generally means name all files the same except for 
  an ordering number suffix (e.g. "myfile_01, myfile_02, ...")
  DO NOT forget to put zeros before single digit part numbers, or this script 
  will merge files in the following order: "file_1, file_10, file_11, file_2, file_3, file_4, ..., file_9"
  * Requires either that the directory to be merged is under the same directory as the script itself, or that an 
  absolute path to the directory to be merged be specified.
  * Stores the resulting .wav file as "combined.wav"
  * Currently only compatible with Windows operating systems.


