versionNumber = "1.4"
print(f"DH1 voiceline renamer v{versionNumber}")

import os
import sys
import random
from threading import Timer
from tkinter import font
from sortedcontainers import SortedDict

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

##################

# importing the hashList
from hashList import (returnHashList)
hashList = returnHashList()

##################

# setting up the application icon
# https://stackoverflow.com/questions/42474560/pyinstaller-single-exe-file-ico-image-in-title-of-tkinter-main-window
datafile = "extremelyprofessionalicon_ef9_icon.ico"
if not hasattr(sys, "frozen"):
    datafile = os.path.join(os.path.dirname(__file__), datafile)
else:
    datafile = os.path.join(sys.prefix, datafile)

def resource_path(relative_path):    
  try:       
      base_path = sys._MEIPASS
  except Exception:
      base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

##################

# establishing the basics of the GUI
root = Tk()
root.title(f"DH1 voiceline renamer v{versionNumber}")
root.iconbitmap(default=resource_path(datafile))

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

##################

# establishing variables
# things for the formatting Canvas
dividerBoxes = []
dividerBoxTexts = []
boxes = []
dividerinput = StringVar()
dividerinput.set(".")
dividerBoxWidth = IntVar()
dividerBoxWidth.set(len(dividerinput.get())*8)
savedDLCFrameXPosition = 0
savedDLCFrameYPosition = 0

# how large the boxes on the formatting Canvas are
boxWidth = IntVar()
boxWidth.set(100)
boxHeight = IntVar()
boxHeight.set(40)

# where the empty boxes that get filled are located
boxX = boxWidth.get()/2
boxXOffset = 20
boxY = boxHeight.get()/2
boxYOffset = 10

# how many empty boxes/ slots there are that cards can be fitted into
maxSlots = 5
filledSlots = {}
for i in range(0, maxSlots+1):
  filledSlots[i] = ""

# assorted variables
inputDir = StringVar()
exampleText = StringVar()
exampleUnusedText = StringVar()
hashListList = list(hashList.items()) #for choosing a random example
forbiddenDividers = ["\\","/",":","*","?","\"","<",">","|"] #characters that can't be used in the divider
orderChosen = []
DLCNameList = ["","",""]
packageNameInput = StringVar()
packageNameInput.set("do")

#####################

# styles
defaultFontDict = font.nametofont('TkDefaultFont').actual()
#'TkDefaultFont' is something like {'family': 'Segoe UI', 'size': 9, 'weight': 'normal', 'slant': 'roman', 'underline': 0, 'overstrike': 0}
italicFont = (defaultFontDict["family"],defaultFontDict["size"],"italic",defaultFontDict["weight"])
bigFont = (defaultFontDict["family"],defaultFontDict["size"]+5,defaultFontDict["weight"])
cardInfoFont = ("Segoe UI",9) # hard coding this so we can set the size of the box a bit better

s = ttk.Style()
s.configure('test.TFrame', background='red')
s.configure('convertButton.TButton',font =bigFont, foreground = 'green')
s.configure('italic.TLabel',font = italicFont, foreground = 'gray10')
s.configure('redText.TLabel', foreground = 'red')

##################

# functions

# letting the user specify an input directory
dialogue = ""
def openDirs(*args):
  dialogue = filedialog.askdirectory()
  inputDir.set(dialogue)
  convertButtonCheck() # checking if we can enable the run button

# setting an example sentence
badRandos = [] #a list of random numbers that we know didn't work
exampleFound = False
randomNumber = 0
def setExample(*args):
  # finding a random line
  global exampleFound
  global randomNumber
  while exampleFound != True:
    randomNumber = random.randrange(0, len(hashListList))
    if randomNumber not in badRandos:
      for key in hashListList[randomNumber]:
        value = hashListList[randomNumber][1]
        for item in value:
          #making sure none of the entries are empty so it's an actually useful example
          #ie this one wouldn't be useful: "Play_EA7832C5035524781EA4A10B0F43D01A": ['file:Shared', 'nick:Dlg_HeartGadget', 'conv:', 'char:HeartGadget', 'id:DisConv_Blurb_329', 'text:He feeds a stray dog every night.  He named her Billy.'],
          if item.strip().endswith(":"):
            badRandos.append(item)
            break
          elif item.find("text:") != -1:
            exampleFound = True
            
  # running the conversion process on the found line and then setting the two relevant StringVars
  [finalFilename,finalFilenameUnused]=nameConvert(hashListList[randomNumber][0])
  exampleText.set(finalFilename)
  exampleUnusedText.set(finalFilenameUnused)


# this just reruns the above setExample function for a new randomized example sentence
def resetExample(*args):
  global exampleFound
  exampleFound = False
  setExample()


# converting a hashed Play_... name into a usable name in the user's specified format
filesFound = False
fileExt = ""
def nameConvert(file):
  global fileExt
  if "." in file:
    fileExt = file.rsplit(".")[-1] # just the extension, should be txtp but might be different if already converted ie to mp3
    fileName = file.rsplit(".")[0] #just the filename without the .txtp extension
  else:
    fileExt = ""
    fileName = file
  
  if fileName.find("#") != -1:
    fileName = fileName[:fileName.find("#")] # "filename # dupe asdf" -> "filename"
    
  # if this file is in our list of voicelines we rename it
  if fileName in hashList:
    global filesFound
    filesFound = True
    
    # saving the original file name for the later renaming process (done in a different function)
    global oldFile
    if fileExt != "":
      oldFile = os.path.join(inputDir.get(), file)
    else:
      oldFile = ""
    
    #if anything wasn't gathered for this conversation, it will automatically be replaced with "[No(blah)]" in the final filename, therefore we set everything to those as defaults here
    filename = "[NoMapname]"
    convNickname = "[NoConvNickname]"
    charName = "[NoCharName]"
    convBlurbID = "[NoConvBlurbID]"
    DLCName = None
    filenameDict = {}
    filenameUnusedDict = {}
  
    global orderChosen
    orderNotChosen = ["dlc","file","char","convNames","id","text"]
  
    #sorting the gathered data into the correct order:
    #cutting the "file:" etc out of the data list items and sorting the data list items into the correct order for the final filename
    for item in hashList[fileName]:
      thisMarker = ""
      # step 1: cutting out the marker
      for marker in ["file","conv","nick","char","id","dlc","text"]:
        if item.startswith(marker) == True:
          thisMarker = marker
          newItem = item.replace(marker + ":","")
          newItem = newItem.strip()
          break
      #step 2: checking if this actually yielded anything
      if newItem != "":
        #step 3: modifying if needed - a few entries need further processing, which we do here
        if thisMarker == "id":
          if convBlurbID == "[NoConvBlurbID]":
            convBlurbID = [newItem]
          else:
            convBlurbID.append(newItem)
            newItem = convBlurbID
            
        elif thisMarker == "dlc":
          DLCNumber = newItem.replace("dlc0","")
          DLCNameList = []
          if dlcFormatVar.get().find("DLC05") != -1:
            DLCNameList = ["DLC05","DLC06","DLC07"]
          elif dlcFormatVar.get().find("Dunwall") != -1:
            DLCNameList = ["DunwallCityTrials","TheKnifeOfDunwall","TheBrigmoreWitches"]
          elif dlcFormatVar.get().find("DCT") != -1:
            DLCNameList = ["DCT","TKoD","TBW"]
          newItem = DLCNameList[int(DLCNumber)-5]
          
        elif thisMarker == "text":
          newItem = newItem.replace("text:","").replace("\\","").replace("/","").replace(":","").replace("*","").replace("?","").replace("\"","").replace("<","").replace(">","").replace("|","") #removing parts of the text that can't be used as filenames
          newItem = newItem.strip()
          while newItem.endswith(".") == True: # ending periods are also problematic
            newItem = newItem[:-1]
         
        #step 4: inserting it at the right spot in the list (except for convNames and ids, which get treated specially)
        if thisMarker == "id":
          if thisMarker in orderChosen:
            filenameDict[orderChosen.index(thisMarker)] =  dividerinput.get().join(convBlurbID)
          else:
            filenameUnusedDict[orderNotChosen.index(thisMarker)] =  ", ".join(convBlurbID)
            
        # all markers that aren't conv or nick and id
        elif thisMarker != "conv" and thisMarker != "nick":
          if thisMarker in orderChosen:
            if thisMarker != "dlc" or (thisMarker == "dlc" and toggleDLC.get() == True): #dlc doesn't get included if the toggle isn't set to on
              filenameDict[orderChosen.index(thisMarker)] = newItem
          else:
            if thisMarker != "dlc" or (thisMarker == "dlc" and toggleDLC.get() == True): #dlc doesn't get included if the toggle isn't set to on
              filenameUnusedDict[orderNotChosen.index(thisMarker)] = newItem
        
        # convNames get treated a bit differently since there are two options for its slot, conv and nick
        else: # this hits if thisMarker == "conv" or thisMarker == "nick"
          if "convNames" in orderChosen:
            # if we want Conversation names (with or without nicknames) in the filename
            if packageNameInput.get() == "c" or packageNameInput.get() == "co":
              if thisMarker == "nick":
                filenameUnusedDict[orderNotChosen.index("convNames")] = newItem
              else:
                if packageNameInput.get() == "c":
                  # cutting out the nickname if it's not needed
                  if newItem.find("(") != -1:
                    filenameDict[orderChosen.index("convNames")] = newItem[:newItem.rfind("(")-1].strip()
                  else:
                    filenameDict[orderChosen.index("convNames")] = newItem
                else:
                  filenameDict[orderChosen.index("convNames")] = newItem
                  
            # if we want data package names (with or without nicknames) in the filename
            if packageNameInput.get() == "d" or packageNameInput.get() == "do":
              if thisMarker == "conv":
                filenameUnusedDict[orderNotChosen.index("convNames")] = newItem
              else:
                if packageNameInput.get() == "d":
                  # cutting out the nickname if it's not needed
                  if newItem.find("(") != -1:
                    filenameDict[orderChosen.index("convNames")] = newItem[:newItem.rfind("(")-1].strip()
                  else:
                    filenameDict[orderChosen.index("convNames")] = newItem
                else:
                  filenameDict[orderChosen.index("convNames")] = newItem
          else:
            # if neither conv nor nick are in the list of used strings we need to include them both so we only insert directly once, the next time we just append it to the string we'd inserted the first time around
            if orderNotChosen.index("convNames") in filenameUnusedDict:
              filenameUnusedDict[orderNotChosen.index("convNames")] = filenameUnusedDict[orderNotChosen.index("convNames")] + dividerinput.get() + newItem
            else:
              filenameUnusedDict[orderNotChosen.index("convNames")] = newItem
            
    # sorting the dicts and then joining them all into one string divided by whatever divider was set earlier
    # the actual filename we want to rename the file to
    global finalFilename
    filenameList = []
    #https://stackoverflow.com/questions/9001509/how-do-i-sort-a-dictionary-by-key
    sortedFilenameDict = SortedDict(filenameDict)
    for item in sortedFilenameDict:
      filenameList.append(sortedFilenameDict[item])
    finalFilename = dividerinput.get().join(filenameList)
    
    # any element that went unused in the newly determined filename
    global finalFilenameUnused
    filenameUnusedList = []
    sortedFilenameUnusedDict = SortedDict(filenameUnusedDict)
    for item in sortedFilenameUnusedDict:
      filenameUnusedList.append(sortedFilenameUnusedDict[item])
    finalFilenameUnused = ", ".join(filenameUnusedList)
    
    return([finalFilename,finalFilenameUnused])


# letting the user choose which Conversation name (conversation name/ data package names) they want
def packageNameBoxChose(*args):
  if packageNameVar.get() == packageNameBox['values'][0]:
    packageNameInput.set("d") # data package names
  elif packageNameVar.get() == packageNameBox['values'][1]:
    packageNameInput.set("do") # data package names (oneshot nicknames in brackets)
  elif packageNameVar.get() == packageNameBox['values'][2]:
    packageNameInput.set("c") # Conversation names
  elif packageNameVar.get() == packageNameBox['values'][3]:
    packageNameInput.set("co") # Conversation names (oneshot nicknames in brackets)
  setExample() # rerunning the example formatter

######################

# popup window: duplicate copy about to be created, ask how to proceed
copyDecision = StringVar()
applyToAllCopy = BooleanVar()
applyToAllCopy.set(False)
def alertWindowCopy(fileName):
  ttk.Entry(root)   # something to interact with
  dlgCopy = Toplevel(root)
  dlgCopy.iconbitmap(default=resource_path(datafile))
  
  dlgFCopy = ttk.Frame(dlgCopy)
  dlgFCopy.grid(column=0, row=0, sticky=(N, W, E, S))
      
  def decisionFCopy(decision):
    if decision == "overwrite":
      copyDecision.set("overwrite")
    elif decision == "copymarker":
      copyDecision.set("copymarker")
    else:
      copyDecision.set("skip")
      
    # destroy alert window
    dlgCopy.grab_release()
    dlgCopy.destroy()

  ttk.Label(dlgFCopy, text=f"Alert:",wraplength=400,justify="center").grid(column=1, columnspan=3, row=0)
  ttk.Label(dlgFCopy, text=f"Output file",wraplength=400,justify="center").grid(column=1, columnspan=3, row=1)
  ttk.Label(dlgFCopy, text=f"{fileName}",wraplength=400,justify="center",style="italic.TLabel").grid(column=1, columnspan=3, row=2)
  ttk.Label(dlgFCopy, text=f"already exists, please input how to proceed.",wraplength=400,justify="center").grid(column=1, columnspan=3, row=3)
  ttk.Checkbutton(dlgFCopy, text='Apply decision to all duplicate files',variable=applyToAllCopy,onvalue=True, offvalue=False).grid(column=1, columnspan=3, row=4)
  ttk.Button(dlgFCopy, text="Skip this file", command=lambda:decisionFCopy("skip")).grid(column=1, row=5)
  ttk.Button(dlgFCopy, text="Overwrite this file", command=lambda:decisionFCopy("overwrite")).grid(column=2, row=5)
  ttk.Button(dlgFCopy, text="Add \"copy[number]\" to the name of the new file", command=lambda:decisionFCopy("copymarker")).grid(column=3, row=5)

  for child in dlgFCopy.winfo_children():
    child.grid_configure(padx=5, pady=5)
    
  dlgCopy.protocol("WM_DELETE_WINDOW", lambda:decisionFCopy("skip")) # intercept close button
  dlgCopy.transient(root)   # dialog window is related to main
  dlgCopy.wait_visibility() # can't grab until window appears, so we wait
  dlgCopy.grab_set()        # ensure all input goes to our window
  dlgCopy.wait_window()     # block until window is destroyed


# popup window: file about to be created has a filename that is too long for Windows to handle, ask how to proceed
lengthDecision = StringVar()
applyToAllLength = BooleanVar()
applyToAllLength.set(False)
def alertWindowLength(fileName):
  ttk.Entry(root)   # something to interact with
  dlgLength = Toplevel(root)
  dlgLength.iconbitmap(default=resource_path(datafile))
  
  dlgFLength = ttk.Frame(dlgLength)
  dlgFLength.grid(column=0, row=0, sticky=(N, W, E, S))
      
  def decisionFLength(decision):
    if decision == "continue":
      lengthDecision.set("continue")
    else:
      lengthDecision.set("skip")
      
    # destroy alert window
    dlgLength.grab_release()
    dlgLength.destroy()

  ttk.Label(dlgFLength, text=f"Alert:",wraplength=400,justify="center").grid(column=1, columnspan=2, row=0)
  ttk.Label(dlgFLength, text=f"Windows can only handle filenames up to a certain character limit. The proposed filename",wraplength=400,justify="center").grid(column=1, columnspan=2, row=1)
  ttk.Label(dlgFLength, text=f"{fileName}",wraplength=400,justify="center",style="italic.TLabel").grid(column=1, columnspan=2, row=2)
  ttk.Label(dlgFLength, text=f"would exceed this limit.",wraplength=400,justify="center").grid(column=1, columnspan=2, row=3)
  ttk.Label(dlgFLength, text=f"Would you like to skip this file, or to continue with the characters that go over the filename length limit dropped?",wraplength=400,justify="center").grid(column=1, columnspan=2, row=4)
  ttk.Checkbutton(dlgFLength, text='Apply decision to all files with overlong filenames',variable=applyToAllLength,onvalue=True, offvalue=False).grid(column=1, columnspan=2, row=5)
  ttk.Button(dlgFLength, text="Skip this file", command=lambda:decisionFLength("skip")).grid(column=1, row=6)
  ttk.Button(dlgFLength, text="Continue with a shortened filename", command=lambda:decisionFLength("continue")).grid(column=2, row=6)

  for child in dlgFLength.winfo_children():
    child.grid_configure(padx=5, pady=5)

  dlgLength.protocol("WM_DELETE_WINDOW", lambda:decisionFLength("skip")) # intercept close button
  dlgLength.transient(root)   # dialog window is related to main
  dlgLength.wait_visibility() # can't grab until window appears, so we wait
  dlgLength.grab_set()        # ensure all input goes to our window
  dlgLength.wait_window()     # block until window is destroyed

######################

# this actually renames the file(s) into the names determined by nameConvert
def fileRenamer(*args):
  lengthDecision.set("")
  copyDecision.set("")
  applyToAllLength.set(False)
  applyToAllCopy.set(False)
  global fileExt
  
  successcounter = 0
  skipcounter = 0
  infoTitle.set("")
  infoText.set("")
  
  global filesFound
  filesFound = False
  
  for path, dirs, files in os.walk(inputDir.get()):
    for f in files:
      showedCopyWindowOnceThisFile = False
      if f[:f.rfind(".")] in hashList:
        file = nameConvert(f)[0]
        fileName = file + "." + fileExt
        # checking the length of this proposed filename to make sure Windows can actually handle it
        if len(fileName) > 254:
          if applyToAllLength.get() != True:
            alertWindowLength(fileName)
          if lengthDecision.get() == "continue":
            print(fileName)
            file = file[:(254 - len(fileExt) - 1)] #254 minus the file extension with one period
            fileName = file + "." + fileExt
        
        emptySpotFound = False
        if len(fileName) < 254 or lengthDecision.get() == "continue":
          copyNum = 0
          while emptySpotFound != True:
            newFile = os.path.join(inputDir.get(), fileName)
            
            # setting what to do with copies of existing files - this might be because it's a copy of an existing voiceline or if there are already renamed files in the input directory from a previous time this script was run
            if os.path.exists(newFile):
              if applyToAllCopy.get() != True and showedCopyWindowOnceThisFile != True:
                alertWindowCopy(fileName)
                showedCopyWindowOnceThisFile = True
              # if we want to add a marker to the end, we need to figure out if this file already exists too, so we loop until we do not find one of the proposed name.
              if copyDecision.get() == "copymarker":
                copyNum = copyNum + 1
                fileName = file + dividerinput.get() + "copy" + str(copyNum)  + "." + fileExt
                if len(fileName) > 254:
                  if applyToAllLength.get() != True:
                    alertWindowLength(fileName)
                  if lengthDecision.get() == "continue":
                    file = file[:(254 - len(fileExt) - 1 - len(dividerinput.get() + "copy" + str(copyNum)) - 4)] #254 minus the file extension with one period minus the copy marker minus a couple of buffer characters for higher copyNums
                    fileName = file + dividerinput.get() + "copy" + str(copyNum)  + "." + fileExt
                  elif lengthDecision.get() == "skip":
                    emptySpotFound = False
                    break
              elif copyDecision.get() == "overwrite":
                emptySpotFound = True
              else:
                emptySpotFound = False
                break
            else:
              emptySpotFound = True
              
        if emptySpotFound == True:
          newFile = os.path.join(inputDir.get(), fileName)
          toDelete = False
          if os.path.exists(newFile):
            print(f"RESULT: Overwriting {fileName}...")
            os.rename(newFile, os.path.join(inputDir.get(), fileName[:100]+"remove")) # renaming the being-overwritten file first just in case something goes wrong during the next step
            toDelete = True
            
          print(f"RESULT: {f} is now {fileName}")
          os.rename(oldFile, newFile)
          
          
          # deleting the being-overwritten file now that the renaming is done
          if toDelete == True:
            os.remove(os.path.join(inputDir.get(), fileName[:100]+"remove"))
          successcounter = successcounter + 1
            
            
        else:
          print(f"RESULT: Skipping {fileName}...")
          skipcounter = skipcounter + 1
   
  if successcounter == 0 and skipcounter == 0:
    infoTitle.set("Error:")
    infoTitleLabel.config(foreground="red")
    infoText.set("no applicable files found in specified directory.")
    infoTextLabel.config(foreground="red")
  elif successcounter == 0:
    infoTitle.set("Alert:")
    infoTitleLabel.config(foreground="orange")
    infoText.set(f"Renamed {successcounter} files, skipped {skipcounter} files.")
    infoTextLabel.config(foreground="orange")
  else:
    infoTitle.set("Success!")
    infoTitleLabel.config(foreground="green")
    if skipcounter == 0:
      infoText.set(f"Renamed {successcounter} files.")
    else:
      infoText.set(f"Renamed {successcounter} files, skipped {skipcounter} files.")
    infoTextLabel.config(foreground="green")


# checking if we can enable the button that runs the renaming scripts
def convertButtonCheck(*args):
  conditionAmount = 0 #how many conditions are there? (increase this with conditionAmount = conditionAmount + 1 every time a new condition is added)
  conditionsMet = 0 #how many conditions have been met?
  
  #condition 1: no forbidden dividers
  conditionAmount = conditionAmount + 1
  if forbiddenDividerWarning.cget("text") == "":
    conditionsMet = conditionsMet + 1
    
  #condition 2: input directory set
  conditionAmount = conditionAmount + 1
  if inputDir.get() != "":
    conditionsMet = conditionsMet + 1
    
  #condition 3: at least one slot is filled
  conditionAmount = conditionAmount + 1
  for key,value in filledSlots.items():
    if value != "":
      conditionsMet = conditionsMet + 1
      break
    
  if conditionsMet == conditionAmount:
    convertButton.state(['!disabled'])
  else:
    convertButton.state(['disabled'])
    
    
# when the divider is changed, recalculate box sizes, positions etc.
global validXCoordList
validXCoordList = []
savedDLCBoxXPosition = 0
savedDLCBoxYPosition = 0
def divChange(*args):
  
  forbiddenDividerWarning.config(text="")
  
  # displaying warnings if the user tries to use characters forbidden in Windows file names
  for character in forbiddenDividers:
    if dividerinput.get().find(character) != -1:
      if forbiddenDividerWarning.cget("text") == "":
        forbiddenDividerWarning.config(text="Error: ")
      forbiddenDividerWarning.config(text=forbiddenDividerWarning.cget("text") + character + " and ")
      dividerinput.set(dividerinput.get())
      
  if forbiddenDividerWarning.cget("text") != "":
    forbiddenDividerWarning.config(text=forbiddenDividerWarning.cget("text")[:-4] + "can't be used in Windows file names.")
    convertButtonCheck() # checking if the convert button can be enabled
  
  # recalculating the divider box sizes and therefore both the empty box locations and the divider box locations too
  global validXCoordList
  validXCoordList = [] #generating new list of coordinate spans for easy access
    
  newDividerBoxWidth = len(dividerinput.get())*8
  dividerBoxWidth.set(str(newDividerBoxWidth)) #calculating the width of the new boxes
  boxXCurrent = boxXOffset + (boxWidth.get()/2)
  for i in range(0, maxSlots+1):
    if i != maxSlots:
      dividerBoxes[i].itemconfig(dividerBoxTexts[i], text=dividerinput.get()) #changing the displayed text in the boxes
      dividerBoxes[i].coords(dividerBoxTexts[i],dividerBoxWidth.get()/2, boxHeight.get()/4) #aligning the displayed text in the boxes
      dividerBoxes[i].config(width=dividerBoxWidth.get()) #updating the width of the box
    
    #saving lowest and highest coordinates of box
    validXCoordList.append([boxXCurrent-(boxWidth.get()/2),boxXCurrent+(boxWidth.get()/2)])
    
    #if this is the dlc box, save the position so we can use it later when hiding/showing the box
    if cardText[cardTextList[i]] == "dlc": 
      savedDLCBoxXPosition = boxXCurrent
      savedDLCBoxYPosition = boxY + boxYOffset
    
    boxes[i].place(x=boxXCurrent , y=boxY + boxYOffset) #updating the position of the choice box
    if filledSlots[i] != "":
      cardsAsStrings[filledSlots[i]].place(x=boxXCurrent , y=boxY + boxYOffset)
    boxXCurrent = boxXCurrent + (boxWidth.get()/2) + (dividerBoxWidth.get()/2) + 5
    if i != maxSlots:
      dividerBoxes[i].place(x=boxXCurrent , y=boxY + boxYOffset) #updating teh (rawr xD) position of the dividerBox.
    boxXCurrent = boxXCurrent + (dividerBoxWidth.get()/2) + (boxWidth.get()/2) + 5
    
  setExample() #updating the example sentence
  
  #updating the width of the canvas if needed, and the empty padding column
  root.update_idletasks()
  newCanvasWidth = (boxXOffset*5) + (dividerBoxWidth.get()*5) + (boxWidth.get()*6)
  mainCanvas.config(width=newCanvasWidth)
  canvasWidthDif = newCanvasWidth - origCanvasWidth - 10
  if canvasWidthDif > origPadding:
    padLabel.grid_configure(ipadx= canvasWidthDif)
  else:
    padLabel.grid_configure(ipadx= origPadding)


# letting the user drag cards (onto empty boxes)
#https://stackoverflow.com/questions/67234255/drag-and-drop-the-object-in-tkinter-ui
def drag(event):
  # stopping the infobox timer and removing it if needed
  global hTimerRunning
  global hTimer
  if hTimerRunning != False:
    hTimerRunning = False
    hTimer.cancel()
    nowShowing = ""
  cardInfoBox.place_forget()
  
  # updating the card coordinates based on user mouse input
  x = event.x + event.widget.winfo_x()
  y = event.y + event.widget.winfo_y()
  event.widget.place(x=x, y=y, anchor="center")


# letting the user drag cards onto empty boxes
def drop(event):
  x = event.x + event.widget.winfo_x()
  y = event.y + event.widget.winfo_y()
  fittedIntoSlot = False
  # checking if this item was dropped near a slot
  # nesting this so we don't run a billion calculations every frame
  if y <= boxY + boxYOffset + (boxHeight.get()/2):
    if not y<boxY + boxYOffset -(boxHeight.get()/2):
      for i in range(0, maxSlots+1):
        if x <= validXCoordList[i][1]:
          if not x<validXCoordList[i][0]:
            # placing the item in the slot
            event.widget.place(x=validXCoordList[i][0]+(boxWidth.get()/2), y=boxY + boxYOffset, anchor="center")
            # removing this item from a slot it was previously in, if needed
            for key,value in filledSlots.items():
              if value == str(event.widget):
                filledSlots[key] = ""
                break
            # adding it to the slot it was just dropped into
            filledSlots[i] = str(event.widget) # event.widget looks like this: .!frame.!canvas.!canvas11
            fittedIntoSlot = True
            break
   
   # if the above determined the user didn't drop the card on a box we can empty whatever box it was previously in (if any)
  if fittedIntoSlot == False:
    for key,value in filledSlots.items():
      if value == str(event.widget):
        filledSlots[key] = ""
        break
        
  #updating the orderChosen list
  global orderChosen
  orderChosen = []
  for key,value in filledSlots.items():
    if value != "":
      orderChosen.append(cards[cardsAsStrings[value]]) #value = '.!frame.!labelframe.!canvas.!canvas13' -> cardsAsStrings[value] = <tkinter.Canvas object .!frame.!labelframe.!canvas.!canvas13> -> cards[cardsAsStrings[value]] = 'file'
      
  print(f"filledSlots is now {filledSlots}")
  print(f"orderChosen is now {orderChosen}")
  
  setExample() #updating the example sentence
  convertButtonCheck() #checking if we can enable the conversion button


#toggling the DLC card and the DLC options select frame off and on depending on user checkbox input
def dlcToggle(*args):
  if toggleDLC.get() == True:
    dlcCard.place(x=savedDLCBoxXPosition,y=savedDLCBoxYPosition, anchor="center")
    dlcFormatFrame.grid(column=3, row=1, sticky=W)
    dlcFormatFrame.grid_configure(padx=20)
  else:
    dlcCard.place_forget()
    dlcFormatFrame.grid_forget()


# popup info window function upon info button press
def infoFunct(infoType):
  if infoType == "format":
    messagebox.showinfo(message="Drag and drop any number of cards into the open slots. Hover over each card to see examples for what that card entails.")
  elif infoType == "dlc":
    messagebox.showinfo(message="Many DLC items have non-standardized prefixes or suffixes in their names to denote their belonging to a DLC. This adds an extra marker to DLC files that is standardized, letting you more easily organize the files into base game and DLC files.")
  elif infoType == "packageNames":
    messagebox.showinfo(message="Many Conversations can be referred to by multiple different names. These are Conversation file names (\"DisDialogOneShot_18\", \"DisDialogOneShot_2\"), data package names (\"L_OvrsrHintJournal_DlgData\", \"LPbFrmPrsnScrpt_DlgData\"), and for some files also oneshot nicknames (\"HintConvoBlackJournal\", \"Pub01a_Piero_First_Meeting\").")
  elif infoType == "divider":
     #cutting out one \ from \\ for display purposes
    forbiddenDividersStr = str(forbiddenDividers)
    forbiddenDividersStr = forbiddenDividersStr[1:-1]
    forbiddenDividersStr = "'" + forbiddenDividersStr[2:]
    messagebox.showinfo(message=f"Divider between the elements of the file name. Characters that can't be used in the divider: {forbiddenDividersStr}")
  elif infoType == "input":
   messagebox.showinfo(message="Files of any extension using the hashed \"Play_...\" names can be used. Remember to backup your files first since this tool will directly rename them.")
# to use: ttk.Button(mainframe, text="🛈", width=3, command=lambda:infoFunct("format")).grid(column=4, row=rowN, sticky=W)


# card infobox function upon hover over card
# actual canvases for this get created down below the slot and cards creation functions so that the infobox appears on top of those canvases
cardInfoBoxX = 0
cardInfoBoxY = 0
hoverTime = 0
newMouseX = 0
newMouseY = 0
oldMouseX = 0
oldMouseY = 0
initiatorBox = ""
hoverFRunning = False
nowShowing = ""

def showCardInfoBox(initiatorEvent):
  global cardInfoBoxX
  global cardInfoBoxY
  
  global nowShowing
  if nowShowing != "" and nowShowing != initiatorEvent:
    cardInfoBox.place_forget()
  nowShowing = initiatorEvent
  
  # infoType is the card's short name, accessible by its value in the cards dictionary. For example cards = {<tkinter.Canvas object .!frame.!labelframe.!canvas.!canvas13>: 'file'} so cards[card1] gets us the needed string for card 1.
  infoType = cards[initiatorEvent]
  
  # getting the boxes' position to place the tooltip below it
  cardInfoBoxX = initiatorEvent.winfo_x() + (boxWidth.get()*0.9) + canvasFrame.winfo_x()
  cardInfoBoxY = initiatorEvent.winfo_y() + (boxHeight.get()) + canvasFrame.winfo_y()
  
  #if this would be outside of the bounds of window, change the coordinates until it fits in the window. Note that the "width" attribute of the cardInfoBox is a string
  if (cardInfoBoxX + float(cardInfoBox.config("width")[4])) > root.winfo_width():
    cardInfoBoxX = root.winfo_width() - float(cardInfoBox.config("width")[4]) - 20
  if (cardInfoBoxY + float(cardInfoBox.config("height")[4])) > root.winfo_height():
    cardInfoBoxY = root.winfo_height() - float(cardInfoBox.config("height")[4]) - 20
  
  text=""
  #cardInfoBox = Canvas(mainframe, width=350, height=200,bg="lemon chiffon",highlightthickness=0,borderwidth=1,relief='solid')
  if infoType == "file":
    text="The UPK map/level script file name. Generic lines (\"Get around him!\", \"Check under everything.\") are labelled as \"Shared\".\n\nExamples:\n\"L_Pub_FromTwrReturn_Script\", \"L_Brothel_Script\", \"L_Distillery2_Script\", \"DLC06_Slaughter_Int_Script\", \"L_DLC07_DraperStreets_Script\"."
    cardInfoBox.config(height=120)
  elif infoType == "char":
    text="The character name as written in the files.\n\nExamples:\n\"Callista\", \"EliteGuard_A\", \"Sokolov\", \"DLC06_Butcher_A\", \"DLC07_DelilahVoidStatue\""
    cardInfoBox.config(height=90)
  elif infoType == "convNames":
    text="Either the DisDialogOneShot/DisDialogTree Conversation file name or the DataPackage object name, plus the DisDialogOneShot's OneShotNickName in brackets at the end if desired and applicable.\n\nExamples of Conversation file names:\n\"DisDialogOneShot_19\", \"DisDialogOneShot_4\", \"Dlg_CityGuard\", \"DLC07_Dlg_Witch\"; \nExamples of data package names:\n\"L_Tower_ConvoBridge1_DlgData\", \"Pub2b_Piero_DlgData\", \"Dlg_AristocraticMale_Shared\", \"DLC07_Void_Outsider_DlgData\"; \nExamples of oneshot nicknames:\n\"RegentTalksToGuardCaptain\", \"Corvos Status\", \"Pub04a_EmilyHides\", \"Eels_Talk_Rothwild\""
    cardInfoBox.config(height=240)
  elif infoType == "id":
    text="The UE Object name of the UE Class DisConv_Blurb along with the name of its parent Object of the UE Class DisConversation.\n\nExamples:\n\"DisConversation.DisConv_Blurb_1\", \"DisConversation_4.DisConv_Blurb_13\", \"DisConversation_2.DisConv_Blurb\""
    cardInfoBox.config(height=120)
  elif infoType == "text":
    text="The actual text of the voiceline, with characters not allowed in file names excised.\n\nExamples:\n\"Attention Dunwall Citizens Due to the rise in the population of plague rats, you are warned to stay out of uninhabited buildings\", \"Get around him!\", \"More importantly, who will you be, Royal Protector or assassin\""
    cardInfoBox.config(height=130)
  elif infoType == "dlc":
    text="An additional marker identifying files from DLCs, see the info button next to the associated checkbox below for more information and the DLC format selector for examples."
    cardInfoBox.config(height=60)
    
  cardInfoBox.itemconfig(cardInfoBoxText, text=text)
  cardInfoBox.place(x=cardInfoBoxX, y=cardInfoBoxY, anchor=NW)

hTimerRunning = False
initiatorEvent = ""
# this starts the process and sets necessary variables
def startHoverTimer(event):
  global hTimerRunning
  global initiatorEvent
  global hTime
  hTime = 0
  if hTimerRunning != True:
    if event.widget != cardInfoBox:
      initiatorEvent = event.widget
    hoverTimer(initiatorEvent)
  else:
    if initiatorEvent != "":
      if initiatorEvent != event.widget:
        #stopping the previous timer
        hTimerRunning = False
        hTimer.cancel()
        nowShowing = ""
        cardInfoBox.place_forget()
        
        #starting the new one
        if event.widget != cardInfoBox:
          initiatorEvent = event.widget
        hoverTimer(initiatorEvent)
  
hTime = 0
def hoverTimer(initiatorEvent):
  global hTimerRunning
  global hTimer
  global hTime
  global nowShowing
  mouseX = mainframe.winfo_pointerx()
  mouseY = mainframe.winfo_pointery()
  
  initiatorX = root.winfo_x() #where is the root?
  initiatorX = initiatorX + canvasFrame.winfo_x() #where is the canvasFrame?
  initiatorX = initiatorX + initiatorEvent.winfo_x() #where is the event itself?
  initiatorX = initiatorX + 10 #10 pixels of padding
  initiatorXMax = initiatorX + float(initiatorEvent.config("width")[4]) + 5 #how wide is the event? plus 5 pixels of padding
  
  initiatorY = root.winfo_y() #where is the root?
  initiatorY = initiatorY + canvasFrame.winfo_y() #where is the canvasFrame?
  initiatorY = initiatorY + initiatorEvent.winfo_y() #where is the event itself?
  initiatorY = initiatorY + 8 #8 pixels of padding
  initiatorY = initiatorY + float(boxHeight.get())
  initiatorYMax = initiatorY + float(initiatorEvent.config("height")[4]) + 5 #how wide is the event? plus 5 pixels of padding
  
  if ( mouseX >= initiatorX ) and ( mouseX <= initiatorXMax ) and ( mouseY >= initiatorY ) and ( mouseY <= initiatorYMax ):
    hTimer = Timer(.1,lambda:hoverTimer(initiatorEvent))
    hTimer.start()
    hTimerRunning = True
    
    hTime = hTime + 1
    if hTime == 10:
      showCardInfoBox(initiatorEvent)
    
  else:
    if hTimerRunning == True:
      hTimerRunning = False
      hTimer.cancel()
      nowShowing = ""
      cardInfoBox.place_forget()
    hTime = 0

################

# and now we're finally into actually setting up the UI!

# setting up the basics of the formatting canvas
canvasFrame = ttk.Labelframe(mainframe,text="Formatting:               ")
mainCanvas = Canvas(canvasFrame)

# inside the formatting canvas: setting up empty boxes (slots) and their dividers
for i in range(0, maxSlots+1):
  if i == 0:
    boxXCurrent = boxXOffset + (boxWidth.get()/2)
  else:
    boxXCurrent = boxXCurrent + (dividerBoxWidth.get()/2) + (boxWidth.get()/2) + 5
  # empty box
  globals()[f"box{i+1}"] = Canvas(mainCanvas, width=boxWidth.get(), height=boxHeight.get(),bg="lightGrey",borderwidth=2,relief='sunken')
  globals()[f"box{i+1}"].place(x=boxXCurrent, y=boxY + boxYOffset, anchor="center")
  
  # divider box
  if i != maxSlots:
    boxXCurrent = boxXCurrent + (dividerBoxWidth.get()/2) + (boxWidth.get()/2) + 5
    globals()[f"dividerBox{i+1}"] = Canvas(mainCanvas, width=dividerBoxWidth.get(), height=boxHeight.get()/2, bg="white")
    globals()[f"dividerBox{i+1}"].place(x=boxXCurrent, y=boxY + boxYOffset, anchor="center")
    globals()[f"dividerBox{i+1}Text"] = globals()[f"dividerBox{i+1}"].create_text(dividerBoxWidth.get()/2,boxHeight.get()/4,fill="black",text=".", anchor="center",justify=CENTER)
  
  # variables and lists
  boxes.append(globals()[f"box{i+1}"])
  if i != maxSlots:
    dividerBoxes.append(globals()[f"dividerBox{i+1}"])
    dividerBoxTexts.append(globals()[f"dividerBox{i+1}Text"])

# inside the formatting canvas: setting up empty boxes (slots) and their dividers
# cards that can get dragged by the user
cardXPaddingStart = 20
cardXPaddingInbetween = 10
cardYPadding = 10
cardY = cardYPadding + (boxHeight.get()*1.5+10)
cards = {} # a dict of all the cards: the key is the tkinter object name, the value is the internal name that is used on our hashList
cardText = {"map name":"file","character name":"char","conversation name":"convNames","conversation and blurb id":"id","text":"text","DLC marker":"dlc"} # the key is the public name we display on the card, the value is the internal name that is used on our hashList
cardTextList = list(cardText)
cardsAsStrings = {} # to match card widget names we've gotta do some ugly stuff
dlcCard = ""

for i in range(0, len(cardText)):
  if i == 0:
    cardX = cardXPaddingStart + (boxWidth.get()/2)
  else:
    cardX = cardX + 100 + cardXPaddingInbetween
  # setting up the card, which is a little canvas of its own
  globals()[f"card{i+1}"] = Canvas(mainCanvas, width=boxWidth.get(), height=boxHeight.get(), bg="grey",borderwidth=1,relief='raised')
  globals()[f"card{i+1}"].create_text(boxWidth.get()/2,boxHeight.get()/2,fill="black",width=boxWidth.get(),justify=CENTER,text=cardTextList[i])
  globals()[f"card{i+1}"].place(x=cardX, y=cardY, anchor="center")
  globals()[f"card{i+1}"].bind("<B1-Motion>", drag)
  globals()[f"card{i+1}"].bind("<ButtonRelease-1>", drop)
  globals()[f"card{i+1}"].bind("<Enter>", startHoverTimer)
  
  # saving the dlc card's position and hiding it by default
  if cardText[cardTextList[i]] == "dlc":
    dlcCard = globals()[f"card{i+1}"]
    savedDLCBoxXPosition = cardX
    savedDLCBoxYPosition = cardY
    dlcCard.place_forget()
  
  # variables and lists
  cards[globals()[f"card{i+1}"]] = cardText[cardTextList[i]] #i=0 -> cardTextList[0] = "map name" -> cardText["map name"] = "file" -> cards[card0] = "file"
  cardsAsStrings[str(globals()[f"card{i+1}"])] = globals()[f"card{i+1}"]
  

################

# filling the main window

rowN = 0

# INPUT DIRECTORY
rowN = rowN + 1 #new row
ttk.Label(mainframe, text="Input directory:").grid(column=1, row=rowN, sticky=W)
ttk.Label(mainframe, textvariable=inputDir, background="lightGrey", width=70).grid(column=2, row=rowN, sticky=W)
# this stuff is in its own frame for visual formatting purposes
inputFrame = ttk.Frame(mainframe)
inputFrame.grid(column=3, row=rowN, sticky=(W,E))
ttk.Button(inputFrame, text="browse", command=lambda:openDirs("input")).grid(column=1, row=1, sticky=W)
ttk.Button(inputFrame, text="🛈", width=3, command=lambda:infoFunct("input")).grid(column=2, row=1, sticky=E)

# FORMATTING CANVAS
rowN = rowN + 1 #new row
canvasFrame.grid(column=1, columnspan=4, row=rowN, sticky=NW)
mainCanvas.grid(column=1, columnspan=4, row=rowN, sticky=(N, S))

# FAKE LABEL FOR FORMATTING CANVAS
# this is a bit more complicated than usual - we want the info button right next to the text label, but Labelframes only let you use plain text as the label. So we assign everything a place here and then right at the very end before the mainloop starts we save the relevant positions, remove the placeholder text label, and move the button down to where it's supposed to be.
rowN = rowN + 1 #new row
# this stuff is in its own frame for visual formatting purposes
formatInfoButtonFrame = ttk.Frame(mainframe)
formatInfoButtonFrame.grid(column=1, columnspan=3, row=rowN, sticky=W)
formatInfoButtonLabel = ttk.Label(formatInfoButtonFrame, text="Formatting:")
formatInfoButtonLabel.grid(column=1, row=1, sticky=W)
formatInfoButton = ttk.Button(formatInfoButtonFrame, text="🛈", width=3, command=lambda:infoFunct("format"))
formatInfoButton.grid(column=2, row=1, sticky=W)

# DLC SETTINGS: TOGGLE
rowN = rowN + 1 #new row
ttk.Label(mainframe, text="Include DLC marker:").grid(column=1, row=rowN, sticky=W)
# this stuff is in its own frame for visual formatting purposes
dlcFrame = ttk.Frame(mainframe)
dlcFrame.grid(column=2,columnspan=2, row=rowN, sticky=(W,E,N,S))
toggleDLC = BooleanVar()
toggleDLC.trace_add("write", dlcToggle)
ttk.Checkbutton(dlcFrame,variable=toggleDLC,onvalue=True, offvalue=False).grid(column=1, row=1, sticky=W)
ttk.Button(dlcFrame, text="🛈", width=3, command=lambda:infoFunct("dlc")).grid(column=2, row=1, sticky=W)

# DLC SETTINGS: FORMAT
# this stuff is in its own frame for visual formatting purposes
dlcFormatFrame = ttk.Frame(dlcFrame)
ttk.Label(dlcFormatFrame, text="DLC marker format: ").grid(column=1, row=1, sticky=E)
dlcFormatVar = StringVar()
dlcFormatBox = ttk.Combobox(dlcFormatFrame, textvariable=dlcFormatVar,width=60)
dlcFormatBox.grid(column=2, row=1, sticky=W)
dlcFormatBox['values'] = ('Number - DLC05/DLC06/DLC07 [default]', 'Name - DunwallCityTrials/TheKnifeOfDunwall/TheBrigmoreWitches', 'Abbreviation - DCT/TKoD/TBW')
dlcFormatVar.set(dlcFormatBox['values'][0])
dlcFormatBox.bind('<<ComboboxSelected>>', setExample)

# CONVERSATION NAME SETTINGS
rowN = rowN + 1 #new row
ttk.Label(mainframe, text="Conversation names:").grid(column=1, row=rowN, sticky=W)
# this stuff is in its own frame for visual formatting purposes
packageNameFrame = ttk.Frame(mainframe)
packageNameFrame.grid(column=2, row=rowN, sticky=W)
packageNameVar = StringVar()
packageNameBox = ttk.Combobox(packageNameFrame, textvariable=packageNameVar,width=60)
packageNameBox.grid(column=1, row=1, sticky=W)
packageNameBox['values'] = ('data package names only', 'data package names (oneshot nicknames in brackets) [default]', 'Conversation file names only', 'Conversation file names (oneshot nicknames in brackets)')
packageNameVar.set(packageNameBox['values'][1])
packageNameBox.bind('<<ComboboxSelected>>', packageNameBoxChose)
ttk.Button(packageNameFrame, text="🛈", width=3, command=lambda:infoFunct("packageNames")).grid(column=2, row=1, sticky=W)

# DIVIDER INPUT
rowN = rowN + 1 #new row
ttk.Label(mainframe, text="Divider:").grid(column=1, row=rowN, sticky=W)
# this stuff is in its own frame for visual formatting purposes
dividerFrame = ttk.Frame(mainframe)
dividerFrame.grid(column=2, row=rowN, sticky=W)
dividerinput.trace_add("write", divChange)
dividerinputEntry = ttk.Entry(dividerFrame, width=7, textvariable=dividerinput)
dividerinputEntry.grid(column=1, row=1, sticky=W)
ttk.Button(dividerFrame, text="🛈", width=3, command=lambda:infoFunct("divider")).grid(column=2, row=1, sticky=W)
forbiddenDividerWarning = ttk.Label(dividerFrame, text="",style="redText.TLabel")
forbiddenDividerWarning.grid(column=3, row=1, sticky=W)

# -----------------------
rowN = rowN + 1 #new row
ttk.Separator(mainframe, orient=HORIZONTAL).grid(column=1, row=rowN, columnspan=4, sticky='WE')

# EXAMPLE DISPLAY
rowN = rowN + 1 #new row
ttk.Label(mainframe, text="Example:").grid(column=1, row=rowN, sticky=NW)
exampleLabel = ttk.Label(mainframe, textvariable=exampleText, width=70,justify="left") #wraplength will be defined down below
exampleLabel.grid(column=2, row=rowN, sticky=NW)
exampleButton = ttk.Button(mainframe, text="different random\nexample sentence", width=20, command=resetExample)
exampleButton.grid(column=3, row=rowN, sticky=NW)

# EXAMPLE DISPLAY: ITEMS THAT HAVE GONE UNUSED
rowN = rowN + 1 #new row
ttk.Label(mainframe, text="Unused data\nin example:").grid(column=1, row=rowN, sticky=NW)
exampleUnusedLabel = ttk.Label(mainframe, textvariable=exampleUnusedText, width=70,justify="left") #wraplength will be defined down below
exampleUnusedLabel.grid(column=2, row=rowN, sticky=NW)

# -----------------------
rowN = rowN + 1 #new row
ttk.Separator(mainframe, orient=HORIZONTAL).grid(column=1, row=rowN, columnspan=4, sticky='WE')

# STATUS DISPLAY * RUN BUTTON
rowN = rowN + 1 #new row
convertButton = ttk.Button(mainframe, text="Rename", command=fileRenamer, state='disabled',style='convertButton.TButton')
convertButton.grid(column=3, row=rowN, sticky=W)
#displaying status
infoTitle = StringVar()
infoText = StringVar()
infoTitleLabel = ttk.Label(mainframe, textvariable=infoTitle, foreground="red")
infoTitleLabel.grid(column=1, row=rowN, sticky=NW)
infoTextLabel = ttk.Label(mainframe, textvariable=infoText, foreground="red")
infoTextLabel.grid(column=2, row=rowN, sticky=NW)

# EMPTY BUFFER LABEL THAT PADS THE MAIN FRAME IF THE FORMATTING CANVAS GETS WIDER
origPadding = 50
padLabel = ttk.Label(mainframe, text="")
padLabel.grid(column=4, row=1, sticky=NW)
padLabel.grid_configure(ipadx=origPadding) # this ipadx will be increased if there needs to be more padding

#####################

# creating the tooltip box for hovering over the cards
# doing this down here instead of up by its function because it needs to be on top of the cards and slots instead of under them
cardInfoBox = Canvas(mainframe, width=350, height=200,bg="lemon chiffon",highlightthickness=0,borderwidth=1,relief='solid')
cardInfoBoxText = cardInfoBox.create_text(5,5,fill="black",text="",justify="left", anchor=NW,width=340, font=cardInfoFont)

#####################

# formatting things visually

# formatting the grid
# a couple of things have already been padded or otherwise placed so we determine a new list of items to be formatted in the grid here
thingsAlreadyFormatted = [formatInfoButtonFrame,dlcFormatFrame,dlcFrame,cardInfoBox,padLabel]
framesToBeFormatted = [mainframe]

for frame in framesToBeFormatted:
  for child in frame.winfo_children():
    if child not in thingsAlreadyFormatted:
      child.grid_configure(padx=5, pady=5)

# updating cached locations
root.update_idletasks()

# formatting some items that aren't satisfied by the above formatting further
# formatting the main canvas
origCanvasWidth = (boxXOffset*5) + (dividerBoxWidth.get()*5) + (boxWidth.get()*6)
mainCanvas.config(width=origCanvasWidth)
mainCanvas.config(height=((boxHeight.get()*2)+30))

# moving the formatting info button
formatInfoButtonX = canvasFrame.winfo_x() + 5
formatInfoButtonY = canvasFrame.winfo_y() - (formatInfoButtonFrame.winfo_height()/2.7)
formatInfoButtonFrame.grid_forget()
formatInfoButtonFrame.place(x=formatInfoButtonX,y=formatInfoButtonY)

# setting some wraplengths now that we've determined the size and position of everything
exampleUnusedLabel.config(wraplength=exampleUnusedLabel.winfo_width()-5)
exampleLabel.config(wraplength=exampleLabel.winfo_width()-5)

#####################

# final cleanup

#running divChange once to set everything up
divChange()

# initialize main loop, gui is go
root.mainloop()
