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
from os.path import isfile # Web server
from time import localtime # Timestamping logs

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
    # If the user just runs the file, or only includes "-v" verbose flag, notify
    # them that "-a" enters command line interface, then build the site.
    if (len(argv) == 1 or len(argv) == 2 and "-v" in argv):
        print(c.UNDERLINE+"Note"+c.ENDC+": You can use '-a' to enter 'Authoring Mode'")
    # If they have run the program with up to 2 parameters other than "-v",
    # open the command line interface.
    elif (len(argv) < 4):
        DisplayInterface(argv[1:])
    else: # Too many parameters
        print(c.FAIL+"Too many parameters"+c.ENDC)
        exit(0)

# Method: DisplayInterface
# Purpose: Provide a command line interface for the script, for more granular control
# of its operation.
# Parameters: params: command line parameters (String)
def DisplayInterface(params):
    # Store the menu in a variable so as to provide easy access at any point in time.
    menu = f"""
    * To clear all structure files:                    {c.OKGREEN}-R{c.ENDC}
    * To revert post timestamps:                       {c.OKGREEN}-r{c.ENDC}
    * To display this menu:                            {c.WARNING}-h{c.ENDC}
    
    * To host local web server to preview local site:  {c.WARNING}-p{c.ENDC}
    * To host public web server to preview local site: {c.WARNING}-P{c.ENDC}

    * To exit this mode and build the site:            {c.FAIL}exit{c.ENDC}
    * To exit this mode and quit the program:          {c.FAIL}!exit{c.ENDC}
    """

    # If the terminal window is less than 59 characters wide, resize the menu
    # to better fit.
    rows, columns = popen('stty size', 'r').read().split()
    if (int(columns) < 59):
        menu = sub(":\s+", ":\n        ", menu)

    # Continue prompting the user for input until they enter a valid argument
    while (True):
        if ("-a" in params): # Entered CLI. Prompt for command.
            print(menu)
            params = GetUserInput("#: ")
        if ("-R" in params): # Rebuild all structure files
            print(" - Clearing structure files... ", end="", flush=True)
            for file in listdir("./html/blog"):
                if (file.endswith(".html")):
                    remove("./html/blog/"+file)
            print(f"{c.OKGREEN}done.{c.ENDC}")
            break
        elif ("-r" in params): # Revert post timestamps
            print(" - Reverting post timestamps... ", end="", flush=True)
            for files in listdir("./content"):
                if (files.endswith(".txt")):
                    Revert("./content/"+files)
            print(f"{c.OKGREEN}done.{c.ENDC}")
        elif ("-h" in params or "help" in params): # Print help menu
            print(f'Entering "-h" at any time will display the menu below.\n{menu}')
        elif ("-p" in params or "-P" in params): # Web server
            from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
            
            # Clear log file
            open("./server.log", "w").close()

            # Setup the request handler
            class GetHandler(BaseHTTPRequestHandler):
                def do_GET(self): # Handle GET requests
                    # Transform request for root to request for index.html
                    if (self.path == "/"):
                        self.path = "/index.html"
                    
                    # Strip leading / from request
                    resource = self.path[1:]
                    
                    # Test for file existence
                    if (isfile(f"./html/{resource}")):
                        # If file exists, send 200 code and appropriate content
                        # header based on file type.
                        self.send_response(200)
                        extension = resource.rsplit(".", 1)[-1]
                        if (extension == "css"):
                            self.send_header('Content-Type','text/css; charset=utf-8')
                        elif (extension == "html"):
                            self.send_header('Content-Type','text/html; charset=utf-8')
                        elif (extension == "xml"):
                            self.send_header('Content-Type','text/xml; charset=utf-8')
                        elif (extension == "jpg"):
                            self.send_header('Content-Type','image/jpg')
                        elif (extension == "ico"):
                            self.send_header('Content-Type','image/ico')
                        else:
                            self.send_header('Content-Type','text/plain; charset=utf-8')
                        self.end_headers()

                        # Serve file
                        fd = open(f"./html/{resource}", "rb")
                        for i,line in enumerate(fd):
                            self.wfile.write(line)
                        fd.close()
                    # If file does not exist, send 404 code and serve 404 page.
                    else:
                        self.send_response(404)
                        self.send_header('Content-Type','text/html; charset=utf-8')
                        self.end_headers()
                        fd = open(f"./html/404.html", "rb")
                        for i,line in enumerate(fd):
                            self.wfile.write(line)
                        fd.close()

                # Send no response if client uses one of these valid but 
                # unsupported HTTP methods.
                def do_HEAD(self):
                    return False
                def do_POST(self):
                    return False
                def do_PUT(self):
                    return False
                def do_DELETE(self):
                    return False
                def do_CONNECT(self):
                    return False
                def do_OPTIONS(self):
                    return False
                def do_TRACE(self):
                    return False
                def do_PATCH(self):
                    return False

                def log_request(self, code):
                    server_fd = open("./server.log", "a")
                    server_fd.write(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {self.requestline} {code} -\n")
                    server_fd.close()
                    print(f"{self.client_address[0]} - - [{self.log_date_time_string()}] {self.requestline} {code} -")

            # Make web server public or private, and notify user
            if ("-p" in params):
                server_address = ("127.0.0.1", 8000)
                print(f"Serving {c.OKGREEN}private{c.ENDC} web server at port {c.OKGREEN}8000{c.ENDC}. Use {c.BOLD}CTRL-C{c.ENDC} to exit.")
            else:
                server_address = ("0.0.0.0", 8000)
                print(f"Serving {c.WARNING}public{c.ENDC} web server at port {c.OKGREEN}8000{c.ENDC}. Use {c.BOLD}CTRL-C{c.ENDC} to exit.")
            # Serve web server forever
            httpd = ThreadingHTTPServer(server_address, GetHandler)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print(f"\r{c.OKGREEN}Exiting.{c.ENDC}")
                server_fd = open("./server.log", "a")
                server_fd.write(f"- - - [{localtime().tm_mday}/{localtime().tm_mon}/{localtime().tm_year} {localtime().tm_hour}:{localtime().tm_min}:{localtime().tm_sec}] Graceful shutdown - -\n")
                server_fd.close()
                httpd.shutdown()
                exit(0)

        elif ("!exit" in params): # Exit without building site
            exit(0)
        else: # Exit then build site
            break

        # Unless "--exit" flag is supplied, prompt user for more input.
        if ("--exit" in params):
            exit(0)
        params = GetUserInput("#: ")

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