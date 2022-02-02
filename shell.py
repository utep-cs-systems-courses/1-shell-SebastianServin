from ast import Try
import os, sys, re

def isInt(i):
    try: 
        int(i)
        return True
    except ValueError:
        return False

def runExit(val):
    if len(val) == 1:
        os.write(1, ("Terminating now with exit code %d\n" %0).encode())
        sys.exit(0)
    else:
        exitCode = val[1]
        if isInt(exitCode):
            os.write(1, ("Terminating now with exit code %d\n" %int(exitCode)).encode())
            sys.exit(int(exitCode))
        else:
            os.write(1, ("Invalid exit code. Exiting now with exit code 0\n").encode())
            sys.exit(0)

def runCD(val):
    if len(val) == 1:
        os.chdir(os.environ['HOME']);
        return
    try:
        if val[1] == "..":
            os.chdir(os.path.dirname(os.getcwd()))
        else:    
            os.chdir(val[1])
    except:
        os.write(1, ("Not a valid directory :(\n").encode())

while True:
    os.write(1, ("(%s): " %os.getcwd()).encode())
    val = input()
    val = val.split()
    if len(val) > 0:
        if val[0].lower() == "exit":
            runExit(val)
        elif val[0].lower() == "cd":
            runCD(val)
        else:
            os.write(1, ("Invalid command :(\n").encode())