import os #used to compile C code automatically at the end

#The base code structure for any C code
cCode = """#include <stdio.h>
int main() {"""

#dictionary assigning atr functions to their C counterparts
atrCommands = {"print": "printf"}

with open("main.atr", "r") as f:
    lines = f.readlines()
    for line in lines:
        cCode += "\n"
        splitLine = line.split(" ")
        for i in range(len(splitLine)):
            currentCommand = splitLine[i]
            if currentCommand in atrCommands.keys():
                cCode += atrCommands[currentCommand] + "(" #add the translated C command and the opening bracket
                value = line.replace(")", "(").split("(")[1] #get the value of the function
                if not value.startswith("\""): #allow other variable types than str to be printed as values
                    value = "\"" + value + "\""
                cCode += value + ")"
        cCode += ";"

cCode += """
return 0;
}
"""

with open("main.c", "w") as f:
    f.write(cCode)

#compile the finished C code
os.system("gcc main.c")
