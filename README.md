# DH1 voiceline renamer

Python script to let the user rename Dishonored (2012) voiceline files from cooked "Play_[...]" file names to more descriptive file names. New file names feature the line's DLC status, map name, name of the speaking character, conversation data package name and conversation nickname (if applicable), conversation index and blurb index. These file names are lengthy but they include all the information needed to quickly identify voicelines without having to use a decompiler or similar method to identify voicelines.

To be used in conjunction with [bnnm's WWiser](https://github.com/bnnm/wwiser) and [its Dishonored 1 WWname list](https://github.com/bnnm/wwiser-utils/tree/master/wwnames). Can be used on files of any extension as long as the "Play_[...]" remains intact.

## Usage
- if not yet done: use wwiser with the relevant wwnames list to generate relevant files
- use the browse button to specify an input directory where the relevant files are located
- drag and drop one or more items onto the empty slots to specify the format you want your filename(s) to be in
  - more information about each item can be found by hovering over it with your cursor
  - use the "different random example sentence" to pull new random example voicelines that follow your specified format to check if it's to your liking
  - specify details of the formats by deciding if you want to include special markers for DLC files, what Conversation names should be used, and/or what divider should be used between elements of the filename
- click rename and wait until a success/error message appears
  - Should conflicts (duplicate files, overly long filenames) occur, make your decisions on how to treat them in the relevant popup windows.

Additional information can be found by clicking the "🛈" buttons in the interface.

## Legal
This program is not associated with WWise, Dishonored or any of its rightsholders. Use at your own risk, I have no idea what I'm doing most of the time.
