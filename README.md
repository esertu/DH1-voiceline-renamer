# DH1 voiceline renamer

Python script to let the user rename Dishonored (2012) voiceline files from cooked "Play_[...]" file names to more descriptive file names. New file names feature the line's DLC status, map name, name of the speaking character, conversation data package name and conversation nickname (if applicable), conversation index and blurb index. These file names are lengthy but they include all the information needed to quickly identify voicelines without having to use a decompiler or similar method to identify voicelines.

To be used in conjunction with [bnnm's WWiser](https://github.com/bnnm/wwiser) and [its Dishonored 1 WWname list](https://github.com/bnnm/wwiser-utils/tree/master/wwnames). Can be used on files of any extension as long as the "Play_[...]" remains intact.

## Usage
- if not yet done: use wwiser with the relevant wwnames list to generate relevant files
- if not yet done: install Python 3.0+
- unzip zip file from the releases somewhere, keeping the two unzipped files in one folder
- open the Dishonored 1 voiceline renamer file by double clicking it or by using the command line to navigate to it and using python to open it
- available system arguments: (use by navigating the command line to the folder where you unzipped the release file, then typing i.e. "python "Dishonored 1 voiceline renamer v1.1.py" -dlcformat=number -divider=.)
  - -input= : path of the folder containing your Play_[...] files. Add quotation marks around the folder path if path contains spaces.
  - -divider= : the symbol(s) you want to use to divide data in your filenames, i.e. -divider=. would lead to a filename like EliteGuard_A.DisConversation_1.DisBlurb_2
  - -convName= : [D] data package names only, [DO] data package names (oneshot nicknames in brackets) (default), [C] Conversation file names only, [CO] Conversation file names (oneshot nicknames in brackets) - Many Conversations can be referred to by multipled different names. These are Conversation file names ("DisDialogOneShot_18", "DisDialogOneShot_2"), data package names ("L_OvrsrHintJournal_DlgData", "LPbFrmPrsnScrpt_DlgData"), and for some files also oneshot nicknames ("HintConvoBlackJournal", "Pub01a_Piero_First_Meeting"). Argument determines which one(s) of these will be used in the filename.
  - -DLCFormat= : [Number] DLC05/DLC06/DLC07 (default), [Name] DunwallCityTrials/TheKnifeOfDunwall/TheBrigmoreWitches, [Abbreviation] DCT/TKoD/TBW - if you would like DLC files to carry a prefix denoting which DLC they're from, this argument will determine what format that prefix will be.
  - -overwrite= : [OA] overwrite all duplicate files, [CA] append "copy[number]" to the name of every new copy (default) - whether you'd like duplicate filenames to be overwritten by any successive files of the same name or want to append "copy[number]" to the end of any successive file of the same name.
  - -cut= : [y]es/[n]o - whether you want filenames that are too long for Windows to handle to be abridged by deleting any characters after the filename size limit. "N" results in the renamer aborting when encountering a filename that exceeds the filename size limit.
  - -format= : list containing any of the following data in the order you would like them to appear in the filename as: "map name", "character name", "conversation name", "conversation and blurb id", "text"
    - "map name": what file this line originates from, i.e. "L_Ovrsr_Back_Script" (High Overseer's Office Backyard), "L_DLC07_Coldridge_Script" (The Brigmore Witches: Coldridge Prison)
    - "character name": what character speaks this line as designated in the files, i.e. "TheOutsider", "DLC06_Butcher_A", "HeartGadget"
    - "conversation name": what Conversation package this originates from, can contain Conversation file names ("DisDialogOneShot_18", "DisDialogOneShot_2"), data package names ("L_OvrsrHintJournal_DlgData", "LPbFrmPrsnScrpt_DlgData"), and for some files also oneshot nicknames ("HintConvoBlackJournal", "Pub01a_Piero_First_Meeting").
    - "conversation and blurb id": what Conversation and Blurb ID this line carries, i.e. "DisConversation_6, DisBlurb_15"
    - "text": dialogue text, i.e. "We're not taking this one alive!", "I've learned that our choices always matter to someone, somewhere.". Note that due to filename size limitations it's not possible to fit all dialogue text into all filenames, and due to filename character restrictions many special characters like "?" and "*" will be deleted when text is used in the filename.
- specify input directory where "Play_[...]" files are located
- specify new file formatting by following the instructions


## Legal
This program is not associated with WWise, Dishonored or any of its rightsholders. Use at your own risk, I have no idea what I'm doing most of the time.
