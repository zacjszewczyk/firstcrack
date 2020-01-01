#!/usr/local/bin/python3

## BEGIN CLI BLOCK
# Purpose: The purpose of this block is to provide an easy to use, as modular
# as possible command line interface. Simply paste in this block, then edit.

### Import modules
from sys import exit, argv, stdout, stdin # Command line interface
from tty import setraw, setcbreak # Raw input
from termios import tcgetattr, tcsetattr, TCSAFLUSH # Backup/resume shell
from os.path import exists # Reading input files
from os import popen # Detect terminal size
from re import sub # Change menu to try to avoid text wrapping

# Class: c(olors)
# Purpose: provide easy access to ANSI escape codes for styling output
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
    if (len(argv) == 1):
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
    menu = """
    * To search all articles:                        %s-S%s
    * To revert post timestamps:                     %s-r%s
    * To clear all structure files:                  %s-R%s
    * To display this menu:                          %s-h%s
    * To exit this mode and build the site:          %sexit%s
    * To exit this mode and quit the program:        %s!exit%s
    """ % (c.OKGREEN, c.ENDC, c.OKGREEN, c.ENDC, c.OKGREEN, c.ENDC, c.WARNING, c.ENDC, c.FAIL, c.ENDC, c.FAIL, c.ENDC)

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
            print('Entering "-h" at any time will display the menu below.\n%s' % (menu))
        elif ("-S" in params): # Search all articles
            # If one has not been provided, get a string to search all files for
            if (search_query == ""):
                if (len(params) == 2):
                    search_query = params[1]
                else:
                    search_query = GetUserInput("Enter search string: ")
            # Iterate over the entire ./Content dirctory
            for file in listdir("Content"):
                # Only inspect text files
                if (not ".txt" in file):
                    continue
                # Search each line of the file, case insensitively
                res = SearchFile(file, search_query)
                if (res):
                    print("\nFile: "+c.UNDERLINE+file+c.ENDC)
                    for match in res:
                        print("    %sLine %d:%s %s" % (c.BOLD, match[0], c.ENDC, match[1]))
            # Cleanup
            del res
        elif ("-r" in params): # Revert post timestamps
            print("Reverting post timestamps.")
            for files in listdir("Content"):
                if (files.endswith(".txt")):
                    Revert("Content/"+files)
        elif ("-R" in params): # Rebuild all structure files
            print("Rebuilding all structure files.")
            for files in listdir("./local/blog"):
                if (files.endswith(".html")):
                    remove("./local/blog/"+files)
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
## END CLI BLOCK

# Imports
from os import listdir, stat, remove, utime, mkdir # File/folder operations
from os.path import isdir, isfile # File/folder existence operations
from time import strptime, strftime, mktime, localtime, gmtime # mod time ops
from datetime import datetime # Recording runtime
from Markdown2 import Markdown # Markdown parser
from ModTimes import CompareMtimes # Compare file mod times
from multiprocessing import Pool # Multiprocessing
from random import choice, choices # Building Explore page
from locale import getpreferredencoding # Speed up file opens

# Global variables
## - files: Dictionary with years as the keys, and sub-dictinaries as the
##          elements. These elements have months as the keys, and a list
##          of the posts made in that month as the elements. (Dictionary)
## - content: A string with the opening and closing HTML tags. (String)
## - months: A map of month numbers to names (Dictionary)
## - md: Placeholder for instance of Markdown parser. (Class)
files = {}
content = ""
months = {"01":"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"December"}
md = ""
ENCODING = getpreferredencoding()

# Config variables, read in from './.config'
## - base_url: The base domain name for your website, i.e. https://zacs.site"). (String)
## - byline: The name of the author, as you want it to display on all blog posts. (String)
## - full_name: The full, legal name of the content owner, used to generate the copyright notice. (String)
## - meta_keywords: Any keywords you would like a search engine to use to send visitors to your website. (String)
## - meta_appname: The app name a user will see if they save your website to their home screen. (String)
## - twitter_url: The URL to your Twtitter profile. (String)
## - instagram_url: The URL to your Instagram profile. (String)
class conf():
    base_url, byline, full_name, meta_keywords, meta_appname, twitter_url, insta_url = "", "", "", "", "", "", ""

# Method: AppendContentOfXToY
# Purpose: Append the first paragraph of an original article, or
#          the entirety of a linkpost, to a target file.
# Parameters:
# - target: Target file name, including extension. (String)
# - source: Source file name, including extension. (String)
def AppendContentOfXToY(target, sources):
    target_fd = open(target+".html", "a", encoding=ENCODING)
    for source,timestamp in sources:
        # Store the name of the corresponding HTML file in a variable
        html_filename = source.lower().replace(" ", "-")[0:-3]+"html"

        # Instantiate a boolean flag variable, "flag". This indicates
        # whether to include the entire article (True) or truncate it
        # at the first paragraph (False)
        flag = True

        # Now that we know there is a structure file built, pull the data
        # from there.

        ## Open the source file
        source_fd = open("./local/blog/"+html_filename, "r", encoding=ENCODING)

        # Skip to the <article tag, then write the opening <article>
        # tag to the output file.
        for i, line in enumerate(source_fd):
            if ("<article" in line): target_fd.write("<article>"); break

        # Iterate over each line of the source structure file.
        for i, line in enumerate(source_fd):
            # Check the first two lines of the structure file for a
            # class tag denoting the type of article. If viewing an
            # original article, truncate it at the first paragraph by
            # setting the flag, "flag", to False
            if (i <= 1):
                if ('class="original"' in line):
                    flag = False
                    line = line.replace("href=\"", "href=\"blog/")
            elif (i == 3):
                line = line.replace("href=\"", "href=\"blog/")
            # Write subsequent lines to the file. If we are truncating
            # the file and we encouter the first paragraph, write it to
            # the output file and then quit.
            elif (flag == False and line[0:2] == "<p"):
                target_fd.write(line)
                break

            # Stop copying content at the end of the article.
            if ("</article>" in line):
                break

            # Write all lines from the structure file to the output file
            # by default.
            target_fd.write(line)

        source_fd.close()

        # Once we have reached the end of the content in the case of a linkpost,
        # or read the first paragraph in the case of an original article, add a
        # "read more" link and close the article.
        target_fd.write("\n    <p class='read_more_paragraph'>\n        <a style='text-decoration:none;' href='blog/%s'>&#x24E9;</a>\n    </p>" % (html_filename))
        target_fd.write("</article>")
    target_fd.close()

    # Cleanup
    del html_filename, flag, target_fd, source_fd

# Method: AppendToFeed
# Purpose: Append the content of a source file to the RSS feed.
# Parameters:
# - source: Source file name, including extension. (String)
def AppendToFeed(sources):
    ## Open the feed and source file
    feed_fd = open("./local/rss.xml", "a", encoding=ENCODING)
    for source in sources:
        if (type(source) == list):
            source = source[0]
        # Store the name of the corresponding HTML file in a variable
        html_filename = source.lower().replace(" ", "-")[0:-3]+"html"

        # Instantiate a boolean flag variable, "flag". This indicates
        # whether to include the entire article (True) or truncate it
        # at the first paragraph (False)
        flag = True

        # Now that we know there is a structure file built, pull the data
        # from there.

        ## Write the opening <item> tag
        feed_fd.write("        <item>\n")

        source_fd = open("./local/blog/"+html_filename, "r", encoding=ENCODING)
        # Skip to the <article tag, then write the opening <article>
        # tag to the output file.
        for i, line in enumerate(source_fd):
            if ("<h2" in line): break

        # Iterate over each line of the source structure file.
        for i, line in enumerate(source_fd):
            # Strip whitespace
            line = line.strip()
            line = line.replace("&", "&#38;")

            # Check the first two lines of the structure file for a
            # class tag denoting the type of article. If viewing an
            # original article, truncate it at the first paragraph by
            # setting the flag, "flag", to False
            # print(i,":",line)
            if (i == 0):
                if ("class=\"original\"" in line):
                    flag = False
                    link = conf.base_url+"/blog/"+line.split("href=\"")[1].split(" ")[0][:-1]
                else:
                    link = line.split("href=\"")[1].split(" ")[0][:-1]
                if (link[0:4] != "http"):
                    link = "http://"+link
                line = "            <title>"+line.split("\">")[1][:-4]+"</title>\n"
                line += "            <link>"+link+"</link>\n"
                line += "            <guid isPermaLink='true'>"+link+"</guid>\n"
            elif (i == 1):
                continue
            elif (i == 2):
                pubdate = gmtime(mktime(strptime(line[16:26]+" "+line.split("</a>")[-1][4:-11], "%Y-%m-%d %H:%M:%S")))
                line = "            <pubDate>"+strftime("%a, %d %b %Y %H:%M:%S", pubdate)+" GMT</pubDate>\n"
                line += "            <description>\n"
            # Write subsequent lines to the file. If we are truncating
            # the file and we encouter the first paragraph, write it to
            # the output file and then quit.
            elif (flag == False and line[0:2] == "<p"):
                feed_fd.write(""+line.replace('href="/', 'href="'+conf.base_url+'/').replace('"#fn', '"'+conf.base_url+'/blog/'+html_filename+"#fn").replace("<", "&lt;").replace(">", "&gt;"))
                break
            else:
                line = ""+line.replace("src='/", "src='"+conf.base_url+'/').replace('href="/', 'href="'+conf.base_url+'/').replace('"#fn', '"'+conf.base_url+'/blog/'+html_filename+"#fn").replace("<", "&lt;").replace(">", "&gt;")

            # Stop copying content at the end of the article.
            if ("&lt;/article&gt;" in line):
                break

            # Write all lines from the structure file to the output file
            # by default.
            feed_fd.write(line+'\n')
        source_fd.close()

        # Once we have reached the end of the content in the case of a linkpost,
        # or read the first paragraph in the case of an original article, add a
        # "read more" link and close the article.
        feed_fd.write("\n<p class='read_more_paragraph'>\n<a style='text-decoration:none;' href='%s/blog/%s'>Read more...</a>\n</p>\n".replace("<", "&lt;").replace(">", "&gt;") % (conf.base_url, html_filename))
        feed_fd.write("            </description>\n        </item>\n")
    feed_fd.close()

    # Cleanup
    del html_filename, flag, feed_fd, source_fd

# Method: BuildFromTemplate
# Purpose: Build a target file, with a specified title and body id, and
# optional fields for inserted stylesheets and content
# Parameters:
# - target: Target file name, including extension. (String)
# - title: Value used in meta title field, and <title> element. (String)
# - bodyid: ID for body element. (String)
# - description: Value used in meta description field. (String)
# - sheets: Any stylesheets to be inserted into the <head> element. (String)
# - passed_content: Body content to insert into the <body> element. (String)
def BuildFromTemplate(target, title, bodyid, description="", sheets="", passed_content=""):
    # Make global variable accessible within the method
    global content

    # Clear the target file, then write the opening HTML code and any passed content.
    open(target, "w", encoding=ENCODING).close()
    fd = open(target, "a", encoding=ENCODING)
    fd.write(content[0].replace("{{META_DESC}}", description).replace("{{ title }}", title).replace("{{ BODYID }}", bodyid, 1).replace("<!-- SHEETS -->", sheets, 1))
    fd.write(passed_content)
    fd.close()

    # Cleanup
    del fd

# Method: CloseTemplateBuild
# Purpose: Open the target file and write the closing HTML to it, with an
#          optional field for inserted scripts.
# Parameters:
# - target: Target file name, including extension. (String)
# - scripts: Any Javascript to be inserted below the <body> element. (String)
def CloseTemplateBuild(target, scripts=""):
    # Make global variable accessible within the method
    global content

    # Write the trailing HTML tags from the template to the target file.
    fd = open(target, "a", encoding=ENCODING)
    fd.write(content[1].replace("<!-- SCRIPTS BLOCK -->", scripts))
    fd.close()

    # Cleanup
    del fd

# Method: HandleYear
# Purpose: Process all the posts in a year.
# Parameters: none
def HandleYear(year):
    # Make global variables accessible in the method, and initialize method variables.
    global files, content

    # For each year in which a post was made, generate a 'year' file, that
    # contains links to each month in which a post was published.

    # Clear the 'year' file
    open("./local/blog/"+year+".html", "w", encoding=ENCODING).close()
    year_fd = open("./local/blog/"+year+".html", "a", encoding=ENCODING)
    # Write the opening HTML tags
    year_fd.write(content[2].replace("{{ title }}", "Post Archives - ").replace("{{ BODYID }}", "archives", 1))
    # Display the months listed.
    year_fd.write("<div id=\"years_index\">\n<div>%s</div>\n" % (year))
    # Sort the sub-dictionaries by keys, months, then iterate over it. For each
    # month in which a post was made, generate a 'month' file that contains all
    # posts made during that month.
    for month in sorted(files[year], reverse=True):
        # Add a link to the month, to the year file it belongs to.
        year_fd.write("<div><a href=\"%s\">%s</a></div>" % (year+"-"+month+".html", months[month]))
        # Clear the 'month' file
        open("./local/blog/"+year+"-"+month+".html", "w", encoding=ENCODING).close()
        month_fd = open("./local/blog/"+year+"-"+month+".html", "a", encoding=ENCODING)
        # Write the opening HTML tags
        month_fd.write(content[2].replace("{{ title }}", "Post Archives - ").replace("{{ BODYID }}", "archives", 1).replace("<!--BLOCK HEADER-->", "<article>\n<p>\n"+months[month]+", <a href=\""+year+".html\">"+year+"</a>\n</p>\n</article>", 1))

        # Sort the sub-dictionaries by keys, days, then iterate over it.
        for day in sorted(files[year][month], reverse=True):
            # Sort the sub-dictionaries by keys, timestamps, then iterate over it
            for timestamp in sorted(files[year][month][day], reverse=True):
                # If a structure file already exists, don't rebuild the HTML file for individual articles
                if (not isfile("./local/blog/"+files[year][month][day][timestamp].lower().replace(" ","-")[0:-3]+"html")):
                    article_title = GenPage(files[year][month][day][timestamp], "%s/%s/%s %s" % (year, month, day, timestamp))
                else:
                    if (CompareMtimes("./Content/"+files[year][month][day][timestamp], "./local/blog/"+files[year][month][day][timestamp].lower().replace(" ","-")[0:-3]+"html")):
                        article_title = GetTitle(files[year][month][day][timestamp], "%s/%s/%s %s" % (year, month, day, timestamp))
                    else:
                        # Generate each content file. "year", "month", "day", "timestamp"
                        # identify the file in the dictionary, and the passed time values
                        # designate the desired update time to set the content file.
                        article_title = GenPage(files[year][month][day][timestamp], "%s/%s/%s %s" % (year, month, day, timestamp))

                # For each article made in the month, add an entry on the appropriate
                # 'month' structure file.
                month_fd.write("<article>\n    %s<a href=\"%s\">%s</a>\n</article>\n" % (year+"/"+month+"/"+day+" "+timestamp+": ", files[year][month][day][timestamp].lower().replace(" ", "-")[0:-3]+"html", article_title.strip()))

        # Write closing HTML tags to the month file.
        month_fd.write(content[1].replace("assets/", "../assets/"))
        month_fd.close()

    # Write closing HTML tags to the year file.
    year_fd.write("</div>\n"+content[1].replace("assets/", "../assets/"))
    year_fd.close()

    # Cleanup
    del article_title, year_fd, month_fd

# Method: GenBlog
# Purpose: Generate the blog, archives, and feed.
# Parameters: none
def GenBlog():
    # Make global variables accessible in the method, and initialize method variables.
    global files

    def order_dict(dictionary):
        return {k: order_dict(v) if isinstance(v, dict) else v
                for k, v in sorted(dictionary.items(), reverse=True)}
    files = order_dict(files)

    # file_idx: Current file number. (Int)
    # rest: Files to append (List)
    file_idx = 0
    rest = []

    for year in files:
        for month in files[year]:
                for day in files[year][month]:
                    for timestamp in files[year][month][day]:
                        fname = files[year][month][day][timestamp]
                        ts = "%s/%s/%s %s" % (year, month, day, timestamp)

                        # Add the first twenty-five articles to the main blog page.
                        if (file_idx < 25):
                            AppendContentOfXToY("./local/blog", [[fname, ts]])
                            AppendToFeed([fname])
                        # Write the years in which a post was made to the header element, in a
                        # big table to facilitate easy reading.
                        elif (file_idx == 25):
                            # This block just puts three year entries in the first row, ends
                            # the row, and then puts three more year entries in the second row.
                            # This code is stored in 'buff', and then added to the archives
                            # page.
                            buff = """\n<article id="years_list">\n<div>"""
                            for x in sorted(files, reverse=True):
                                buff += "\n<a href=\"/blog/%s\">%s</a></div>\n<div>" % (x.lower()+".html", x)
                            buff += "\n</div>\n</article>"
                            archives_fd = open("./local/archives.html", "a", encoding=ENCODING)
                            archives_fd.write(buff)
                            archives_fd.close()
                            del buff

                            # Add the twenty-sixth article to the archives page.
                            AppendContentOfXToY("./local/archives", [[fname, ts]])
                            AppendToFeed([fname])

                        # Add all other articles to the list of files to append.
                        else:
                            rest.append([fname, ts])

                        # Increase the file index.
                        file_idx += 1
    # Append the list of files.
    AppendContentOfXToY("./local/archives", rest)
    AppendToFeed(rest)

    # Select three random articles for explore page
    for year in choices(list(files.keys()), k=3):
        month = choice(list(files[year]))
        day = choice(list(files[year][month]))
        timestamp = choice(list(files[year][month][day]))
        AppendContentOfXToY("./local/explore", [[files[year][month][day][timestamp], timestamp]])

    # Cleanup
    del file_idx, month, day, timestamp

# Method: GenPage
# Purpose: Given a source content file, generate a corresponding HTML structure file.
# Parameters:
# - source: Filename of the source content file. (String)
# - timestamp: Timestamp for reverting update time, format %Y/%m/%d %H:%M:%S. (String)
def GenPage(source, timestamp):
    global content

    # md.clear()
    md = Markdown(conf.base_url)

    src = "Content/"+source
    dst = "./local/blog/"+source.lower().replace(" ", "-")[0:-3]+"html"

    # Ensure source file contains header. If not, use the Migrate() method to generate it.
    source_fd = open(src, "r", encoding=ENCODING)
    line = source_fd.readline()
    if (line[0:5] != "Type:"):
        Migrate(source, timestamp)
    source_fd.close()

    # Open the source file in read mode.
    source_fd = open(src, "r", encoding=ENCODING)

    # Use the source file's name to calculate, clear, and re-open the structure file.
    target_fd = open(dst, "w", encoding=ENCODING).close()
    target_fd = open(dst, "a", encoding=ENCODING)

    # Insert Javascript code for device detection.
    local_content = content[2].replace("{{ BODYID }}", "post",1).replace("assets/", "/assets/")

    # Initialize idx to track line numbers, and title to hold the title block of each article.
    idx = 0
    title = ""

    # Iterate over each line in the source content file.
    for i, line in enumerate(source_fd):
        # In the first line, classify the article as a linkpost or an original piece.
        if (idx == 0):
            ptype = line[6:].strip()
            if (ptype == "original"):
                title += "<article>\n<h2 style=\"text-align:center;\">\n<a href=\"{{URL}}\" class=\"%s\">{{URL_TITLE}}</a>" % (ptype)
            else:
                title += "<article>\n<h2 style=\"text-align:center;\">\n<a href=\"{{URL}}\" class=\"%s\">{{URL_TITLE}}</a>" % (ptype)
        # In the second line of the file, add the article title.
        elif (idx == 1):
            article_title = line[7:].strip()
            title = title.replace("{{URL_TITLE}}", article_title)
            local_content = local_content.replace("{{ title }}", line[7:].strip()+" - ")
        # In the third line of the file, add the article URL to the title/link.
        elif (idx == 2):
            line = line[6:].strip()
            if (line[0:4] != "http" and ("htm" == line[-3:])):
                line = line.replace(".htm", ".html").replace(" ", "-").lower()
            title = title.replace("{{URL}}", line)+"\n                    </h2>"
        # In the fourth line of the file, read the pubdate, and add it to the article.
        elif (idx == 3):
            # print(line)
            line = line[9:].strip().replace(" ", "/").split("/")
            title += """\n<time datetime="%s-%s-%s" pubdate="pubdate">By <link rel="author">%s</link> on <a href="%s">%s</a>/<a href="%s">%s</a>/%s %s EST</time>""" % (line[0], line[1], line[2], conf.byline, line[0]+".html", line[0], line[0]+"-"+line[1]+".html", line[1], line[2], line[3])
        # In the fifth line of the file, we're reading the author line. Since we don't do anything
        # with this, pass.
        elif (idx == 4):
            pass
        # Blank line between header and content
        elif (idx == 5):
            pass
        # First paragraph. Write the opening tags to the target, then the file's content as
        # generated up to this point. Then write the first paragraph, parsed.
        elif (idx == 6):
            target_fd.write(local_content.replace("{{META_DESC}}", line.replace('"', "&#34;").strip()).strip())
            target_fd.write("\n"+title.strip())
            target_fd.write("\n"+md.html(line).strip())
        # For successive lines of the file, parse them as Markdown and write them to the file.
        elif (idx > 5):
            # print(src)
            target_fd.write("\n"+md.html(line).rstrip('\n'))

        # Increase the line number
        idx += 1
    else:
        # At the end of the file, write closing HTML tags.
        target_fd.write("\n"+md.html("{EOF}"))
        target_fd.write("\n</div>\n                </article>")
        target_fd.write(content[1].replace("assets/", "../assets/").replace("<!-- SCRIPTS BLOCK -->", """""",1))

    # Close file descriptors.
    target_fd.close()
    source_fd.close()

    mtime = stat("./Content/"+source).st_mtime
    utime(dst, (mtime, mtime))

    # Cleanup
    del src, dst, source_fd, idx, title, target_fd, mtime, local_content, ptype, md

    return article_title

# Method: GetTitle
# Purpose: Return the article title of a source file.
# Parameters:
# - source: Source file name, including extension. (String)
def GetTitle(source, timestamp):
    src = "Content/"+source

    # Ensure source file contains header. If not, use the Migrate() method to generate it.
    source_fd = open(src, "r", encoding=ENCODING)
    line = source_fd.readline()
    if (line[0:5] != "Type:"):
        source_fd.close()
        Migrate(source, timestamp)

    # Open the source file in read mode.
    source_fd = open(src, "r", encoding=ENCODING)
    source_fd.readline()
    title = source_fd.readline()[7:]
    source_fd.close()

    # Cleanup
    del src, source_fd, line

    return title

# Method: Init
# Purpose: Instantiate the global variable 'content', to reduce duplicate I/O
#          operations. Then clear the blog and archive structure files, and
#          the RSS feed, and write the opening tags. Generate file dictionary.
#          Make sure ./local exists.
# Parameters: none
def Init():
    # Check for the existence of a ".config" file, which contains config info.
    # On error, notify the user, create the file, and prompt the user to fill it out.
    if (not isfile("./.config")):
        stdout.write(c.FAIL+"The FirstCrack config file, './.config', does not exist. Would you like to create it now?\n"+c.ENDC)
        res = GetUserInput("(y/n) # ")

        while (res != "y" and res != "n"):
            stdout.write(c.FAIL+"Invalid input. Please try again.\n"+c.ENDC)
            res = GetUserInput("(y/n) # ")

        if (res == "y"):
            print(c.UNDERLINE+"Base URL"+c.ENDC+": The base domain for your website, i.e. https://zacs.site")
            print(c.UNDERLINE+"Byline"+c.ENDC+": The name of the author, as you want it to display on all blog posts.")
            print(c.UNDERLINE+"Full name"+c.ENDC+": The full, legal name of the content owner, for the copyright notice.")
            print(c.UNDERLINE+"Keywords"+c.ENDC+": Key words that describe your website.")
            print(c.UNDERLINE+"App name"+c.ENDC+": The name users will see if they put your site on their home screen.")
            print(c.UNDERLINE+"Twitter URL"+c.ENDC+": The URL to your Twtitter profile.")
            print(c.UNDERLINE+"Instagram URL"+c.ENDC+": The URL to your Instagram profile.")
            print()

            conf.base_url = GetUserInput("Base URL: ").rstrip("/")
            conf.byline = GetUserInput("Byline: ")
            conf.full_name = GetUserInput("Full name: ")
            conf.meta_keywords = GetUserInput("Keywords: ")
            conf.meta_appname = GetUserInput("App name: ")
            conf.twitter_url = GetUserInput("Twitter URL: ")
            conf.insta_url = GetUserInput("Instagram URL: ")
            fd = open("./.config", "w", encoding=ENCODING)
            fd.write("# FirstCrack configuration document\n# The following variables are required:\n## base_url - The base URL for your website, i.e. https://zacs.site\n## byline - The name of the author, as it will display on all posts\n## full_name - The full, legal name of the content owner.\n## meta_keywords - Any additional keywords you would like to include in the META keywords tag\n## meta_appname - The desired app name, stored in a META tag\n## twitter - URL to your Twtitter profile\n## instagram - URL to your Instagram profile\nbase_url = %s\nbyline = %s\nfull_name = %s\nmeta_keywords = %s\nmeta_appname = %s\ntwitter = %s\ninstagram = %s" % (conf.base_url, conf.byline, conf.full_name, conf.meta_keywords, conf.meta_appname, conf.twitter_url, conf.insta_url))
            fd.close()
        else:
            print(c.FAIL+"Configuration file not created."+c.ENDC)
            print(c.WARNING+"Please run again."+c.ENDC)
            exit(0)

        # Cleanup
        del res

        # Remove the migration script.
        if (isfile("./.sys.sh")):
            remove("./.sys.sh")

    # On success, extract values and store them for use when building the site.
    else:
        # Open the './.config' file
        fd = open("./.config", "r", encoding=ENCODING)
        for i, line in enumerate(fd):
            if (i == 9): # Extract base URL for site
                conf.base_url = line.split(" = ")[1].strip()
            elif (i == 10): # Extract author byline
                conf.byline = line.split(" = ")[1].strip()
            elif (i == 11): # Extract author full (legal) name
                conf.full_name = line.split(" = ")[1].strip()
            elif (i == 12): # Extract additional site keywords
                conf.meta_keywords = line.split(" = ")[1].strip()
            elif (i == 13): # Extract app name
                conf.meta_appname = line.split(" = ")[1].strip()
            elif (i == 14): # Extract Twitter profile URL
                conf.twitter_url = line.split(" = ")[1].strip()
            elif (i == 15): # Extract Instagram profile URL
                conf.insta_url = line.split(" = ")[1].strip()
        fd.close()

        # Cleanup
        del fd

    # If any of these values were blank, notify the user and throw an error.
    if (conf.base_url == "" or conf.byline == "" or conf.full_name == ""):
        print(c.FAIL+"Error reading settings from './.config'. Please check file configuration and try again."+c.ENDC)
        exit(0)
    elif (conf.meta_keywords == "" or conf.meta_appname == "" or conf.twitter_url == "" or conf.insta_url == ""):
        print(c.WARNING+"You have not finished initializing the configuration file. Please finish setting up './.config'.")

    # Check for existence of system files and Content directory.
    # These are requirements for First Crack; it will fail if they do not exist.
    ## Check for the existence of the "./system" directory first...
    if (not isdir("./system")):
        print(c.FAIL+"\"./system\" directory does not exist. Exiting."+c.ENDC)
        exit(0)
    ## ...then for the existence of the Content directory
    if (not isdir("./Content")):
        print(c.FAIL+"\"./Content\" directory does not exist. Exiting."+c.ENDC)
        exit(0)

    ## Now ensure crucial system files exist
    for f in ["template.htm", "index.html", "projects.html", "disclaimers.html"]:
        if (not isfile("./system/"+f)):
            print(c.FAIL+"\"./system/"+f+"\" does not exist. Exiting."+c.ENDC)
            exit(1)

    # Make sure ./local exists with its subfolders
    if (not isdir("./local")):
        mkdir("./local")
    if (not isdir("./local/blog")):
        mkdir("./local/blog")
    if (not isdir("./local/assets")):
        mkdir("./local/assets")

    # Make global variables accessible in the method, and initialize method variables.
    global files, content, md
    files = {}

    # Open the template file, split it, modify portions as necessary, and store each half in a list.
    fd = open("system/template.htm", "r", encoding=ENCODING)
    content = fd.read()
    content = content.split("<!--Divider-->")
    # This line replaces all generics in the template file with values in config file
    content[0] = content[0].replace("{{META_KEYWORDS}}", conf.meta_keywords).replace("{{META_APPNAME}}", conf.meta_appname).replace("{{META_BYLINE}}", conf.byline).replace("{{META_BASEURL}}", conf.base_url)
    # This line replaces placeholders with social media URLs in the config file
    content[1] = content[1].replace("{{META_BYLINE}}", conf.full_name).replace("{{TWITTER_URL}}", conf.twitter_url).replace("{{INSTA_URL}}", conf.insta_url)
    content.append(content[0].replace("index.html", "../index.html", 1).replace("blog.html", "../blog.html", 1).replace("explore.html", "../explore.html", 1).replace("archives.html", "../archives.html", 1).replace("projects.html", "../projects.html", 1))
    fd.close()

    # Clear and initialize the archives.html and blog.html files.
    BuildFromTemplate(target="./local/archives.html", title="Post Archives - ", bodyid="postarchives", description="DESCRIPTION HERE", sheets="", passed_content="")
    BuildFromTemplate(target="./local/blog.html", title="Blog - ", bodyid="blog", description="DESCRIPTION HERE", sheets="", passed_content="")

    # Clear and initialize the RSS feed
    fd = open("./local/rss.xml", "w", encoding=ENCODING)
    fd.write("""<?xml version='1.0' encoding='ISO-8859-1' ?>\n<rss version="2.0" xmlns:sy="http://purl.org/rss/1.0/modules/syndication/" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n    <title>%s</title>\n    <link>%s</link>\n    <description>RSS feed for %s's website, found at %s/</description>\n    <language>en-us</language>\n    <copyright>Copyright 2012, %s. All rights reserved.</copyright>\n    <atom:link href="%s/rss.xml" rel="self" type="application/rss+xml" />\n    <lastBuildDate>%s GMT</lastBuildDate>\n    <ttl>5</ttl>\n    <generator>First Crack</generator>\n""" % (conf.byline, conf.base_url, conf.byline, conf.base_url, conf.byline, conf.base_url, datetime.utcnow().strftime("%a, %d %b %Y %I:%M:%S")))
    fd.close()

    # Generate a dictionary with years as the keys, and sub-dictinaries as the elements.
    # These elements have months as the keys, and a list of the posts made in that month
    # as the elements.
    for each in listdir("Content"):
        if (".txt" in each):
            mtime = strftime("%Y/%m/%d/%H:%M:%S", localtime(stat("Content/"+each).st_mtime)).split("/")
            if (mtime[0] not in files):
                files[mtime[0]] = {}
            if (mtime[1] not in files[mtime[0]]):
                files[mtime[0]][mtime[1]] = {}
            if (mtime[2] not in files[mtime[0]][mtime[1]]):
                files[mtime[0]][mtime[1]][mtime[2]] = {}
            if (mtime[3] not in files[mtime[0]][mtime[1]][mtime[2]]):
                files[mtime[0]][mtime[1]][mtime[2]][mtime[3]] = {}
            files[mtime[0]][mtime[1]][mtime[2]][mtime[3]] = each

    # Cleanup
    del fd

# Method: Migrate
# Purpose: For files without the header information in their first five lines, generate
#          that information, insert it into the file, and revert the update time.
# Parameters
# - target: Target file name, including extension. (String)
# - mod_time: Timestamp for reverting update time, format %Y/%m/%d %H:%M:%S. (String)
def Migrate(target, mod_time):
    # Open the target file and read the first line.
    fd = open("Content/"+target, "r", encoding=ENCODING)
    article_content = fd.readline()

    # Detect a linkpost or an original article, and parse the information appropriately.
    if (article_content[0:3] == "# ["):
        article_type = "linkpost"
        article_content = article_content[2:].replace(") #", "")
        article_content = article_content.split("]")
        article_title = article_content[0][1:]
        article_url = article_content[1][1:-1]
    else:
        article_type = "original"
        article_title = article_content
        article_url = target.replace(".txt", ".html").replace(" ", "-").replace("'","").lower()
        article_content = fd.readline()

    # Read the rest of the article's content from the file.
    article_content = fd.read()
    fd.close()

    # Clear the target file, then write it's contents into it after the header information.
    fd = open("Content/"+target, "w", encoding=ENCODING)
    fd.write("""Type: %s\nTitle: %s\nLink: %s\nPubdate: %s\nAuthor: %s\n\n%s""" % (article_type, article_title.strip(), article_url.strip(), mod_time, conf.byline, article_content.strip()))
    fd.close()

    # Cleanup
    del fd, article_content, article_title, article_url

    # Revert the update time for the target file, to its previous value.
    utime("Content/"+target, ((mktime(strptime(mod_time, "%Y/%m/%d %H:%M:%S"))), (mktime(strptime(mod_time, "%Y/%m/%d %H:%M:%S")))))

    # Return the read article type, for debugging.
    return article_type

# Method: Revert
# Purpose: Check file timestamp against article timestamp. Correct if necessary.
# Parameters:
# - tgt: Target file name (String)
def Revert(tgt):
    fd = open(tgt, "r", encoding=ENCODING)
    fd.readline()
    fd.readline()
    fd.readline()
    mod_time = mktime(strptime(fd.readline()[9:].strip(), "%Y/%m/%d %H:%M:%S"))
    fd.close()

    if (mod_time != stat(tgt).st_mtime):
        print("Does not match for",tgt)
        print("Reverting to",mod_time)
        utime(tgt, (mod_time, mod_time))

    # Cleanup
    del fd, mod_time

# Method: SearchFile
# Purpose: Search for a string within a file.
# Parameters:
# - tgt: Target file name (String)
# - q: String to search for (String)
def SearchFile(tgt, q):
    ret = []
    fd = open("Content/"+tgt, encoding=ENCODING)
    idx = 0
    for i, line in enumerate(fd):
        if (q.lower() in line.lower()):
            ret.append([idx, line.strip()])
        idx += 1
    fd.close()
    if (len(ret) == 0):
        return False
    return ret

# If run as an individual file, generate the site and report runtime.
# If imported, only make methods available to imported program.
if __name__ == '__main__':
    ActivateInterface()

    t1 = datetime.now()
    Init()
    
    # Purpose: Create static structure files.
    ## Reference the index.html source file to generate the front-end structure file.
    fd = open("system/index.html", "r", encoding=ENCODING)
    home = fd.read().split("<!-- DIVIDER -->")
    fd.close()
    BuildFromTemplate(target="./local/index.html", title="", bodyid="home", description="DESCRIPTION HERE", sheets=home[0], passed_content=home[1])
    del home
    ## Reference the projects.html source file to generate the front-end structure file.
    fd = open("system/projects.html", "r", encoding=ENCODING)
    projects = fd.read().split("<!-- DIVIDER -->")
    fd.close()
    BuildFromTemplate(target="./local/projects.html", title="Projects - ", bodyid="projects", description="DESCRIPTION HERE", sheets="", passed_content=projects[1])
    del projects
    ## Reference the disclaimers.html source file to generate the front-end structure file.
    fd = open("system/disclaimers.html", "r", encoding=ENCODING)
    disclaimers = fd.read().split("<!-- DIVIDER -->")
    fd.close()
    BuildFromTemplate(target="./local/disclaimers.html", title="Disclaimers - ", bodyid="disclaimers", description="DESCRIPTION HERE", sheets="", passed_content=disclaimers[1].replace("{{NAME}}", conf.full_name))
    del disclaimers
    ## Build the 404.html file.
    BuildFromTemplate(target="./local/404.html", title="Error - ", bodyid="error", description="DESCRIPTION HERE", sheets="", passed_content="")
    ## Explore file
    BuildFromTemplate("./local/explore.html", "Explore -", "explore", description="DESCRIPTION HERE", sheets="", passed_content="")
    # Add intro paragraph to explore page
    fd = open("./local/explore.html", "a", encoding=ENCODING)
    fd.write("<article>\n<p>\nEvery time I update this site, new articles appear here. This helps unearth old, unpopular posts that&#160;&#8212;&#160;left alone&#160;&#8212;&#160;no one would ever read again.\n</p>\n</article>")
    fd.close()
    
    # Use multithreading to speed up processing each year's posts
    with Pool() as pool:
        pool.map(HandleYear, files, 1)

    # Build the blog and archives pages, and the feed
    GenBlog()

    # Write closing tags to all template files
    CloseTemplateBuild("./local/index.html")
    CloseTemplateBuild("./local/projects.html")
    CloseTemplateBuild("./local/disclaimers.html")
    CloseTemplateBuild("./local/404.html", """<script type="text/javascript">document.getElementById("content_section").innerHTML = "<article><h2 style='text-align:center;'>Error: 404 Not Found</h2><p>The requested resource at <span style='text-decoration:underline;'>"+window.location.href+"</span> could not be found.</p></article>"</script>""")
    CloseTemplateBuild("./local/explore.html")
    CloseTemplateBuild("./local/archives.html")
    CloseTemplateBuild("./local/blog.html")

    # Write closing tags to the RSS feed.
    fd = open("./local/rss.xml", "a", encoding=ENCODING)
    fd.write("""\n</channel>\n</rss>""")
    fd.close()

    # import cProfile
    # cProfile.run("Init()", "./init.cprof")
    # cProfile.run("GenStatic()", "./init.cprof")
    # cProfile.run("GenSite()", "./init.cprof")

    t2 = datetime.now()

    print(("Execution time: "+c.OKGREEN+str(t2-t1)+"s"+c.ENDC))

    # Cleanup
    del t1, t2, pool, fd
