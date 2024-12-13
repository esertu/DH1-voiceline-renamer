import os
import sys
import shutil
import io

##################

from hashList import (returnHashList)
hashList = returnHashList()

##################

print("DH1 voiceline renamer v1.0")

# setting input directory - this loops until a valid input directory has been found or is set to be created
inputdirset = False
while inputdirset == False:
  print("Please enter input directory below:")
  inputdir = input()
  if os.path.exists(inputdir):
    inputdirset = True
  else:
    print(f"Directory {inputdir} does not exist. Please try again with a different folder.")

print("---------------------------")

##################

# setting final filename formatting preferences
print("Please enter how you would like the filenames to be formatted. There are four items that will be included in the filename: map name, conversation nickname, character name, conversation + blurb id number. You can also specify what character(s) you would like to be used as a divider between these items.")
print("")
print("The default filename format is as follows:")
print("Map name.Conversation data package name (Conversation nickname if applicable).Character name.Conversation if applicable.Blurb")
print("For example: L_Ovrsr_Script.L_OvrsrSermon_DlgData (OverseerSermon).Preacher.DisConversation_6.DisConv_Blurb_17.txtp")
print("")
print("If you'd like to abort filename formatting customization and use the default format after all, please write \"cancel\" at any time you are prompted for an input and hit enter.")
print("")

alldone = False
aborted = False
DLCNameList = ["","","","","","","",""] #making sure the dlcnamelist is seven entries long
while alldone != True:
  orderOptions = ["map name","conversation nickname","character name","conversation and blurb id"]
  orderChosen = []
  wantsToCustomize = False
  alldone = False
  dlcformat = None
  aborted = False
  print("Customize filename formatting? [Y]es/[n]o (default)")
  defaultinput = input().lower()
  if defaultinput == "n":
    print("Leaving formatting options default.")
  elif defaultinput == "y":
    print("Commencing formatting option setting.")
    wantsToCustomize = True
  else:
    print("Input not recognized, defaulting to using default filename formatting.")
  if wantsToCustomize == True:
    n = 1
    done = False
    
    while done != True:
      print(f"Slot {n} can be filled by: {orderOptions}")
      print("Please write your choice below and hit enter:")
      choiceinput = input().lower()
      if choiceinput in orderOptions:
        print(f"Slot {n} will be filled by {choiceinput}.")
        orderChosen.append(choiceinput)
        n = n + 1
        orderOptions.remove(choiceinput)
        print("")
      elif choiceinput == "cancel":
        print("Aborting filename formatting customization and using the default format after all.")
        done = True
        aborted = True
        break
      else:
        print(f"Input \"{choiceinput}\" not recognized, please try again.")
      if n > 4:
        done = True
        break
    
    if aborted != True:
      print("Would you like to use data package names or Conversation file names as Conversation names? For example, one conversation from the Overseer map can be either named \"L_OvrsrHintJournal_DlgData\" (data package name) or \"DisDialogOneShot_18\" (file name). As another example, one conversation from the Pub can be either named \"Pub05a_Lydia_DlgData\" (data package name) or \"DisDialogOneShot_10\" (file name). [D]ata package names (default)/[C]onversation file names")
      packageNameInput = input().lower()
      if packageNameInput == "d":
        print("Data package names will be used as Conversation names.")
      elif packageNameInput == "c":
        print("Conversation file names will be used as Conversation names.")
      elif packageNameInput == "cancel":
        print("Aborting filename formatting customization and using the default format after all.")
        aborted = True
      else:
        print(f"Input \"{packageNameInput}\" not recognized, defaulting to using data package names.")
        packageNameInput = "d"
    
    if aborted != True:
      print("Please write your choice for the divider between slots below and hit enter. Default is .")
      dividerinput = input()
      if dividerinput.lower() == "cancel":
        print("Aborting filename formatting customization and using the default format after all.")
        aborted = True
        
    if aborted != True:
      print("Would you like all DLC files to start with an additional slot that marks it as belonging to a DLC? For example, this would turn .... into ... Note that many DLC items already have non standardized prefixes or suffixes in their filenames to denote their belonging to a DLC, this is simply meant to better organize the files. [Y]es/[n]o (default)")
      dlcinput = input().lower()
      done = False
      if dlcinput == "y":
        print("What format would you like this additional part of the filename to have? [Number] - DLC05/DLC06/DLC07 (default). [Name] - DunwallCityTrials/TheKnifeOfDunwall/TheBrigmoreWitches. [Abbreviation] - DCT/TKoD/TBW")
        dlcformatinput = input().lower()
        if dlcformatinput == "number":
          print("DLC files will be preceeded by DLC05/DLC06/DLC07.")
          dlcformat = dlcformatinput
          DLCNameList[5] = "DLC05"
          DLCNameList[6] = "DLC06"
          DLCNameList[7] = "DLC07"
        elif dlcformatinput == "name":
          print("DLC files will be preceeded by DunwallCityTrials/TheKnifeOfDunwall/TheBrigmoreWitches.")
          dlcformat = dlcformatinput
          DLCNameList[5] = "DunwallCityTrials"
          DLCNameList[6] = "TheKnifeOfDunwall"
          DLCNameList[7] = "TheBrigmoreWitches"
        elif dlcformatinput == "abbreviation":
          print("DLC files will be preceeded by DCT/TKoD/TBW.")
          dlcformat = dlcformatinput
          DLCNameList[5] = "DCT"
          DLCNameList[6] = "TKoD"
          DLCNameList[7] = "TBW"
        elif dlcformatinput == "cancel":
          print("Aborting filename formatting customization and using the default format after all.")
          aborted = True
        else:
          print(f"Input \"{dlcinput}\" not recognized, defaulting to DLC files being preceeded by DLC05/DLC06/DLC07.")
          dlcformat = "number"
          DLCNameList[5] = "DLC05"
          DLCNameList[6] = "DLC06"
          DLCNameList[7] = "DLC07"
      elif dlcinput == "n":
        print("No additional part will be added to the filename of DLC files.")
        dlcformat = None
      else:
        print(f"Input \"{dlcinput}\" not recognized, defaulting to not adding any additional part to the filename of DLC files.")
        dlcformat = None
  else:
    orderChosen = ["map name","conversation nickname","character name","conversation and blurb id"]
    packageNameInput = "d"
    dividerinput = "."
    dlcformat = "number"
    DLCNameList[5] = "DLC05"
    DLCNameList[6] = "DLC06"
    DLCNameList[7] = "DLC07"
  
  print("")
  print("Final settings: filenames will follow this format:")
  if dlcformat == "number":
    print("Base game:")
    print(orderChosen[0] + dividerinput + orderChosen[1] + dividerinput + orderChosen[2] + dividerinput + orderChosen[3])
    print("DLCs:")
    print("DLC0X" + dividerinput + orderChosen[0] + dividerinput + orderChosen[1] + dividerinput + orderChosen[2] + dividerinput + orderChosen[3])
  elif dlcformat == "name":
    print("Base game:")
    print(orderChosen[0] + dividerinput + orderChosen[1] + dividerinput + orderChosen[2] + dividerinput + orderChosen[3])
    print("DLCs:")
    print("DLC title" + dividerinput + orderChosen[0] + dividerinput + orderChosen[1] + dividerinput + orderChosen[2] + dividerinput + orderChosen[3])
  elif dlcformat == "abbreviation":
    print("Base game:")
    print(orderChosen[0] + dividerinput + orderChosen[1] + dividerinput + orderChosen[2] + dividerinput + orderChosen[3])
    print("DLCs:")
    print("DLC title abbreviation" + dividerinput + orderChosen[0] + dividerinput + orderChosen[1] + dividerinput + orderChosen[2] + dividerinput + orderChosen[3])
  else:
    print(orderChosen[0] + dividerinput + orderChosen[1] + dividerinput + orderChosen[2] + dividerinput + orderChosen[3])
  print("Is this correct? [Y]es (default)/[n]o")
  correctinput = input().lower()
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
    print(f"Input \"{correctinput}\" not recognized, defaulting to yes instead.")
    print("Formatting options setting done!")
    print("")
    alldone == True
    break

if aborted == True:
    orderChosen = ["map name","conversation nickname","character name","conversation and blurb id"]
    packageNameInput = "d"
    dividerinput = "."
    dlcformat = "number"
    DLCNameList[5] = "DLC05"
    DLCNameList[6] = "DLC06"
    DLCNameList[7] = "DLC07"

##################

# iterating through the given input directory
copyBehavior = None
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
      
      #sorting the gathered data into the correct order:
      #step one: cutting the "file:" etc out of the data list items
      for item in hashList[fileName]:
        if item.startswith("file:") == True:
          filename = item.replace("file:","")
        elif item.startswith("conv:") == True:
          convFilename = item.replace("conv:","")
        elif item.startswith("nick:") == True:
          convNickname = item.replace("nick:","")
        elif item.startswith("char:") == True:
          charName = item.replace("char:","")
        elif item.startswith("id:") == True:
          if convBlurbID != "[NoConvBlurbID]":
            convBlurbID = convBlurbID + dividerinput + item.replace("id:","")
          else:
            convBlurbID = item.replace("id:","")
        elif item.startswith("dlc:") == True:
          DLCNumber = item.replace("dlc:dlc0","")
          if dlcformat != None:
            DLCName = DLCNameList[int(DLCNumber)] #DLCNameList[5] = "DLC05" or DLCNameList[5] = "DunwallCityTrials" or DLCNameList[5] = "DCT"
            
      #step two: sorting the data list items into the correct order for the final filename
      #orderChosen is for example ["map name","conversation nickname","character name","conversation and blurb id"]
      filenameList = ["","","",""]
      filenameList[orderChosen.index("map name")] = filename
      if packageNameInput == "c":
        filenameList[orderChosen.index("conversation nickname")] = convFilename
      else:
        filenameList[orderChosen.index("conversation nickname")] = convNickname
      filenameList[orderChosen.index("character name")] = charName
      filenameList[orderChosen.index("conversation and blurb id")] = convBlurbID
      
      # adding the DLC name to the front of the list if needed
      if DLCName != None:
        filenameList.insert(0, DLCName)
      
      # joining them all into one string divided by whatever divider was set earlier plus the txtp file ending and then joining that string with the input directory path to get the entire path of the final file
      finalFilename = dividerinput.join(filenameList)
      finalFilenameFull = finalFilename + "." + fileExt
      newFile = os.path.join(inputdir, finalFilenameFull)
      
      # setting what to do with copies of existing files - this might be because it's a copy of an existing voiceline or if there are already renamed files in the input directory from a previous time this script was run
      if os.path.exists(newFile):
        if (copyBehavior == None) or (copyBehavior != "oa" and copyBehavior != "ca"):
          print(f"While trying rename file {oldFile} to {finalFilenameFull}, a file with the name {finalFilenameFull} was found in the output directory. Do you want to overwrite the existing file or add \"copy[number]\" to the name of the new copy?")
          print("[o] - overwrite existing file")
          print("[c] - add \"copy[number]\" to the name of the new copy (default)")
          copyBehaviorInput = input().lower()
          if copyBehaviorInput == "o":
            print("Existing file will be overwritten.")
            copyBehavior = "o"
          elif copyBehaviorInput == "c":
            print("Adding \"copy[number]\" to the name of the new copy.")
            copyBehavior = "c"
          else:
            print(f"Input \"{copyBehaviorInput}\" not recognized, defaulting to adding \"copy[number]\" to the name of the new copy.")
            copyBehavior = "c"
          if len(copyBehavior) == 1: # if this is true, then the copyBehavior setting was just run for the first time (or last time the user chose to have it apply only to one file)
            print("Apply this behavior to all name conflicts or just to this single file?")
            print("[a] - apply to all")
            print("[s] - apply to just this single file (default)")
            copyBehaviorInput = input().lower()
            if copyBehaviorInput == "a":
              copyBehavior = copyBehavior + "a"
            elif copyBehaviorInput == "s":
              print(f"Applying this to just this single file.")
            else:
              print(f"Input \"{copyBehaviorInput}\" not recognized, defaulting to only applying this to just this single file.")
              
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
  print(f"Warning: No relevant files were found in the directory {inputdir}. No actions were taken.")
  print("Press enter to exit.")
  input()
else:
  print("Done! Press enter to exit.")
  input()