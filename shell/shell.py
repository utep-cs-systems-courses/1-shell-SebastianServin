#! /usr/bin/python3

from fileinput import close
import os, sys, re

# Returns true if I can be converted to an integer.
def isInt(i):
    try: 
        int(i)
        return True
    except ValueError:
        return False

# Runs when 'exit' is used.
def runExit(val):

    # No exit code given
    if len(val) == 1:
        os.write(2, ("Terminating now with exit code %d\n" %0).encode())
        sys.exit(0)
    
    # Exit code given
    else:
        exitCode = val[1]
        if isInt(exitCode):
            os.write(2, ("Terminating now with exit code %d\n" %int(exitCode)).encode())
            sys.exit(int(exitCode))
        else:
            os.write(2, ("Invalid exit code. Exiting now with exit code 0\n").encode())
            sys.exit(0)

# Runs when 'cd' is used.
def runCD(val):
    # No path specificed, will return to home directory
    if len(val) == 1:
        os.chdir(os.environ['HOME'])
        return
    try:
        os.chdir(val[1])
        # os.write(1, ("(%s): " %os.getcwd()).encode())
    except:
        os.write(2, ("Not a valid directory :(\n").encode())

def execCommand(val, background):
    if background:
        val = val.replace('&', '')
    args = val.split()
    rc = os.fork()

    if rc < 0:
        sys.exit(1)

    elif rc == 0:
        dirs = re.split(":", os.environ['PATH'])
        dirs.append('')
        for dir in dirs:
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass

    
        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)

    else:
        if not background:
            os.wait()


def runRedirect(val):
    symbol = val[len(val) - 2]
    destinationFile = val[len(val) - 1]

    rc = os.fork()

    if rc < 0:
        sys.exit(1)

    elif rc == 0:
        args = []
        
        # Stores function to call along with args
        for i in range(len(val) - 2):
            args.append(val[i])
            
        if symbol == ">":
            # redirect child's stdout
            os.close(1)
            os.open(destinationFile, os.O_CREAT | os.O_WRONLY)
            os.set_inheritable(1, True)
        else:
            os.close(0)
            os.open(destinationFile, os.O_RDONLY)
            os.set_inheritable(0, True)

        for dir in re.split(":", os.environ['PATH']):
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass
        
        sys.exit(1)

    elif rc != 0: 
            os.wait()


def runPipe(unsplitString):
    argsTemp = unsplitString.split(' | ')
    # pid = os.getpid()

    pr,pw = os.pipe()
    for f in (pr, pw):
        os.set_inheritable(f, True)

    rc = os.fork()

    if rc < 0:
        sys.exit(1)

    elif rc == 0:

        os.close(1)
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        dirs = re.split(":", os.environ['PATH'])
        dirs.append('')
        for dir in dirs:
            argsOne = argsTemp[0].split()
            program = "%s/%s" % (dir, argsOne[0])
            try:
                os.execve(program, argsOne, os.environ)
            except FileNotFoundError:
                pass                             
                
    else:
        pass

    pipe2 = os.fork()

    if pipe2 < 0:
        sys.exit(1)

    elif pipe2 == 0:
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pw, pr):
            os.close(fd)
        dirs = re.split(":", os.environ['PATH'])
        dirs.append('')
        for dir in dirs:
            argsTwo = argsTemp[1].split()
            program = "%s/%s" % (dir, argsTwo[0])
            try:
                os.execve(program, argsTwo, os.environ)
            except FileNotFoundError:
                pass                             

    else:
        pass
    
            

while True:
    os.write(2, ("(%s): " %os.getcwd()).encode())
    vals = (os.read(0,1000)).decode()
    # split val by \n
    # loop through values
    #     search for pipe in val
    #     split
    #     search for cd in val[0]
    #     search for exit in val[0]
    #     search for redirect 
    #     else run general command
    vals = vals.split('\n')
    for val in vals:
        if len(val) > 0:
            unsplitString = val
            val = val.split()
            if '|' in unsplitString:
                runPipe(unsplitString)
            elif val[0] == "cd":
                if (len(val) > 0):
                    runCD(val)
            elif val[0] == "exit":
                if (len(val) > 0):
                    runExit(val)
            elif val[len(val) - 2].lower() == ">" or val[len(val) - 2].lower() == "<":
                if (len(val) > 0):
                    runRedirect(val)
            else:
                if '&' in unsplitString:
                    execCommand(unsplitString, True)
                else:
                    execCommand(unsplitString, False)
    # exit()
    # sys.exit()