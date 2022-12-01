# TODO: Work on line wrapping.
# TODO: Add comments to code.

import os
import runpy
import shutil
import subprocess
import sys
import threading
from time import sleep
from tkinter import filedialog as fd

import pynput

global parenthesisCount
global syntaxBuild
global syntaxType
global editorLinesWithSyntax
inEditor = True  # Define the 'inEditor' variable. When this variable is true, then you're in the editor. If false, then you're not.
key = ""  # Define the 'key' variable.
cursorBlink = 0  # Define the 'cursorBlink' variable.
# Color constants
RED = "\033[0;31m"
NC = "\033[0m"
P = "\033[0;35m"

if (
    not os.path.dirname(sys.argv[0]) == ""
):  # Set currentWorkingDirectory to the directory of editor.py
    os.chdir(os.path.dirname(sys.argv[0]))
currentWorkingDirectory = os.getcwd().replace("\\", "/")
terminalHeight = (
    shutil.get_terminal_size().lines
)  # Set 'terminalHeight' to the terminal height
terminalWidth = (
    shutil.get_terminal_size().columns
)  # Set 'terminalWidth' to the terminal width


def increment():  # Cursor blink thread
    global cursorBlink
    cursorBlink = 1  # when cursorBlink is 1, then the cursor is being shown.
    while inEditor:
        cursorBlink = 0  # If it's zero, it's hidden
        sleep(0.5)
        cursorBlink = 1
        sleep(0.5)
        if key == "save":
            exit()
    exit()


def error(text):  # Error function
    print(RED + "Error: " + text + NC)


print("")
print("Select your project folder.")
print("")
# Get the project folder that the user wants to edit
folder = ""
try:
    if not sys.argv[1] is None:
        folder = sys.argv[1].replace(
            "\\", "/"
        )  # If editor.py is ran with an argument, then set 'folder' to it.
        # For example, the command ran is 'py editor.py ../projects/example', then it'll set 'folder' to '../projects/example'
except IndexError:
    sleep(2)
    folder = fd.askdirectory(
        title="Choose a project.", initialdir="../projects"
    )
    folder = folder.replace("\\", "/")
if os.path.isdir(folder):
    previousPath = os.getcwd()
    os.chdir(folder)
    folder = os.getcwd().replace("\\", "/") + "/Stage"
    realFolderPath = os.path.dirname(folder)
    os.chdir(previousPath)
    if not os.path.isfile(
        realFolderPath + "/.maindir"
    ):  # Detect if current directory is a ScratchLang project
        error(
            "Not a ScratchScript project ("
            + realFolderPath
            + "), or .maindir file was deleted."
        )
        exit()
    os.chdir(realFolderPath)
    editorLines = []
    print("Loading " + realFolderPath + "...")
    print("")
    os.chdir("Stage")
    fileOpened = open("project.ss1", "r")
    fileOpenedLength = len(fileOpened.readlines())
    fileOpened.close()
    fileOpened = open("project.ss1", "r")
else:
    editorLines = []
    print("Loading " + folder + "...")
    print("")
    fileOpened = open(folder, "r")
    fileOpenedLength = len(fileOpened.readlines())
    fileOpened.close
    fileOpened = open(folder, "r")
    folder = os.path.dirname(folder)
    os.chdir(folder)
progressBarLength = 55
q = 0
for line in fileOpened.readlines():
    q += 1
    percent = q / fileOpenedLength
    print(
        "\033[A["
        + round(progressBarLength * percent) * "#"
        + (progressBarLength - round(progressBarLength * percent)) * " "
        + "] "
        + str(round(percent * 100))
        + "%"
    )
    line = line.strip("\n")
    editorLines += [line + " "]
fileOpened.close()
print("")
print("Loading settings...")
print("")
fileOpened = open(currentWorkingDirectory + "/var/editor_settings", "r")
tabSize = 2
syntaxHighlightingEnabled = True
previousFileOpenedLength = fileOpenedLength
fileOpenedLength = len(fileOpened.readlines())
fileOpened.close()
fileOpened = open(currentWorkingDirectory + "/var/editor_settings", "r")
progressBarLength = 55
q = 0
for line in fileOpened.readlines():
    q += 1
    percent = q / fileOpenedLength
    print(
        "\033[A["
        + round(progressBarLength * percent) * "#"
        + (progressBarLength - round(progressBarLength * percent)) * " "
        + "] "
        + str(round(percent * 100))
        + "%"
    )
    if "tabsize" in line:
        tabSize = int(line.replace("tabsize: ", ""))
    elif "syntax_highlighting" in line:
        syntaxHighlightingEnabled = line.replace("syntax_highlighting: ", "")
    elif "show_cwd" in line:
        isTrue = line.replace("show_cwd: ", "")
        if isTrue == "True":
            showCwd = True
        elif isTrue == "False":
            showCwd = False
        else:
            showCwd = True
fileOpened.close()
fileOpenedLength = previousFileOpenedLength
print("")
print("Building syntax highlighting...")
print("")
q = 0
# Stuff used for syntax highlighting.
colors = {
    "c": "\033[0m",
    "p": "\033[48;5;10m",
    "n": "\033[48;5;10m",
    "0": "\033[37m",
    "1": "\033[38;2;153;102;255m",
    "2": "\033[38;2;255;140;26m",
    "3": "\033[38;2;255;102;26m",
    "4": "\033[38;2;255;191;0m",
    "5": "\033[38;2;207;99;207m",
    "6": "\033[38;2;255;171;25m",
    "7": "\033[38;2;92;177;214m",
    "8": "\033[38;2;89;192;89m",
    "9": "\033[38;2;15;189;140m",
}
backgroundColors = {
    "c": "",
    "p": "\033[1;90m",
    "n": "\033[1;90m",
    "0": "",
    "1": "",
    "2": "",
    "3": "",
    "4": "",
    "5": "",
    "6": "",
    "7": "",
    "8": "",
    "9": "",
}
parenthesisColors = {
    "0": "",
    "1": "\033[31m",
    "2": "\033[38;5;202m",
    "3": "\033[33m",
    "4": "\033[32m",
    "5": "\033[34m",
    "6": "\033[38;5;135m",
    "7": "\033[35m",
    "8": "\033[38;5;206m",
}
looks = [
    "switch backdrop to (",
    "next backdrop",
    "change [c",
    "change [fileOpened",
    "change [w",
    "change [pix",
    "change [m",
    "change [b",
    "change [g",
    "clear graphic effects",
    "(backdrop [",
    "set [c",
    "set [fileOpened",
    "set [w",
    "set [pix",
    "set [m",
    "set [b",
    "set [g",
]
looksFindType = [
    "le",
    "eq",
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "eq",
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
]
dataVar = [
    "var:",
    "] to (",
    "] by (",
    "show variable [",
    "hide variable [",
]
dataVarFindType = [
    "le",
    "in",
    "in",
    "le",
    "le",
]
dataList = [
    "list:",
    ") to [",
    ") by [",
    "delete all of [",
    "delete (",
    "insert (",
    "replace item (",
    "(item (",
    "(item # of (",
    "(length of [",
    "] contains (",
    "show list [",
    "hide list [",
]
dataListFindType = [
    "le",
    "in",
    "in",
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "in",
    "le",
    "le",
]
events = [
    "broadcast [",
    "broadcast:",
    "when I receive [",
    "when [",
    "when flag clicked",
    "when backdrop switches to [",
]
eventsFindType = ["le", "le", "le", "le", "eq", "le"]
sounds = [
    "play sound (",
    "start sound (",
    "change [pit",
    "change [pan",
    "set [pit",
    "set [pan",
    "stop all sounds",
    "(volume)",
    "clear sound effects",
    "change volume by (",
    "set volume to (",
]
soundsFindType = [
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "eq",
    "eq",
    "eq",
    "le",
    "le",
]
control = [
    "wait (",
    "wait until <",
    "repeat (",
    "repeat until <",
    "forever {",
    "if <",
    "} else {",
    "while <",
    "create a clone of (",
    "for [",
    "stop [",
]
controlFindType = [
    "le",
    "le",
    "le",
    "le",
    "le",
    "le",
    "eq",
    "le",
    "le",
    "le",
    "le",
]
sensing = [
    "ask (",
    "(answer)",
    "<key (",
    "<mouse down?>",
    "(mouse x)",
    "(mouse y)",
    "(loudness)",
    "(timer)",
    "reset timer",
    "([",
    "(current [",
    "(days since 2000)",
    "(username)",
]
sensingFindType = [
    "le",
    "eq",
    "le",
    "eq",
    "eq",
    "eq",
    "eq",
    "eq",
    "eq",
    "le",
    "le",
    "eq",
    "eq",
]
operators = [
    ") + (",
    ") - (",
    ") / (",
    ") * (",
    ") > (",
    ") < (",
    "(pick random (",
    ") = (",
    "> and <",
    "> or <",
    "<not <",
    "(join (",
    "(letter (",
    "(length of (",
    ") contains (",
    ") mod (",
    "(round (",
]
operatorsFindType = [
    "in",
    "in",
    "in",
    "in",
    "in",
    "in",
    "le",
    "in",
    "in",
    "in",
    "le",
    "le",
    "le",
    "le",
    "in",
    "in",
    "le",
]
pen = ["erase all"]
penFindType = ["eq"]
startParenthesis = ["(", "[", "{", "<"]
endParenthesis = [")", "]", "}", ">"]
excludes = ["46;1", "38;5;8", "0", "37", "35", "7", "1"]
bracketCount = 0
shabang = [
    "//!looks",
    "//!var",
    "//!list",
    "//!events",
    "//!sound",
    "//!control",
    "//!sensing",
    "//!operators",
]


def determine_type(line):
    global syntaxType
    syntaxType = "0"
    syntaxTypeId = 0
    q = -1
    for i in operators:
        q += 1
        if operatorsFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "8"
        elif operatorsFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "8"
        elif operatorsFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "8"
    q = -1
    for i in looks:
        q += 1
        if looksFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "1"
        elif looksFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "1"
        elif looksFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "1"
    q = -1
    for i in dataVar:
        q += 1
        if dataVarFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "2"
        elif dataVarFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "2"
        elif dataVarFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "2"
    q = -1
    for i in dataList:
        q += 1
        if dataListFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "3"
        elif dataListFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "3"
        elif dataListFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "3"
    q = -1
    for i in events:
        q += 1
        if eventsFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "4"
        elif eventsFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "4"
        elif eventsFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "4"
    q = -1
    for i in sounds:
        q += 1
        if soundsFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "5"
        elif soundsFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "5"
        elif soundsFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "5"
    q = -1
    for i in sensing:
        q += 1
        if sensingFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "7"
        elif sensingFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "7"
        elif sensingFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "7"
    q = -1
    for i in control:
        q += 1
        if controlFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "6"
        elif controlFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "6"
        elif controlFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "6"
    q = -1
    for i in pen:
        q += 1
        if penFindType[q] == "le":
            if i == line.lstrip(" ")[: len(i)]:
                syntaxType = "9"
        elif penFindType[q] == "eq":
            if i == line.lstrip(" ").rstrip(" "):
                syntaxType = "9"
        elif penFindType[q] == "in":
            if i in line.lstrip(" "):
                syntaxType = "9"
    for i in shabang:
        syntaxTypeId += 1
        if i in line.lstrip(" "):
            syntaxType = str(syntaxTypeId)
    if "\\n" in line.lstrip(" "):
        syntaxType = "n"
    if "\\p" in line.lstrip(" "):
        syntaxType = "p"


def splitByLen(text, length=0):
    splitList = []
    buffer = ""
    lengthCount = 0
    for mm in range(len(text)):
        lengthCount += 1
        buffer += text[mm]
        if lengthCount == length or mm == len(text) - 1:
            splitList += [buffer]
            lengthCount = 0
            buffer = ""
    return splitList


def add_syntax(line, progressBarEnabled=True):
    global q, editorLinesWithSyntax, bracketCount
    syntaxLine = line
    q += 1
    percent = q / fileOpenedLength
    if progressBarEnabled:
        print(
            "\033[A["
            + round(progressBarLength * percent) * "#"
            + (progressBarLength - round(progressBarLength * percent)) * " "
            + "] "
            + str(round(percent * 100))
            + "%"
        )
    determine_type(line)
    i = -1
    buildedLine = ""
    parenthesisCount = bracketCount
    while True:
        i += 1
        try:
            character = syntaxLine[i]
        except IndexError:
            break
        buildedLine += character
        if character in startParenthesis:
            if not character == "{":
                if character == "<":
                    if not (
                        syntaxLine[i - 1] == " " and syntaxLine[i + 1] == " "
                    ):
                        parenthesisCount += 1
                        c = 0
                        for z in range(parenthesisCount):
                            c += 1
                            if c == 9:
                                c = 1
                        buildedLine = buildedLine.rstrip(buildedLine[-1])
                        buildedLine += (
                            parenthesisColors[str(c)]
                            + character
                            + colors[syntaxType]
                        )
                else:
                    parenthesisCount += 1
                    c = 0
                    for z in range(parenthesisCount):
                        c += 1
                        if c == 9:
                            c = 1
                    buildedLine = buildedLine.rstrip(buildedLine[-1])
                    buildedLine += (
                        parenthesisColors[str(c)]
                        + character
                        + colors[syntaxType]
                    )
            else:
                bracketCount += 1
                c = 0
                for z in range(bracketCount):
                    c += 1
                    if c == 9:
                        c = 1
                buildedLine = buildedLine.rstrip(buildedLine[-1])
                buildedLine += (
                    parenthesisColors[str(c)] + character + colors[syntaxType]
                )
        elif character in endParenthesis:
            if not character == "}":
                if character == ">":
                    if not (
                        syntaxLine[i - 1] == " " and syntaxLine[i + 1] == " "
                    ):
                        if parenthesisCount > 0:
                            c = 0
                            for z in range(parenthesisCount):
                                c += 1
                                if c == 9:
                                    c = 1
                            buildedLine = buildedLine.rstrip(buildedLine[-1])
                            buildedLine += (
                                parenthesisColors[str(c)]
                                + character
                                + colors[syntaxType]
                            )
                            parenthesisCount -= 1
                else:
                    if parenthesisCount > 0:
                        c = 0
                        for z in range(parenthesisCount):
                            c += 1
                            if c == 9:
                                c = 1
                        buildedLine = buildedLine.rstrip(buildedLine[-1])
                        buildedLine += (
                            parenthesisColors[str(c)]
                            + character
                            + colors[syntaxType]
                        )
                        parenthesisCount -= 1
            else:
                if bracketCount > 0:
                    c = 0
                    for z in range(bracketCount):
                        c += 1
                        if c == 9:
                            c = 1
                    buildedLine = buildedLine.rstrip(buildedLine[-1])
                    buildedLine += (
                        parenthesisColors[str(c)]
                        + character
                        + colors[syntaxType]
                    )
                    bracketCount -= 1
        if character == '"':
            buildedLine = buildedLine.rstrip(buildedLine[-1])
            buildedLine += '\033[38;5;34m"'
            while True:
                i += 1
                try:
                    character = syntaxLine[i]
                except IndexError:
                    break
                buildedLine += character
                if character == '"':
                    buildedLine += colors[syntaxType]
                    break
        if character == "'":
            buildedLine = buildedLine.rstrip(buildedLine[-1])
            buildedLine += "\033[38;5;34m'"
            while True:
                i += 1
                try:
                    character = syntaxLine[i]
                except IndexError:
                    break
                buildedLine += character
                if character == "'":
                    buildedLine += colors[syntaxType]
                    break
        if character == "/":
            i -= 1
            if syntaxLine[i] == "/":
                i += 1
                buildedLine = buildedLine.rstrip("//")
                buildedLine += "\033[38;5;8m//"
                while True:
                    i += 1
                    try:
                        character = syntaxLine[i]
                    except IndexError:
                        break
                    buildedLine += character
                break
            else:
                i += 1
    syntaxLine = buildedLine
    syntaxBuild = (
        backgroundColors[syntaxType]
        + colors[syntaxType]
        + syntaxLine
        + "\033[0m"
    )
    if syntaxBuild == "":
        syntaxBuild = line
    return syntaxBuild


lineWrapWarning = False
editorLinesWithSyntax = []
for line in editorLines:
    if len(line) > terminalWidth:
        lineWrapWarning = True
    editorLinesWithSyntax.append(add_syntax(line))
print(
    "This editor is only useful if you'd like syntax highlighting when you're editng. If you don't care, try using Notepad, VSCode, or any of your favorite text editors."
)
if lineWrapWarning:
    print("")
    print(
        "WARNING: Line wrap may occur and will make the editor glitch out. Instead of using this, you should use something like Notepad or VSCode to edit the ScratchScript file, as it's much better than this editor."
    )
sleep(2)
editorCurrentLine = 1
editorChar = len(editorLines[0])
realLine = 1
quoteComplete = False
parenthesisComplete = 0
capsLock = False


def on_press(keypressed):
    global realLine, editorCurrentLine, editorChar, cursorBlink, key, capsLock
    global quoteComplete, parenthesisComplete, inEditor, state
    if len(str(keypressed)) == 5:
        key = str(keypressed)[1:-1]
    else:
        key = str(keypressed).replace("'", "")
    if key == "Key.f1":
        inEditor = False
        state = "tree"
    if key == "Key.f2":
        inEditor = False
        state = "new"
    if key == "Key.up" and editorCurrentLine > 1:
        editorCurrentLine -= 1
        if editorCurrentLine == realLine - 1 and realLine > 1:
            realLine -= 1
        cursorBlink = 1
        if editorChar > len(editorLines[editorCurrentLine - 1]):
            editorChar = len(editorLines[editorCurrentLine - 1])
    if key == "Key.down" and editorCurrentLine < len(editorLines):
        editorCurrentLine += 1
        if (
            editorCurrentLine == realLine + terminalHeight - 3
            and not editorCurrentLine == len(editorLines)
        ):
            realLine += 1
        cursorBlink = 1
        if editorChar > len(editorLines[editorCurrentLine - 1]):
            editorChar = len(editorLines[editorCurrentLine - 1])
    if key == "Key.left":
        if editorChar > 1:
            editorChar -= 1
        elif editorCurrentLine > 1:
            editorChar = len(editorLines[editorCurrentLine - 2])
            editorCurrentLine -= 1
            if editorCurrentLine == realLine and realLine > 1:
                realLine -= 1
            if editorChar > len(editorLines[editorCurrentLine - 1]):
                editorChar = len(editorLines[editorCurrentLine - 1])
        if quoteComplete:
            quoteComplete = False
        cursorBlink = 1
    if key == "Key.right":
        if editorChar < len(editorLines[editorCurrentLine - 1]):
            editorChar += 1
        elif editorCurrentLine < len(editorLines):
            editorChar = 1
            editorCurrentLine += 1
            if (
                editorCurrentLine == realLine + terminalHeight - 3
                and not editorCurrentLine == len(editorLines)
            ):
                realLine += 1
            if editorChar > len(editorLines[editorCurrentLine - 1]):
                editorChar = len(editorLines[editorCurrentLine - 1])
        if quoteComplete:
            quoteComplete = False
        cursorBlink = 1
    if key == "Key.backspace":
        if editorChar == 1:
            if not editorCurrentLine == 1:
                editorChar = len(editorLines[editorCurrentLine - 2])
                transfer = (
                    editorLines[editorCurrentLine - 2].rstrip(" ")
                    + editorLines[editorCurrentLine - 1]
                )
                editorLines[editorCurrentLine - 2] = transfer
                editorLinesWithSyntax[editorCurrentLine - 2] = add_syntax(
                    transfer, False
                )
                del editorLines[editorCurrentLine - 1]
                del editorLinesWithSyntax[editorCurrentLine - 1]
                editorCurrentLine -= 1
                if realLine > 1:
                    if editorCurrentLine == realLine and realLine > 1:
                        realLine -= 1
        else:
            backspaceSplit = (
                editorLines[editorCurrentLine - 1][: editorChar - 2]
                + editorLines[editorCurrentLine - 1][editorChar - 1 :]
            )
            editorLines[editorCurrentLine - 1] = backspaceSplit
            editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                backspaceSplit, False
            )
            if editorChar > 1:
                editorChar -= 1
            editorChar = (
                len(editorLines[editorCurrentLine - 1])
                if editorChar > len(editorLines[editorCurrentLine - 1])
                else editorChar
            )
        cursorBlink = 1
    if key == "Key.delete":
        if not editorChar + 1 == len(editorLines[editorCurrentLine - 1]):
            backspaceSplit = (
                editorLines[editorCurrentLine - 1][:editorChar]
                + editorLines[editorCurrentLine - 1][editorChar + 1 :]
            )
            editorLines[editorCurrentLine - 1] = backspaceSplit
            editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                backspaceSplit, False
            )
        cursorBlink = 1
    if key == "Key.enter":
        leadings = len(editorLines[editorCurrentLine - 1]) - len(
            editorLines[editorCurrentLine - 1].lstrip(" ")
        )
        if editorChar == len(editorLines[editorCurrentLine - 1]):
            if len(editorLines[editorCurrentLine - 1]) == len(
                editorLines[editorCurrentLine - 1].lstrip(" ")
            ):
                leadings -= 1
            editorLines.insert(
                editorCurrentLine,
                (
                    leadings
                    + (
                        2
                        if leadings == -1
                        else 1
                        - (
                            1
                            if str.strip(editorLines[editorCurrentLine - 1])
                            == ""
                            else 0
                        )
                    )
                )
                * " ",
            )
            editorLinesWithSyntax.insert(
                editorCurrentLine,
                (
                    leadings
                    + (
                        2
                        if leadings == -1
                        else 1
                        - (
                            1
                            if str.strip(editorLines[editorCurrentLine - 1])
                            == ""
                            else 0
                        )
                    )
                )
                * " ",
            )
            editorChar = len(editorLines[editorCurrentLine])
        else:
            if (
                editorLines[editorCurrentLine - 1][editorChar - 1] == "}"
                and editorLines[editorCurrentLine - 1][editorChar - 2] == "{"
            ):
                leadings = len(editorLines[editorCurrentLine - 1]) - len(
                    editorLines[editorCurrentLine - 1].lstrip(" ")
                )
                lineInsert = (
                    leadings * " "
                    + editorLines[editorCurrentLine - 1][editorChar - 1 :]
                )
                editorLines[editorCurrentLine - 1] = (
                    editorLines[editorCurrentLine - 1].rstrip(lineInsert) + " "
                )
                editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                    editorLines[editorCurrentLine - 1],
                    False,
                )
                editorLines.insert(
                    editorCurrentLine, (leadings + tabSize + 1) * " "
                )
                editorLinesWithSyntax.insert(
                    editorCurrentLine, (leadings + tabSize + 1) * " "
                )
                editorLines.insert(editorCurrentLine + 1, lineInsert)
                editorLinesWithSyntax.insert(
                    editorCurrentLine + 1, add_syntax(lineInsert, False)
                )
                editorChar = leadings + tabSize + 1
                if editorCurrentLine == realLine + terminalHeight - 3:
                    realLine += 1
            else:
                lineInsert = editorLines[editorCurrentLine - 1][
                    editorChar - 1 :
                ]
                editorLines[editorCurrentLine - 1] = (
                    editorLines[editorCurrentLine - 1].rstrip(lineInsert) + " "
                )
                editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                    editorLines[editorCurrentLine - 1],
                    False,
                )
                editorLines.insert(
                    editorCurrentLine,
                    (leadings + (2 if leadings == -1 else 0)) * " "
                    + lineInsert,
                )
                editorLinesWithSyntax.insert(
                    editorCurrentLine,
                    add_syntax(
                        (leadings + (2 if leadings == -1 else 0)) * " "
                        + lineInsert,
                        False,
                    ),
                )
                editorChar = leadings + 1
        editorCurrentLine += 1
        if (
            editorCurrentLine == realLine + terminalHeight - 2
            or editorCurrentLine == realLine + terminalHeight - 3
        ):
            realLine += 1
        cursorBlink = 1
    if key == "Key.caps_lock":
        if capsLock:
            capsLock = False
        else:
            capsLock = True
    if key == "Key.space":
        key = " "
    if key == "\\\\":
        key = "\\"
    if key == "\\x13":
        key = "save"
        exit()
    if key == "Key.tab":
        key = tabSize * " "
        newLine = (
            editorLines[editorCurrentLine - 1][: editorChar - 1]
            + (key if not capsLock else key.upper())
            + editorLines[editorCurrentLine - 1][editorChar - 1 :]
        )
        editorLines[editorCurrentLine - 1] = newLine
        editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
            newLine, False
        )
        editorChar += tabSize
    if key == "Key.page_down":
        realLine += 37
        if realLine > len(editorLines):
            realLine = len(editorLines)
        editorCurrentLine = realLine
    if key == "Key.page_up":
        realLine -= 37
        if realLine < 1:
            realLine = 1
        editorCurrentLine = realLine
    if len(str(key)) == 1:
        if (
            key == '"' or key == "'"
        ):  # Bug when you press the (') key. nothing happenes. The cause of the bug is unknown, as this was working before.
            if not quoteComplete:
                newLine = (
                    editorLines[editorCurrentLine - 1][: editorChar - 1]
                    + (key if not capsLock else key.upper())
                    + editorLines[editorCurrentLine - 1][editorChar - 1 :]
                )
                editorLines[editorCurrentLine - 1] = newLine
                editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                    newLine, False
                )
                editorChar += 1
                cursorBlink = 1
                quoteComplete = True
                newLine = (
                    editorLines[editorCurrentLine - 1][: editorChar - 1]
                    + (key if not capsLock else key.upper())
                    + editorLines[editorCurrentLine - 1][editorChar - 1 :]
                )
                editorLines[editorCurrentLine - 1] = newLine
                editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                    newLine, False
                )
            else:
                editorChar += 1
                cursorBlink = 1
                quoteComplete = False
        elif key in startParenthesis:
            parenthesisComplete += 1
            previousKey = key
            newLine = (
                editorLines[editorCurrentLine - 1][: editorChar - 1]
                + key
                + editorLines[editorCurrentLine - 1][editorChar - 1 :]
            )
            editorLines[editorCurrentLine - 1] = newLine
            editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                newLine, False
            )
            editorChar += 1
            cursorBlink = 1
            if key == "(":
                key = ")"
            if key == "[":
                key = "]"
            if key == "{":
                key = "}"
                parenthesisComplete -= 1
            if key == "<":
                key = ">"
            newLine = (
                editorLines[editorCurrentLine - 1][: editorChar - 1]
                + key
                + editorLines[editorCurrentLine - 1][editorChar - 1 :]
            )
            key = previousKey
            editorLines[editorCurrentLine - 1] = newLine
            editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                newLine, False
            )
        elif key in endParenthesis:
            if parenthesisComplete > 0:
                parenthesisComplete -= 1
                editorChar += 1
                cursorBlink = 1
            else:
                newLine = (
                    editorLines[editorCurrentLine - 1][: editorChar - 1]
                    + key
                    + editorLines[editorCurrentLine - 1][editorChar - 1 :]
                )
                editorLines[editorCurrentLine - 1] = newLine
                editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                    newLine, False
                )
                editorChar += 1
                cursorBlink = 1
        else:
            if capsLock:
                newLine = (
                    editorLines[editorCurrentLine - 1][: editorChar - 1]
                    + (key.upper() if key.lower() == key else key.lower())
                    + editorLines[editorCurrentLine - 1][editorChar - 1 :]
                )
            else:
                newLine = (
                    editorLines[editorCurrentLine - 1][: editorChar - 1]
                    + key
                    + editorLines[editorCurrentLine - 1][editorChar - 1 :]
                )
            editorLines[editorCurrentLine - 1] = newLine
            editorLinesWithSyntax[editorCurrentLine - 1] = add_syntax(
                newLine, False
            )
            editorChar += 1
            cursorBlink = 1
    if editorChar < 1:
        editorChar = 1
    if editorChar > len(editorLines[editorCurrentLine - 1]):
        editorChar = len(editorLines[editorCurrentLine - 1])


def resetkey(release):
    global key
    key = ""


def inputloop():
    with pynput.keyboard.Listener(
        on_press=on_press, on_release=resetkey
    ) as listener:
        listener.join()


def editor_print(line):
    global bracketCount
    getLineCount = len(str(len(editorLines)))
    if showCwd:
        currentWorkingDirectoryString = (
            "\033[46m\033[35;1mCurrent Working Directory: "
            + folder
            + "/project.ss1"
        )
        if (
            len("Current Working Directory: ") + len(folder + "/project.ss1")
            > terminalWidth
        ):
            currentWorkingDirectoryString = (
                currentWorkingDirectoryString.rstrip(
                    currentWorkingDirectoryString[
                        terminalWidth
                        - (
                            len("Current Working Directory: ")
                            + len(folder + "/project.ss1")
                        )
                        - 4 :
                    ]
                )
                + "..."
            )
    else:
        currentWorkingDirectoryString = (
            "\033[46m\033[35;1m                           "
        )
    editorBuffer = (
        currentWorkingDirectoryString
        + (terminalWidth - (len(currentWorkingDirectoryString) - 12)) * " "
        + "\033[0m\n"
    )
    q = realLine - 1
    for i in range(line - 2):
        q += 1
        try:
            filler = (
                terminalWidth
                - (len(editorLines[q - 1]) + len(str(len(editorLines))) + 5)
            ) * " "
            editorBufferLine = (
                "\033[38;5;8m"
                + (getLineCount - len(str(q))) * " "
                + ("\033[93m" if editorCurrentLine == q else "")
                + str(q)
                + "     "
                + "\033[0m"
                + editorLinesWithSyntax[q - 1]
                + filler
                + "\n"
            )
            if editorCurrentLine == q and cursorBlink == 1:
                editorBufferBuffer = editorLines[q - 1]
                determine_type(editorBufferBuffer)
                find = colors[syntaxType]
                parenthesisCount = 0
                bracketCount = 0
                j = -1
                for k in range(len(editorBufferBuffer)):
                    quote = False
                    comment = False
                    j += 1
                    if editorChar == j + 1:
                        find += "\033[46;1m"
                    try:
                        if editorBufferBuffer[j] == '"':
                            find += '\033[38;5;34m"'
                            quote = True
                        elif editorBufferBuffer[j] == "'":
                            find += "\033[38;5;34m'"
                            quote = True
                        elif editorBufferBuffer[j] == "/":
                            j -= 1
                            if editorBufferBuffer[j] == "/":
                                j += 1
                                if editorChar == j:
                                    find += "\033[46;1m\033[38;5;8m/\033[0m\033[38;5;8m/"
                                elif editorChar == j + 1:
                                    find += "\033[0m\033[38;5;8m/\033[46;1m/\033[0m"
                                else:
                                    find += "\033[38;5;8m//"
                                comment = True
                            else:
                                j += 1
                        else:
                            find += editorBufferBuffer[j]
                    except IndexError:
                        break
                    character = editorBufferBuffer[j]
                    if editorChar == j + 1:
                        find += "\033[0m" + colors[syntaxType]
                    if character in startParenthesis:
                        if not character == "{":
                            if character == "<":
                                if not (
                                    editorBufferBuffer[j - 1] == " "
                                    or editorBufferBuffer[j + 1] == " "
                                ):
                                    parenthesisCount += 1
                                    c = 0
                                    for z in range(parenthesisCount):
                                        c += 1
                                        if c == 9:
                                            c = 1
                                    find = find.rstrip(find[-1])
                                    find += (
                                        parenthesisColors[str(c)]
                                        + (
                                            character
                                            if not editorChar == j + 1
                                            else ""
                                        )
                                        + colors[syntaxType]
                                    )
                            else:
                                parenthesisCount += 1
                                c = 0
                                for z in range(parenthesisCount):
                                    c += 1
                                    if c == 9:
                                        c = 1
                                find = find.rstrip(find[-1])
                                find += (
                                    parenthesisColors[str(c)]
                                    + (
                                        character
                                        if not editorChar == j + 1
                                        else ""
                                    )
                                    + colors[syntaxType]
                                )
                        else:
                            bracketCount += 1
                            c = 0
                            for z in range(bracketCount):
                                c += 1
                                if c == 9:
                                    c = 1
                            find = find.rstrip(find[-1])
                            find += (
                                parenthesisColors[str(c)]
                                + (
                                    character
                                    if not editorChar == j + 1
                                    else ""
                                )
                                + colors[syntaxType]
                            )
                    elif character in endParenthesis:
                        if not character == "}":
                            if character == ">":
                                if not (
                                    editorBufferBuffer[j - 1] == " "
                                    and editorBufferBuffer[j + 1] == " "
                                ):
                                    if parenthesisCount > 0:
                                        c = 0
                                        for z in range(parenthesisCount):
                                            c += 1
                                            if c == 9:
                                                c = 1
                                        find = find.rstrip(find[-1])
                                        find += (
                                            parenthesisColors[str(c)]
                                            + (
                                                character
                                                if not editorChar == j + 1
                                                else ""
                                            )
                                            + colors[syntaxType]
                                        )
                                        parenthesisCount -= 1
                            else:
                                if parenthesisCount > 0:
                                    c = 0
                                    for z in range(parenthesisCount):
                                        c += 1
                                        if c == 9:
                                            c = 1
                                    find = find.rstrip(find[-1])
                                    find += (
                                        parenthesisColors[str(c)]
                                        + (
                                            character
                                            if not editorChar == j + 1
                                            else ""
                                        )
                                        + colors[syntaxType]
                                    )
                                    parenthesisCount -= 1
                        else:
                            if bracketCount > 0:
                                c = 0
                                for z in range(bracketCount):
                                    c += 1
                                    if c == 9:
                                        c = 1
                                find = find.rstrip(find[-1])
                                find += (
                                    parenthesisColors[str(c)]
                                    + (
                                        character
                                        if not editorChar == j + 1
                                        else ""
                                    )
                                    + colors[syntaxType]
                                )
                                bracketCount -= 1
                    if character == '"':
                        if quote:
                            find += "\033[38;5;34m"
                            while True:
                                j += 1
                                try:
                                    character = editorBufferBuffer[j]
                                except IndexError:
                                    break
                                if editorChar == j + 1:
                                    find += "\033[46;1m"
                                character = editorBufferBuffer[j]
                                find += character
                                if editorChar == j + 1:
                                    find += "\033[0m" + "\033[38;5;34m"
                                if character == '"':
                                    find += colors[syntaxType]
                                    break
                        else:
                            find = find.rstrip(find[-1])
                            find += '\033[38;5;34m"'
                            while True:
                                j += 1
                                try:
                                    character = editorBufferBuffer[j]
                                except IndexError:
                                    break
                                find += character
                                if character == '"':
                                    find += colors[syntaxType]
                                    break
                    if character == "'":
                        if quote:
                            find += "\033[38;5;34m"
                            while True:
                                j += 1
                                try:
                                    character = editorBufferBuffer[j]
                                except IndexError:
                                    break
                                if editorChar == j + 1:
                                    find += "\033[46;1m"
                                character = editorBufferBuffer[j]
                                find += character
                                if editorChar == j + 1:
                                    find += "\033[0m" + "\033[38;5;34m"
                                if character == "'":
                                    find += colors[syntaxType]
                                    break
                        else:
                            find = find.rstrip(find[-1])
                            find += "\033[38;5;34m'"
                            while True:
                                j += 1
                                try:
                                    character = editorBufferBuffer[j]
                                except IndexError:
                                    break
                                find += character
                                if character == "'":
                                    find += colors[syntaxType]
                                    break
                    if character == "/":
                        j -= 1
                        if editorBufferBuffer[j] == "/":
                            j += 1
                            if comment:
                                find += "\033[38;5;8m"
                                while True:
                                    j += 1
                                    try:
                                        character = editorBufferBuffer[j]
                                    except IndexError:
                                        break
                                    if editorChar == j + 1:
                                        find += "\033[46;1m"
                                    character = editorBufferBuffer[j]
                                    find += character
                                    if editorChar == j + 1:
                                        find += "\033[0m" + "\033[38;5;8m"
                            else:
                                find = find.rstrip("//")
                                if editorChar == j:
                                    find += "\033[46;1m\033[38;5;8m/\033[0m\033[38;5;8m/"
                                elif editorChar == j + 1:
                                    find += "\033[38;5;8m/\033[46;1m/\033[0m"
                                else:
                                    find += "\033[38;5;8m//"
                                while True:
                                    j += 1
                                    try:
                                        character = editorBufferBuffer[j]
                                    except IndexError:
                                        break
                                    find += character
                                break
                        else:
                            j += 1
                            if not editorBufferBuffer[j + 1] == "/":
                                if editorChar == j + 1:
                                    find += "\033[46;1m/\033[0m"
                                else:
                                    find += character
                editorBufferLine = (
                    "\033[38;5;8m"
                    + (getLineCount - len(str(editorCurrentLine))) * " "
                    + "\033[93m"
                    + str(editorCurrentLine)
                    + "     "
                    + "\033[0m"
                    + find
                    + "\033[0m"
                    + filler
                    + "\033[0m\n"
                )
        except IndexError:
            editorBufferLine = (
                "\033[38;5;8m~\033[0m     " + (terminalWidth - 6) * " " + "\n"
            )
        editorBuffer += editorBufferLine
    print("\033[H\033[3J", end="")
    print(editorBuffer + "\033[A")


# https://stackoverflow.com/questions/7168508/background-function-in-python
# ---


class CursorBlink(threading.Thread):
    def __init__(self, increment):
        threading.Thread.__init__(self)
        self.runnable = increment
        self.daemon = True

    def run(self):
        self.runnable()


cursorBlinkLoop = CursorBlink(increment)
cursorBlinkLoop.start()


class InputLoop(threading.Thread):
    def __init__(self, inputloop):
        threading.Thread.__init__(self)
        self.runnable = inputloop
        self.daemon = True

    def run(self):
        self.runnable()


keyPressLoop = CursorBlink(inputloop)
keyPressLoop.start()


# ---
def editor():
    global terminalHeight, terminalWidth, inEditor, cursorBlink, key
    subprocess.run("bash -c clear", shell=False)
    editor_print(terminalHeight)
    while inEditor:
        terminalHeight = shutil.get_terminal_size().lines
        terminalWidth = shutil.get_terminal_size().columns
        editor_print(terminalHeight)
        cursorBlinkPrevious = cursorBlink
        while True:
            if not cursorBlinkPrevious == cursorBlink:
                break
            if not key == "":
                if key == "save":
                    projectDir = (
                        os.getcwd().replace("\\", "/") + "/project.ss1"
                    )
                    print("Saving to " + projectDir + "...")
                    with open(projectDir, "w") as fp:
                        for item in editorLines:
                            fp.write("%s\n" % item.rstrip(" "))
                    inEditor = False
                    print("Done. Press ctrl+c to exit.")
                    exit()
                break


state = "edit"
while True:
    if state == "edit":
        editor()
    elif state == "tree":
        print("Open a ScratchScript file.")
        folder = ""
        sleep(2)
        folder = fd.askopenfilename(
            title="Choose a file.",
            initialdir="../ ",
            filetypes=(
                ("ScratchScript 1 files", "*.ss1"),
                ("All Files", "*.*"),
            ),
        )
        folder = folder.replace("\\", "/")
        if folder == "":
            error("Empty path.")
            exit()
        sys.argv = [currentWorkingDirectory + "\\\\editor.py", folder]
        runpy.run_path(sys.argv[0])
    elif state == "new":
        os.chdir("..")
        z = 0
        while True:
            z += 1
            if not os.path.isdir("Sprite" + str(z)):
                break
        os.mkdir("Sprite" + str(z))
        os.chdir("Sprite" + str(z))
        os.mkdir("assets")
        h = open("project.ss1", "w")
        h.write("ss1")
        h.close()
        sys.argv = [
            currentWorkingDirectory + "/editor.py",
            os.getcwd().replace("\\", "/") + "/project.ss1",
        ]
        runpy.run_path(sys.argv[0])
