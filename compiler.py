import os #used to compile C code automatically at the end


#whether or not the translated C code should be instantly compiled into .exe format, requires gcc
instantCompile = False

#the base code structure for any C code
cCode = ["#include <stdio.h>\n", "\n"]


#dictionary assigning atr functions to their C counterparts
atrCommands = {"print": "printf"}

#dictionary assigning atr boolean operators to their C counterparts
atrBooleanOperators = {"and": "&&", "or": "||", "not": "!"}

#dictionary containing all variable format specifiers
formatSpecifierTable = {"int": "i", "float": "f", "string": "s"}

#the amount of spaces to use for indent in translated C code
indentAmount = 4

#tuple of digits to check the format of a value when printing (special syntax required when printing numbers)
digits = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")

#list of math symbols to recognize when a value should be interpreted as math
mathSigns = ("+", "-", "*", "/", "^")


def readFunctionArguments(arguments: list[str]) -> str:
    """Translates function arguments to C, returns the arguments as a single string."""
    functionCallArguments = ""
    for i in range(len(arguments)):
        functionCallArguments += arguments[i]
        if i < len(arguments)-1:
            functionCallArguments += " "
    
    functionCallArguments = functionCallArguments.replace("(", "").replace(")", "")
    return functionCallArguments


def addDicts(dict1: dict, dict2: dict):
    for key, value in enumerate(dict2):
        if not key in dict1:
            dict1[key] = value
    return dict1


def readVariableDefinition(variableTypes: dict, definedFunctions: dict, splitLine: list[str], expectVarKeyword=True):
    result = ""
    if not expectVarKeyword:
        splitLineShift = -1
    else:
        splitLineShift = 0

    varName = splitLine[1+splitLineShift]
    value = splitLine[3+splitLineShift:]
    finalValue = splitLine[3+splitLineShift]
                #in case the value to be assigned contained a space (for example in strings or addition), keep adding the rest of the line together until the full value is reached, unless the first part was a recognized user-defined function
    if not value[0] in definedFunctions.keys():
        while len(value) > 1:
            finalValue += " " + value.pop(1)
    value = finalValue
    varType = None

    if value in variableTypes.keys():
        varType = variableTypes[value]
                
    elif value in definedFunctions.keys():
        varType = definedFunctions[value]
        if varType == "string":
            result = "char {}[] = {};\n".format(splitLine[1+splitLineShift], splitLine[3+splitLineShift]+splitLine[4+splitLineShift])
        else:
            result = "{} {} = {};\n".format(varType, splitLine[1+splitLineShift], splitLine[3+splitLineShift]+splitLine[4+splitLineShift])
        return result, varName, varType

    elif value.startswith("\""):
        #there is a special syntax for "strings" in C, consisting of an array of char elements
        result = "char {}[] = {};\n".format(varName, value)
        variableTypes[varName] = "string" #C requires a format specifier for every variable to be printed correctly
                
    elif any((sign in value) for sign in mathSigns): #if there is any mathematical sign and the value isn't a string, interpret value as math
        result = "float {} = {};\n".format(varName, value)
        variableTypes[varName] = "float" #convert any mathematical operation to float since it's easier to always assume a float and integers can be displayed as x.0
                
    elif value.startswith(digits):
        if "." in value:
            varType = "float"
        else:
            varType = "int"

    if varType:
        result = "{} {} = {};\n".format(varType, varName, value)
        variableTypes[varName] = varType
    
    return result, varName, varType



def interpret(code: list[str], indent=0, definedVariables: dict[str: str]={}) -> tuple[list[str], list[str], int]:
    global formatSpecifierTable
    """
    Compiles atr code to C code, taking in a list of strings, the lines of atr code, and returning lines of c code.
    indent can be set to automatically indent the generated C code. Useful when calling recursively, for example in nested loops.
    """
    #all defined functions need to be added before the main function in the C code
    functions: list[str] = []
    finalCode: list[str] = []
    variableTypes: dict[str: str] = {}
    definedFunctions: dict[str: str] = {}

    recursiveLineShift = 0 #lines in functions to be added to lineIndex
    targetIndex = 0

    endInterpretation = False

    for lineIndex, line in enumerate(code):
        if lineIndex < targetIndex: #skip lines already interpreted in recursive calls as functions
            continue
        splitLine = line.split(" ")
        finalCode.append(" "*indent*4) #add indent
        while not splitLine[0]:
            splitLine = splitLine[1:]
        
        for splitIndex in range(len(splitLine)):
            skipToNextLine = False

            while splitLine[0] == " ": #remove indents at the start of line
                splitLine = splitLine[1:]
            
            if splitLine[-1].endswith("\n"): #remove newlines at the end of lines
                splitLine[-1] = splitLine[-1][:-1]

            currentCommand = splitLine[splitIndex]

            if currentCommand == "if":
                condition = ""
                for conditionPart in splitLine[1:-1]:
                    if conditionPart in atrBooleanOperators.keys():
                        condition += atrBooleanOperators[conditionPart] + ("" if conditionPart == "not" else " ") #append a space if the boolean operator is "and" or "or" since "not" usually stands before the value without a space
                    elif conditionPart in ["True", "False"]:
                        condition += "1" if conditionPart == "True" else "0" #C does not contain booleans as "true" and "false", instead they are treated as integers, 1 and 0
                    else:
                        condition += conditionPart + " "
                    
                finalCode[-1] += "if ({}) ".format(condition) + "{\n"

                _, statementCode, lineShift = interpret(code[lineIndex+1:], indent+1, definedVariables=addDicts(definedVariables, variableTypes)) #carry over newly defined variables as well as already defined ones
                for statementLine in statementCode:
                    finalCode.append(statementLine)
                
                if indent == 1:
                    print(finalCode)
                recursiveLineShift += lineShift+2
                targetIndex = lineIndex + recursiveLineShift
                skipToNextLine = True

            if currentCommand == "while":
                pass

            if currentCommand == "func":
                functionName = splitLine[1]
                argList = ""
                for i in range(len(splitLine[2:-3])): #skip over return type declaration and opening curely bracket with :-3
                    argList += splitLine[2+i]
                
                argList = argList.replace(")", "").replace("(", "").split(",") #this takes all the arguments in the brackets in .atr and splits them at commas
                stringArguments = ""
                dictArguments = {}
                returnType = splitLine[-2]
                functionDefinition = "{} {}(".format(returnType, functionName)

                if argList[0]: #only search for arguments if there are any
                    for i, argument in enumerate(argList):
                        argumentName, argumentType = argument.replace(" ", "").split(":")
                        stringArguments += argumentName
                        
                        dictArguments[argumentName] = argumentType

                        if argumentType == "string":
                            functionDefinition += "char {}[]".format(argumentName)
                        else:
                            functionDefinition += "{} {}".format(argumentType, argumentName)

                        if i != len(argList) - 1:
                            stringArguments += ", " #append comma only if this isn't the last argument
                            functionDefinition += ", "
                
                functionDefinition += ")"
                
                functions.append(functionDefinition + " {\n")
                definedFunctions[functionName] = splitLine[-2]
                _, functionCode, lineShift = interpret(code[lineIndex+1:], 1, definedVariables=dictArguments) #recursive call enables functions and loops to be interpreted easily
                for functionLine in functionCode:
                    functions.append(functionLine)
                print(functionCode)
                recursiveLineShift += lineShift+3
                targetIndex = lineIndex + recursiveLineShift
                del finalCode[-1] #since no line in main code is needed, remove already added indents
                skipToNextLine = True

            if currentCommand == "}":
                endInterpretation = True
                skipToNextLine = True
                del finalCode[-1]
                break

            if currentCommand == "return":
                finalCode[-1] += "return {};\n".format(splitLine[1])
                endInterpretation = True
                skipToNextLine = True
                break

            if currentCommand.startswith("#"): #skip comments
                if splitLine[0].startswith("#"): #completely ignore line if it was a comment
                    skipToNextLine = True
                    finalCode.pop()
                break

            if currentCommand in atrCommands.keys():
                finalCode[-1] += atrCommands[currentCommand] + "(" #add the translated C command and the opening bracket
                value = line.replace(")", "(").split("(")[1] #get the parameter of the function

                if currentCommand == "print":
                    if value in definedVariables:
                        varType = definedVariables[value]

                    elif value in variableTypes:
                        varType = variableTypes[value]
                    
                    elif value.startswith(("\"", "'")):
                        varType = "string"
                    elif value.startswith(digits + ("-",)):
                        if "." in value:
                            varType = "float"
                        else:
                            varType = "int"

                    value = "\"%{}".format(formatSpecifierTable[varType]) + r'\n", ' + f"{value}" #r before string makes escape characters (\) be accepted as normal characters instead of actual escape characters

                finalCode[-1] += value + ");\n"
                skipToNextLine = True
        
            elif currentCommand in definedFunctions.keys():
                functionCallArguments = readFunctionArguments(splitLine[1:])
                finalCode[-1] += "{}({});\n".format(currentCommand, functionCallArguments)
                skipToNextLine = True

            elif currentCommand == "var":
                definition, varName, varType = readVariableDefinition(variableTypes, definedFunctions, splitLine)
                finalCode[-1] += definition
                definedVariables[varName] = varType
                skipToNextLine = True

            elif currentCommand in definedVariables.keys():
                reDefinition, _, _ = readVariableDefinition(variableTypes, definedFunctions, splitLine, expectVarKeyword=False)
                print(reDefinition)
                reDefinition = reDefinition.split(" ")[1:] #remove type redeclaration since C does not accept redefinitions of the same variable
                definitionNoType = ""
                for definitionPart in reDefinition:
                    definitionNoType += definitionPart + " "
                
                print(reDefinition)
                finalCode[-1] += definitionNoType
                skipToNextLine = True

            if skipToNextLine:
                break

        if not skipToNextLine:
            if len(finalCode[-1].replace(" ", "")) and ("}" not in finalCode[-1]): #if there was no (translatable) content on the line, do not add semicolon
                finalCode[-1] += ";"
            finalCode[-1] += "\n"
        
        if endInterpretation:
            finalCode.append(" "*(indent-1)*4 + "}\n")
            break
    
    return functions, finalCode, lineIndex


#compile all the lines in main.atr
with open("main.atr", "r") as f:
    lines = f.readlines()
    functions, interpretedLines, _ = interpret(lines, indent=1)
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
