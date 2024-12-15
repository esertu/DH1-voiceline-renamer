import os
import sys
import shutil
import io

##################

from hashList import (returnHashList)
hashList = returnHashList()

##################

# accounting for the user using square brackets around their response
def inputF():
  text = input()
  textSanitized = text.strip()
  if textSanitized.startswith("[") == True:
    textSanitized = textSanitized[1:]
  if textSanitized.endswith("]") == True:
    textSanitized = textSanitized[:-1]
  return(textSanitized)

# checking the length of a proposed filename to make sure Windows can actually handle it
def cutFilename(finalFilename,finalFilenameFull,cutinput,fileExt,dividerinput):
  if cutinput == None:
    print(f"Alert: Windows can only handle filenames up to a certain character limit. The proposed filename {finalFilenameFull} would exceed this limit. Would you like to cut this filename down to the limit?")
    print("    [Y]es (default) (will apply this to all further incidents of overly lengthy filenames as well)")
    print("    [N]o - this will abort the script.")
    cutinput = inputF()().lower()
  if cutinput != "n":
    if cutinput != "y":
      print(f"Input \"{cutinput}\" not recognized, defaulting to yes instead. (Available correct inputs: y, n)")
    finalFilenameFull = finalFilename[:(254-(len(fileExt)+1+len(dividerinput)+4+3))] + "." + fileExt #254 minus the length of the file extension plus a period plus the length of the dividerinput plus the length of "copy" plus three placeholder characters for copy numbers
  return(finalFilenameFull,cutinput)

##################

print("DH1 voiceline renamer v1.3")

inputdir = None
inputFormat = None
dividerinput = None
packageNameInput = None
dlcformat = None
copyBehavior = None
cutinput = None
orderChosen = []
# setting variables with system arguments if applicable
if len(sys.argv) > 1:
  for argumentCaps in sys.argv[1:]:
    argument = argumentCaps.lower()
    if argument.find("-input=") != -1:
      inputdir = argument[7:]
    elif argument.find("-format=") != -1:
      inputFormat = argument[8:]
      if inputFormat.startswith("[") or inputFormat.startswith("("):
        inputFormat = inputFormat[1:]
      if inputFormat.endswith("]") or inputFormat.endswith(")"):
        inputFormat = inputFormat[:-1]
      orderChosen = inputFormat.split(",")
    elif argument.find("-convname=") != -1:
      packageNameInput = argument[10:]
    elif argument.find("-dlcformat=") != -1:
      dlcformat = argument[11:]
    elif argument.find("-overwrite=") != -1:
      copyBehavior = argument[11:]
    elif argument.find("-divider=") != -1:
      dividerinput = argument[9:]
    elif argument.find("-cut=") != -1:
      cutinput = argument[5:]
    else:
      print(f"System argument {argument} has not been recognized as a valid input and will be ignored.")

# setting input directory - this loops until a valid input directory has been found or is set to be created
inputdirset = False
while inputdirset == False:
  if inputdir == None:
    print("Please enter input directory below:")
    inputdir = input()
  if os.path.exists(inputdir):
    inputdirset = True
  else:
    inputdir = None
    print(f"Directory {inputdir} does not exist. Please try again with a different folder.")

print("---------------------------")

##################

DLCNameList = ["","","","","","","",""] #making sure the dlcnamelist is seven entries long

if len(orderChosen) == 0:
  # setting final filename formatting preferences
  print("Please enter what information you would like to include in the filenames, and in what order.")
  print("These are the items that can be included in the filename: map name, conversation data package and/or nickname, character name, conversation + blurb id number, dialogue text.")
  print("The default filename format is as follows:")
  print("Map name.Character name.Conversation data package name (Conversation nickname if applicable).Conversation if applicable.Blurb")
  print("For example: L_Ovrsr_Script.Preacher.L_OvrsrSermon_DlgData (OverseerSermon).DisConversation_6.DisConv_Blurb_17.txtp")
  print("If you'd like to abort filename formatting customization and use the default format after all, please write \"cancel\" at any time you are prompted for an input and hit enter.")

  orderOptions = ["map name","conversation name","character name","conversation and blurb id","text"]
  formatSet = False

  # checking if the user wants to customize filenames at all
  print("Customize filename formatting?")
  print("    [Y]es")
  print("    [N]o (default)")
  defaultinput = inputF().lower()
  if defaultinput == "n":
    print("Leaving formatting options default.")
    formatSet = True
  elif defaultinput == "y":
    print("Commencing formatting option setting.")
    print("")
  else:
    print(f"Input \"{defaultinput}\" not recognized, defaulting to using default filename formatting. (Available correct inputs: y, n)")
    formatSet = True
    
alldone = False
while alldone != True:
  if len(orderChosen) == 0:
    # setting the order of data in the filename
    n = 1
    while formatSet != True:
      #print(f"Slot {n} can be filled by: {', '.join(orderOptions)}")
      print(f"Slot {n} can be filled by:")
      for option in orderOptions:
        print("    " + option)
      print("Please write your choice below and hit enter, or write \"finish\" and hit enter if you've input all your choices without using all possible data inputs in your filename format:")
      choiceinput = inputF().lower()
      if choiceinput in orderOptions:
        print(f"Slot {n} will be filled by {choiceinput}.")
        orderChosen.append(choiceinput)
        n = n + 1
        orderOptions.remove(choiceinput)
        print("")
      elif choiceinput == "cancel":
        print("Aborting filename formatting customization and using the default format after all.")
        break
      elif choiceinput != "finish":
        print(f"Input \"{choiceinput}\" not recognized, please try again. (Available correct inputs: {', '.join(orderOptions)}")
      if n > 5 or choiceinput == "finish":
        formatSet = True
        break

  # setting package or conversation names if applicable
  if packageNameInput == None:
    if len(orderChosen) > 0:
      if "conversation name" in orderChosen:
        print("")
        print("Many Conversations can be referred to by multipled different names. These are Conversation file names (\"DisDialogOneShot_18\", \"DisDialogOneShot_2\"), data package names (\"L_OvrsrHintJournal_DlgData\", \"LPbFrmPrsnScrpt_DlgData\"), and for some files also oneshot nicknames (\"HintConvoBlackJournal\", \"Pub01a_Piero_First_Meeting\"). Which of these names would you like to be used?")
        print("    [D] - data package names only")
        print("    [DO] - data package names (oneshot nicknames in brackets) (default)")
        print("    [C] - Conversation file names only")
        print("    [CO] - Conversation file names (oneshot nicknames in brackets)")
        packageNameInput = inputF().lower()
        if packageNameInput == "d":
          print("Conversation names set, using data package names only.")
        elif packageNameInput == "do":
          print("Conversation names set, using data package names (with oneshot nicknames in brackets).")
        elif packageNameInput == "c":
          print("Conversation names set, using Conversation file names only.")
        elif packageNameInput == "co":
          print("Conversation names set, using Conversation file names (with oneshot nicknames in brackets).")
        elif packageNameInput == "cancel":
          print("Aborting filename formatting customization and using the default format after all.")
          orderChosen = []
        else:
          print(f"Input \"{packageNameInput}\" not recognized, defaulting to using data package names (with oneshot nicknames in brackets). (Available correct inputs: d, do, c, co)")
          packageNameInput = "do"
      
  # setting DLC name options
  if dlcformat == None:
    if len(orderChosen) > 0:
      print("")
      print("Would you like all DLC files to start with an additional slot that marks it as belonging to a DLC? Note that many DLC items already have non standardized prefixes or suffixes in their filenames to denote their belonging to a DLC, this is simply meant to better organize the files.")
      print("    [Y]es")
      print("    [N]o (default)")
      dlcinput = inputF().lower()
      if dlcinput == "y":
        print("What format would you like this additional part of the filename to have?")
        print("    [Number] - DLC05/DLC06/DLC07 (default)")
        print("    [Name] - DunwallCityTrials/TheKnifeOfDunwall/TheBrigmoreWitches")
        print("    [Abbreviation] - DCT/TKoD/TBW")
        dlcformatinput = inputF().lower()
        if dlcformatinput == "number":
          print("DLC files will be preceeded by DLC05/DLC06/DLC07.")
          dlcformat = dlcformatinput
        elif dlcformatinput == "name":
          print("DLC files will be preceeded by DunwallCityTrials/TheKnifeOfDunwall/TheBrigmoreWitches.")
          dlcformat = dlcformatinput
        elif dlcformatinput == "abbreviation":
          print("DLC files will be preceeded by DCT/TKoD/TBW.")
          dlcformat = dlcformatinput
        elif dlcformatinput == "cancel":
          print("Aborting filename formatting customization and using the default format after all.")
          orderChosen = []
        else:
          print(f"Input \"{dlcformatinput}\" not recognized, defaulting to DLC files being preceeded by DLC05/DLC06/DLC07. (Available correct inputs: number, name, abbreviation)")
          dlcformat = "number"
      elif dlcinput == "n":
        print("No additional part will be added to the filename of DLC files.")
        dlcformat = None
      else:
        print(f"Input \"{dlcinput}\" not recognized, defaulting to not adding any additional part to the filename of DLC files. (Available correct inputs: y, n)")
        dlcformat = None
        
  if dlcformat == "number" or dlcformat == "name" or dlcformat == "abbreviation":
    if dlcformat == "number":
      DLCNameList[5] = "DLC05"
      DLCNameList[6] = "DLC06"
      DLCNameList[7] = "DLC07"
    elif dlcformat == "name":
      DLCNameList[5] = "DunwallCityTrials"
      DLCNameList[6] = "TheKnifeOfDunwall"
      DLCNameList[7] = "TheBrigmoreWitches"
    elif dlcformat == "abbreviation":
      DLCNameList[5] = "DCT"
      DLCNameList[6] = "TKoD"
      DLCNameList[7] = "TBW"

  # setting the divider between data in the filename
  if dividerinput == None:
    print("")
    print("Please write your choice for the divider between slots below and hit enter. Default is .")
    dividerinput = inputF()
    if dividerinput.find("\\") != -1 or dividerinput.find("/") != -1 or dividerinput.find(":") != -1 or dividerinput.find("*") != -1 or dividerinput.find("?") != -1 or dividerinput.find("\"") != -1 or dividerinput.find("<") != -1 or dividerinput.find(">") != -1 or dividerinput.find("\\") != -1 or dividerinput.find("|") != -1:
      dividerinput = dividerinput.replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","") #removing parts of the text that can't be used as filenames
      print(f"Forbidden character detected in divider input, using the sanitized {dividerinput} instead.")
    if dividerinput.lower() == "cancel":
      print("Aborting filename formatting customization and using the default format after all.")
      orderChosen = []

  # setting everything to default values if needed
  if len(orderChosen) == 0:
    orderChosen = ["map name","character name","conversation name","conversation and blurb id"]
    packageNameInput = "do"
    dividerinput = "."
    dlcformat = None

  ##############
  
  # asking the user to confirm that the above is correct
  print("")
  print("Filename customization done, filenames will follow this format:")
  orderChosenPreview = orderChosen.copy()
  
  if "conversation name" in orderChosenPreview:
    if packageNameInput == "c":
      orderChosenPreview[orderChosenPreview.index("conversation name")] = "conversation file name"
    elif packageNameInput == "co":
      orderChosenPreview[orderChosenPreview.index("conversation name")] = "conversation file name (oneshot nickname if applicable)"
    elif packageNameInput == "d":
      orderChosenPreview[orderChosenPreview.index("conversation name")] = "conversation data package name"
    elif packageNameInput == "do":
      orderChosenPreview[orderChosenPreview.index("conversation name")] = "conversation data package name (oneshot nickname if applicable)"
    
  if dlcformat == "number":
    dlcPreview = ["DLC0X"] + orderChosenPreview
  elif dlcformat == "name":
    dlcPreview = ["DLC title"] + orderChosenPreview
  elif dlcformat == "abbreviation":
    dlcPreview = ["DLC title abbreviation"] + orderChosenPreview
  if dlcformat == None:
    print(dividerinput.join(orderChosenPreview))
  else:
    print("Base game:")
    print(dividerinput.join(orderChosenPreview))
    print("DLCs:")
    print(dividerinput.join(dlcPreview))
  
  print("Is this correct?")
  print("    [Y]es (default)")
  print("    [N]o")
  correctinput = inputF().lower()
  if correctinput == "n":
    print("Running formatting options setting again...")
  elif correctinput == "y":
    print("Formatting options setting done!")
    print("")
    alldone == True
    break
  elif correctinput == "cancel":
    print("Aborting filename formatting customization and using the default format after all.")
    aborted = True
  else:
    print(f"Input \"{correctinput}\" not recognized, defaulting to yes instead. (Available correct inputs: y, n)")
    print("Formatting options setting done!")
    print("")
    alldone == True
    break


##################

# iterating through the given input directory
filesFound = False # a boolean that stores whether any relevant files were found in this directory
for path, dirs, files in os.walk(inputdir):
  for file in files:
    fileExt = file.rsplit(".")[-1] # just the extension, should be txtp but might be different if already converted ie to mp3
    fileName = file.rsplit(".")[0] #just the filename without the .txtp extension
    
    if fileName.find("#") != -1:
      fileName = fileName[:fileName.find("#")] # "filename # dupe asdf" -> "filename"
      
    if fileName in hashList: #checking if this file is in our list of voicelines
      filesFound = True
      #...in which case we rename it
      oldFile = os.path.join(inputdir, file)
      
      #if anything wasn't gathered for this conversation, it will automatically be replaced with "[No(blah)]" in the final filename
      filename = "[NoMapname]"
      convNickname = "[NoConvNickname]"
      charName = "[NoCharName]"
      convBlurbID = "[NoConvBlurbID]"
      DLCName = None
      filenameList = []
      
      #sorting the gathered data into the correct order:
      #cutting the "file:" etc out of the data list items and sorting the data list items into the correct order for the final filename
      for item in hashList[fileName]:
        if item.startswith("file:") == True:
          filename = item.replace("file:","")
          filename = filename.strip()
          if filename != "":
            if "map name" in orderChosen:
              filenameList.insert(orderChosen.index("map name"),filename)
        elif item.startswith("conv:") == True:
          convFilename = item.replace("conv:","")
          convFilename = convFilename.strip()
          if convFilename != "":
            if "conversation name" in orderChosen:
              if packageNameInput == "c":
                if convFilename.find("(") != -1: #cutting out the (oneshot nickname) at the end if applicable
                  filenameList.insert(orderChosen.index("conversation name"),convFilename[:convFilename.find("(")-1])
                else:
                  filenameList.insert(orderChosen.index("conversation name"),convFilename)
              elif packageNameInput == "co":
                filenameList.insert(orderChosen.index("conversation name"),convFilename)
        elif item.startswith("nick:") == True:
          convNickname = item.replace("nick:","")
          convNickname = convNickname.strip()
          if convNickname != "":
            if "conversation name" in orderChosen:
              if packageNameInput == "d":
                if convNickname.find("(") != -1: #cutting out the (oneshot nickname) at the end if applicable
                  filenameList.insert(orderChosen.index("conversation name"),convNickname[:convNickname.find("(")-1])
                else:
                  filenameList.insert(orderChosen.index("conversation name"),convNickname)
              elif packageNameInput == "do":
                filenameList.insert(orderChosen.index("conversation name"),convNickname)
        elif item.startswith("char:") == True:
          charName = item.replace("char:","")
          charName = charName.strip()
          if charName != "":
            if "character name" in orderChosen:
              filenameList.insert(orderChosen.index("character name"),charName)
        elif item.startswith("id:") == True:
          newID = item.replace("id:","")
          newID = newID.strip()
          if newID != "":
            if "conversation and blurb id" in orderChosen:
              if convBlurbID != "[NoConvBlurbID]":
                convBlurbID = convBlurbID + dividerinput + newID
                filenameList[orderChosen.index("conversation and blurb id")] = convBlurbID
              else:
                filenameList.insert(orderChosen.index("conversation and blurb id"),newID)
        elif item.startswith("dlc:") == True:
          if dlcformat != None:
            DLCNumber = item.replace("dlc:dlc0","")
            DLCName = DLCNameList[int(DLCNumber)] #DLCNameList[5] = "DLC05" or DLCNameList[5] = "DunwallCityTrials" or DLCNameList[5] = "DCT"
            # this will get added to the list once parsing the hashList entry is done so it doesn't mess up the indexing of entries on the list
        elif item.startswith("text:") == True:
          if "text" in orderChosen:
            newText = item.replace("text:","").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","") #removing parts of the text that can't be used as filenames
            newText = newText.strip()
            if newText != "":
              if newText.endswith(".") == True: # ending periods are also problematic
                newText = newText[:-1]
              filenameList.insert(orderChosen.index("text"),newText)
      
      # adding this now, see above for explanation
      if DLCName != None:
        filenameList.insert(0, DLCName)
      
      # joining them all into one string divided by whatever divider was set earlier plus the txtp file ending and then joining that string with the input directory path to get the entire path of the final file
      finalFilename = dividerinput.join(filenameList)
      finalFilenameFull = finalFilename + "." + fileExt
      # checking the length of this proposed filename to make sure Windows can actually handle it
      if len(finalFilenameFull) > 254:
        finalFilenameFull,cutinput = cutFilename(finalFilename,finalFilenameFull,cutinput,fileExt,dividerinput)
      newFile = os.path.join(inputdir, finalFilenameFull)
      
      # setting what to do with copies of existing files - this might be because it's a copy of an existing voiceline or if there are already renamed files in the input directory from a previous time this script was run
      if os.path.exists(newFile):
        if (copyBehavior == None) or (copyBehavior != "oa" and copyBehavior != "ca"):
          print(f"While trying rename file {oldFile} to {finalFilenameFull}, a file with the name {finalFilenameFull} was found in the output directory. Do you want to overwrite the existing file or add \"copy[number]\" to the name of the new copy?")
          print("    [O] - overwrite existing file")
          print("    [C] - add \"copy[number]\" to the name of the new copy (default)")
          copyBehaviorInput = inputF().lower()
          if copyBehaviorInput == "o":
            print("Existing file will be overwritten.")
            copyBehavior = "o"
          elif copyBehaviorInput == "c":
            print("Adding \"copy[number]\" to the name of the new copy.")
            copyBehavior = "c"
          else:
            print(f"Input \"{copyBehaviorInput}\" not recognized, defaulting to adding \"copy[number]\" to the name of the new copy. (Available correct inputs: o, c)")
            copyBehavior = "c"
          if len(copyBehavior) == 1: # if this is true, then the copyBehavior setting was just run for the first time (or last time the user chose to have it apply only to one file)
            print("Apply this behavior to all name conflicts or just to this single file?")
            print("    [A] - apply to all")
            print("    [S] - apply to just this single file (default)")
            copyBehaviorInput = inputF().lower()
            if copyBehaviorInput == "a":
              copyBehavior = copyBehavior + "a"
            elif copyBehaviorInput == "s":
              print(f"Applying this to just this single file.")
            else:
              print(f"Input \"{copyBehaviorInput}\" not recognized, defaulting to only applying this to just this single file. (Available correct inputs: a, s)")
              
        if copyBehavior != None:
          if copyBehavior == "ca" or copyBehavior == "c":
            # if this is a copy of an existing file and the user chose to have copies renamed:
            # checking whichever number of copy it is by checking if "(filename)(divider)copy(int).txtp" exists and then using the next greatest int, ie if "IAmAFile.copy399.txtp" already exists the name of the file currently being renamed will be "IAmAFile.copy400.txtp"
            copynumberfound = False
            testingint = 1
            while copynumberfound == False:
              testingNewName = finalFilename + dividerinput + "copy" + str(testingint) + "." + fileExt
              testingNewFile = os.path.join(inputdir, testingNewName)
              if os.path.exists(testingNewFile):
                testingint = testingint + 1
              else:
                print(f"Creating copy number {testingint} of {finalFilename}...")
                newFile = testingNewFile
                copynumberfound = True
                finalFilenameFull = testingNewName
                # checking the length of this proposed filename to make sure Windows can actually handle it
                fullext = len(fileExt)+1
                fullext = fullext * -1
                if len(finalFilenameFull) > 254:
                  finalFilenameFull,cutinput = cutFilename(finalFilename,finalFilenameFull,cutinput,fileExt,dividerinput)
                  finalFilenameFull = finalFilenameFull[:fullext] + dividerinput + "copy" + str(testingint) + "." + fileExt
                  newFile = os.path.join(inputdir, finalFilenameFull)
          elif copyBehavior == "oa" or copyBehavior == "o":
            # if this is a copy of an existing file and the user chose to have copies overwrite:
            # deleting the existing file so that the new file can safely be renamed to that file's name
             print(f"Overwriting {finalFilenameFull}...")
             os.remove(newFile)
      
      # final step for this file: renaming the file to its new name
      os.rename(oldFile, newFile)
      print(f"{file} is now {finalFilenameFull}")
  


##################

print("---------------------------")

if filesFound == False:
  print(f"Alert: No relevant files were found in the directory {inputdir}. No actions were taken.")
  print("Press enter to exit.")
  input()
else:
  print("Done! Press enter to exit.")
  input()
