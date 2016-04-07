# eaf_utils
This is a collection of python programs to help in reviewing and preparing ELAN .eaf transcription files. A brief description of each script is given below.

## eaf_spell_check.py
A basic spell checker for .eaf files. Especially useful if you are preparing transcriptions for forced alignment using FAVE or something like that. This program is meant to be run interactively in a terminal, and includes "replace all instances" and "skip all instances" functionality. 

* USAGE: (python) eaf_spell_check.py <file>
* NOTES: 
  *At this time, eaf_spell_check.py requires that the file to be checked either be in the same directory as the script itself, or for an absolute path to be specified.
  *Because this program depends on PyEnchant, it can only be run using a 32 bit python interpreter.
