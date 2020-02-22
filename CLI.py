# Purpose: The purpose of this script is to provide an easy to use, as modular
# as possible command line interface. Simply paste in this block, then edit.

### Import modules
from sys import exit, argv, stdout, stdin # Command line interface
from tty import setraw, setcbreak # Raw input
from termios import tcgetattr, tcsetattr, TCSAFLUSH # Backup/resume shell
from os.path import exists # Reading input files
from os import popen, remove # Detect terminal size
from re import sub # Change menu to try to avoid text wrapping
from os import listdir # Directory traversal

# Class: c(olors)
# Purpose: provide access to ANSI escape codes for styling output
class c():
    HEADER = '\033[95m' # Pink
    OKBLUE = '\033[94m' # Purple
    OKGREEN = '\033[92m' # Green
    WARNING = '\033[93m' # Yellow
    FAIL = '\033[91m' # Red
    ENDC = '\033[0m' # None
    BOLD = '\033[1m' # Blue
    UNDERLINE = '\033[4m' # Underline

# Method: ActivateInterface
# Purpose: Activate the command line interface.
# Parameters: none.
def ActivateInterface():
    # If the user just runs the file, notify them that they can use "-a"
    # to enter "Authoring Mode". Then build the site.
    if (len(argv) == 1 or len(argv) == 2 and "-v" in argv):
        print(c.UNDERLINE+"Note"+c.ENDC+": You can use '-a' to enter 'Authoring Mode'")
    # If they have run the program with a single parameter, bounds check
    # it, then send them to the interface
    elif (len(argv) < 4):
        # Don't allow double or single quatation marks, or input over 2
        # characters long
        if ('"' in argv[1] or "'" in argv[1] or len(argv[1]) > 2):
            print(c.FAIL+"Invalid parameters"+c.ENDC)
            exit(0)

        # Send the user to the CLI
        DisplayInterface(argv[1:])

    else: # Too many parameters
        print(c.FAIL+"Too many parameters"+c.ENDC)
        exit(0)

# Method: DisplayInterface
# Purpose: Provide a command line interface for the script, for more granular control
# of its operation.
# Parameters: params: command line parameters (String)
def DisplayInterface(params,search_query="",end_action="continue"):
    # If the exit flag is set, check for other flags, then exit.
    if ("--exit" in params):
        end_action = "quit"

    # Store the menu in a variable so as to provide easy access at any point in time.
    menu = f"""
    * To revert post timestamps:                     {c.OKGREEN}-r{c.ENDC}
    * To clear all structure files:                  {c.OKGREEN}-R{c.ENDC}
    * To display this menu:                          {c.WARNING}-h{c.ENDC}
    * To exit this mode and build the site:          {c.FAIL}exit{c.ENDC}
    * To exit this mode and quit the program:        {c.FAIL}!exit{c.ENDC}
    """

    # If the terminal window is less than 59 characters wide, resize the menu
    # to better fit.
    rows, columns = popen('stty size', 'r').read().split()
    if (int(columns) < 59):
        menu = sub(":\s+", ":\n        ", menu)

    # Continue prompting the user for input until they enter a valid argument
    while (True):
        if ("-a" in params): # Get new input
            print(menu)
            params = GetUserInput("#: ")
        if ("-h" in params or "help" in params): # Print help menu
            print(f'Entering "-h" at any time will display the menu below.\n{menu}')
        elif ("-r" in params): # Revert post timestamps
            print("Reverting post timestamps.")
            for files in listdir("./content"):
                if (files.endswith(".txt")):
                    Revert("./content/"+files)
        elif ("-R" in params): # Rebuild all structure files
            print("Rebuilding all structure files.")
            for file in listdir("./html/blog"):
                if (file.endswith(".html")):
                    remove("./html/blog/"+file)
            return False
        elif ("!exit" in params): # Exit without building site
            exit(0)
        else: # Exit then build site
            return False

        if (end_action == "continue"):
            params = GetUserInput("#: ")
        else:
            # Cleanup
            del menu
            break

# Method: GetUserInput
# Purpose: Accept user input and perform basic bounds checking
# Parameters:
# - prompt: Text to prompt the user for input (String)
def GetUserInput(prompt):
    # Prompt the user for valid input until they enter it.
    while True:
        # Capture user input
        string = GetLine(prompt)

        # Bounds check
        ## Do not allow empty strings
        if (len(string) == 0):
            print(c.WARNING+"Input cannot be empty."+c.ENDC)
            continue
        ## Do not allow more than 256 characters
        elif (len(string) > 256):
            print(c.WARNING+"Input bound exceeded."+c.ENDC)
            continue

        # If we get here, we have valid input
        break

    # Send the user's input back to the requesting method.
    return string

# Method: GetLine
# Purpose: Read a line from the user, allowing for cursor movement.
# Parameters:
# - prompt: Text to prompt the user for input (String)
def GetLine(prompt):
    # Backup the shell session, to restore it later.
    backup = tcgetattr(stdin)

    # Set the stage for the session.
    setraw(stdin)
    input = ""
    index = 0

    # Continue accepting input until the user aborts the process (CTRL-C)
    # or hits the enter key.
    while True:
        # Clear screen, then print current input string with prompt
        stdout.write(u"\u001b[1000D")
        stdout.write(u"\u001b[0K")
        stdout.write(prompt+" "+input)
        stdout.write(u"\u001b[1000D")
        stdout.write(u"\u001b[" + str(index+len(prompt)+1) + "C")
        stdout.flush()

        # Read a single character and get its code.
        char = ord(stdin.read(1))

        # Manage internal data-model
        if char == 3: # CTRL-C
            # Restore shell session from backup, then exit.
            tcsetattr(stdin, TCSAFLUSH, backup)
            return
        elif 32 <= char <= 126: # Normal letters
            # Insert new characters at the appropriate index.
            input = input[:index] + chr(char) +  input[index:]
            index += 1
        elif char in {10, 13}: # Enter key
            # Restore shell session from backup, then exit the loop.
            # index = 0 # Should be able to get rid of this.
            tcsetattr(stdin, TCSAFLUSH, backup)
            break
        elif char == 27: # Arrow keys
            # Accept input from arrow keys and move the cursor accordingly
            next1, next2 = ord(stdin.read(1)), ord(stdin.read(1))
            if next1 == 91:
                if next2 == 68: # Left
                    index = max(0, index - 1)
                elif next2 == 67: # Right
                    index = min(len(input), index + 1)
        elif char == 127: # Delete
            # Remove characters at the appropriate index.
            input = input[:index-1] + input[index:]
            index = max(index-1,0)
        # stdout.flush() # Should be able to get rid of this.

    # On exit, print a newline and reset the cursor left.
    stdout.write('\n')
    stdout.write(u"\u001b[1000D")

    # Cleanup
    del index, char

    # Return the string the user's input.
    return input