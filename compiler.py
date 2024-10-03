import os #used to compile C code automatically at the end


#whether or not the translated C code should be instantly compiled into .exe format
instantCompile = False

#the base code structure for any C code
cCode = """#include <stdio.h>
int main() {"""

#dictionary assigning atr functions to their C counterparts
atrCommands = {"print": "printf"}


def interpret(code: list[str], indent=0) -> list[str]:
    """
    Compiles atr code to C code, taking in a list of strings, the lines of atr code, and returning lines of c code.
    indent can be set to automatically indent the generated C code. Useful when calling recursively, for example in nested loops.
    """
    finalCode = []
    for i, line in enumerate(code):
        finalCode.append("")
        splitLine = line.split(" ")
        for splitIndex in range(len(splitLine)):
            currentCommand = splitLine[splitIndex]
            if currentCommand in atrCommands.keys():
                finalCode[i] += atrCommands[currentCommand] + "(" #add the translated C command and the opening bracket
                value = line.replace(")", "(").split("(")[1] #get the value of the function
                if not value.startswith("\""): #allow other variable types than str to be printed as values
                    value = "\"" + value + "\""
                finalCode[i] += value + ")"
            finalCode[i] += ";\n"
    
    return finalCode


with open("main.atr", "r") as f:
    lines = f.readlines()
    interpretedLines = interpret(lines)
    for line in interpretedLines:
        cCode += line

cCode += """
return 0;
}
"""

with open("main.c", "w") as f:
    f.write(cCode)

if instantCompile:
    #compile the finished C code
    os.system("gcc main.c")
