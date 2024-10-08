import os #used to compile C code automatically at the end


#whether or not the translated C code should be instantly compiled into .exe format, requires gcc
instantCompile = False

#the base code structure for any C code
cCode = \
"""#include <stdio.h>

"""

#dictionary assigning atr functions to their C counterparts
atrCommands = {"print": "printf"}

#dictionary containing all assigned variable names
definedVariables = {}


def interpret(code: list[str], indent=0) -> tuple[list[str], list[str]]:
    """
    Compiles atr code to C code, taking in a list of strings, the lines of atr code, and returning lines of c code.
    indent can be set to automatically indent the generated C code. Useful when calling recursively, for example in nested loops.
    """
    #all defined functions, need to be added before the main function in the C code
    functions: list[str] = []
    finalCode: list[str] = []

    for lineIndex, line in enumerate(code):
        finalCode.append(" "*indent)
        splitLine = line.split(" ")
        for splitIndex in range(len(splitLine)):
            skipLine = False
            currentCommand = splitLine[splitIndex]
            if currentCommand.startswith("#"): #skip comments
                if splitLine[0].startswith("#"): #completely ignore line if it was a comment
                    skipLine = True
                    finalCode.pop()
                break

            if currentCommand in atrCommands.keys():
                finalCode[lineIndex] += atrCommands[currentCommand] + "(" #add the translated C command and the opening bracket
                value = line.replace(")", "(").split("(")[1] #get the parameter of the function
                if not value.startswith("\""): #allow other variable types than str to be printed as values
                    value = "\"" + value + "\""
                finalCode[lineIndex] += value + ")"
        
        if not skipLine:
            if len(finalCode[lineIndex].replace(" ", "")): #if there was no (translatable) content on the line, do not add semicolon
                finalCode[lineIndex] += ";"
            finalCode[lineIndex] += "\n"
    
    return functions, finalCode


#compile all the lines in main.atr
with open("main.atr", "r") as f:
    lines = f.readlines()
    functions, interpretedLines = interpret(lines, indent=4)
    for line in functions:
        cCode += line
    cCode += "int main() {\n"
    for line in interpretedLines:
        cCode += line
        

cCode += """    return 0;
}
"""

#write the code to main.c
with open("main.c", "w") as f:
    f.write(cCode)

if instantCompile:
    #compile the finished C code
    os.system("gcc main.c")
