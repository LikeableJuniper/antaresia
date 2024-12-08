import os #used to compile C code automatically at the end


#whether or not the translated C code should be instantly compiled into .exe format, requires gcc
instantCompile = False

#the base code structure for any C code
cCode = ["#include <stdio.h>\n", "\n"]


#dictionary assigning atr functions to their C counterparts
atrCommands = {"print": "printf"}

#dictionary containing all variable format specifiers
formatSpecifierTable = {"char": "c", "int": "i", "float": "f"}

#the amount of spaces to use for indent in translated C code
indentAmount = 4


def interpret(code: list[str], indent=0) -> tuple[list[str], list[str], int]:
    global formatSpecifierTable
    """
    Compiles atr code to C code, taking in a list of strings, the lines of atr code, and returning lines of c code.
    indent can be set to automatically indent the generated C code. Useful when calling recursively, for example in nested loops.
    """
    #all defined functions need to be added before the main function in the C code
    functions: list[str] = []
    finalCode: list[str] = []
    variables: dict[str: str] = {}

    functionLineShift = 0 #lines in functions to be added to lineIndex

    for lineIndex, line in enumerate(code):
        currentIndex = lineIndex + functionLineShift
        if lineIndex < currentIndex: #skip lines already interpreted in recursive calls as functions
            continue
        splitLine = line.split(" ")
        finalCode.append(" "*indent*4) #add indent
        while not splitLine[0]:
            splitLine = splitLine[1:]
        
        for splitIndex in range(len(splitLine)):
            skipLine = False

            while splitLine[0] == " ": #remove indents at the start of line
                splitLine = splitLine[1:]
            
            if splitLine[-1].endswith("\n"):
                splitLine[-1] = splitLine[-1][:-1]
            
            currentCommand = splitLine[splitIndex]

            if currentCommand == "func":
                functions.append("int {}()".format(splitLine[1]) + " {\n")
                _, functionCode, lineShift = interpret(code[lineIndex+1:], 1) #recursive call enables functions and loops to be interpreted easily
                for functionLine in functionCode:
                    functions.append(functionLine)
                functionLineShift += lineShift+2
                
            
            if currentCommand == "}":
                break

            if currentCommand == "return":
                finalCode[-1] += "return {};\n".format(splitLine[1])
                finalCode.append("}")

            if currentCommand.startswith("#"): #skip comments
                if splitLine[0].startswith("#"): #completely ignore line if it was a comment
                    skipLine = True
                    finalCode.pop()
                break

            if currentCommand in atrCommands.keys():
                finalCode[-1] += atrCommands[currentCommand] + "(" #add the translated C command and the opening bracket
                value = line.replace(")", "(").split("(")[1] #get the parameter of the function
                finalCode[-1] += value + ")"
        
            elif currentCommand == "var" and splitLine[0].startswith("var"):
                value = splitLine[3:]
                finalValue = splitLine[3]
                while len(value) > 1: #in case the value to be assigned contained a space (for example in strings), keep adding the rest of the line together until the full value is reached
                    finalValue += " " + value.pop(1)
                value = finalValue
                varType = None

                if value.startswith("\"") and len(value.replace("\"", "")) == 1:
                    varType = "char"
                elif value.startswith("\""):
                    #there is a special syntax for "strings" in C, consisting of an array of char elements
                    finalCode[-1] += "char {}[] = {}".format(splitLine[1], value)
                    variables[splitLine[1]] = "s" #C requires a format specifier for every variable to be printed correctly
                
                if varType:
                    finalCode[-1] += "{} {} = {}".format(varType, splitLine[1], value)
                    variables[splitLine[1]] = formatSpecifierTable[varType]

        
        if not skipLine:
            if len(finalCode[-1].replace(" ", "")): #if there was no (translatable) content on the line, do not add semicolon
                finalCode[-1] += ";"
            finalCode[-1] += "\n"
    
    return functions, finalCode, lineIndex


#compile all the lines in main.atr
with open("main.atr", "r") as f:
    lines = f.readlines()
    functions, interpretedLines, _ = interpret(lines, indent=1)
    print(functions, interpretedLines, _)
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
