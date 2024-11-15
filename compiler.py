import os #used to compile C code automatically at the end


#whether or not the translated C code should be instantly compiled into .exe format, requires gcc
instantCompile = False

#the base code structure for any C code
cCode = ["#include <stdio.h>\n", "\n"]


#dictionary assigning atr functions to their C counterparts
atrCommands = {"print": "printf"}

#dictionary containing all variable format specifiers
formatSpecifierTable = {"char": "c", "int": "i", "float": "f"}


def interpret(code: list[str], indent=0) -> tuple[list[str], list[str]]:
    global formatSpecifierTable
    """
    Compiles atr code to C code, taking in a list of strings, the lines of atr code, and returning lines of c code.
    indent can be set to automatically indent the generated C code. Useful when calling recursively, for example in nested loops.
    """
    #all defined functions need to be added before the main function in the C code
    functions: list[str] = []
    finalCode: list[str] = []
    variables: dict[str: str] = {}

    commentLines = 0 #counting the amount of full line comments that were removed from the list to subtract from lineIndex

    for lineIndex, line in enumerate(code):
        finalCode.append(" "*indent) #add indent
        currentIndex = lineIndex - commentLines
        splitLine = line.split(" ")
        for splitIndex in range(len(splitLine)):
            skipLine = False

            while splitLine[0] == " ": #remove indents at the start of line
                splitLine = splitLine[1:]
            
            if splitLine[-1].endswith("\n"):
                splitLine[-1] = splitLine[-1][:-1]
            
            currentCommand = splitLine[splitIndex]

            if currentCommand.startswith("#"): #skip comments
                if splitLine[0].startswith("#"): #completely ignore line if it was a comment
                    skipLine = True
                    finalCode.pop()
                    commentLines += 1
                break

            if currentCommand in atrCommands.keys():
                finalCode[currentIndex] += atrCommands[currentCommand] + "(" #add the translated C command and the opening bracket
                value = line.replace(")", "(").split("(")[1] #get the parameter of the function
                #if not value.startswith("\""): #allow other data types than str to be printed as values
                #    value = "\"" + value + "\""
                finalCode[currentIndex] += value + ")"
        
            elif currentCommand == "var" and splitLine[0].startswith("var"):
                value = splitLine[3:]
                finalValue = splitLine[3]
                while len(value) > 1: #in case the value to be assigned contained a space (for example in strings), keep adding the rest of the line together until the full value is reached
                    finalValue += " " + value.pop(1)
                value = finalValue
                varType = None

                if value.startswith("\"") and (stringLength := len(value.replace("\"", ""))) == 1:
                    varType = "char"
                elif value.startswith("\""):
                    #there is a special syntax for "strings" in C, consisting of an array of char elements
                    finalCode[currentIndex] += "char {}[] = {}".format(splitLine[1], value)
                    variables[splitLine[1]] = "s" #C requires a format specifier for every variable to be printed correctly
                
                if varType:
                    finalCode[currentIndex] += "{} {} = {}".format(varType, splitLine[1], value)
                    variables[splitLine[1]] = formatSpecifierTable[varType]

        
        if not skipLine:
            if len(finalCode[currentIndex].replace(" ", "")): #if there was no (translatable) content on the line, do not add semicolon
                finalCode[currentIndex] += ";"
            finalCode[currentIndex] += "\n"
    
    return functions, finalCode


#compile all the lines in main.atr
with open("main.atr", "r") as f:
    lines = f.readlines()
    functions, interpretedLines = interpret(lines, indent=4)
    cCode += functions
    cCode += "int main() {\n"
    cCode += interpretedLines
        

cCode += ["""    return 0;\n}\n"""]

#write the code to main.c
with open("main.c", "w") as f:
    for line in cCode:
        f.write(line)

if instantCompile:
    #compile the finished C code
    os.system("gcc main.c")
