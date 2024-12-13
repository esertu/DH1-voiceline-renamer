# DH1 voiceline renamer

Python script to let the user rename Dishonored (2012) voiceline files from cooked "Play_[...]" file names to more descriptive file names. New file names feature the line's DLC status, map name, name of the speaking character, conversation data package name and conversation nickname (if applicable), conversation index and blurb index. These file names are lengthy but they include all the information needed to quickly identify voicelines without having to use a decompiler or similar method to identify voicelines.

To be used in conjunction with [bnnm's WWiser](https://github.com/bnnm/wwiser) and [its Dishonored 1 WWname list](https://github.com/bnnm/wwiser-utils/tree/master/wwnames). Can be used on files of any extension as long as the "Play_[...]" remains intact.

## Usage
- if not yet done: use wwiser with the relevant wwnames list to generate relevant files
- if not yet done: install Python 3.0+
- unzip zip file from the releases somewhere, keeping the two unzipped files in one folder
- open the Dishonored 1 voiceline renamer file by double clicking it or by using the command line to navigate to it and using python to open it
- specify input directory where "Play_[...]" files are located
- specify new file formatting by following the instructions


## Legal
This program is not associated with WWise, Dishonored or any of its rightsholders. Use at your own risk, I have no idea what I'm doing most of the time.
