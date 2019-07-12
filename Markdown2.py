#!/usr/local/bin/python3

# Footnotes

# Import methods
from re import findall # re.findall, for links
from os.path import isfile

class Markdown:
    # Method: __init__
    # Purpose: Accept base URL for relative links
    # Parameters:
    # - self: Class namespace
    # - __base_url: Base URL for relative links. (String)
    # Return: none
    def __init__(self, base_url=""):
        self.__base_url = base_url

    # Initialize variables
    __base_url = "" # Base URL, given for relative links
    __line_tracker = ["", "", ""] # Last three lines, raw.
    __line_type_tracker = ["", "", ""] # Type of last three lines.
    __line_indent_tracker = [0, 0, 0] # Indent level of last three lines.
    __close_out = [] # List of block-level elements that still need closed out.
    __pre = False # Yes/no, is the parser in a <pre> tag?

    # Method: __parseInlineMD
    # Purpose: Turn all inline Markdown tags into HTML.
    # Parameters:
    # - self: Class namespace
    # - __line: Input line to process, mangled (String)
    # Return:
    # - Parsed line. (String)
    def __parseInlineMD(self, __line):
        # Add a <br /> if three or more trailing spaces.
        if ((len(__line) - len(__line.rstrip(' '))) > 2):
            __line = __line.strip() + "<br />"
        
        # Parser tracks leading whitespace, so remove it.
        __line = __line.strip()

        # If the remaining line length is 0, return blank line.
        if (len(__line) == 0):
            return ""
        
        # Parse  emdashes
        __line = __line.replace("--", "&#160;&#8212;&#160;")

        ## Prase **, or <strong>, tags first, to keep them from being
        ## interpreted as <em> tags...
        while ("**" in __line):
            __line = __line.replace("**", "<strong>", 1).replace("**", "</strong>", 1)

        # Performance test to this point

        ## ... then parse the remaining <em> tags. Make sure there is an even
        # number of * to parse as <em> ... </em>.
        if (__line.count("*") != 1):
            while ("*" in __line):
                __line = __line.replace("*", "<em>", 1).replace("*", "</em>", 1)

        ## Parse inline code with <code> ... </code> tags.
        while ("`" in __line):
            __line = __line.replace("`", "<code>", 1).replace("`", "</code>", 1)

        ## Parse aposrophes.
        for each in findall("\w'\w", __line):
            __line = __line.replace(each, each.replace("'", "&#8217;"))
        
        ## Parse single quotatin marks.
        for each in findall("\'[^\']+\'", __line):
            __line = __line.replace(each, each.replace("'", "&#8216;", 1).replace("'", "&#8217;", 1))

        ## Catch apostrophes without the trailing conjugation
        __line = __line.replace("'", "&#8217;")

        ## Parse double quotation marks.
        for each in findall("\"[^\"]+\"", __line):
            __line = __line.replace(each, each.replace('"', "&#8220;", 1).replace('"', "&#8221;", 1))
        if (__line[0] == '"'):
            __line = __line.replace('"', "&#8220;", 1)
        if (__line[-1] == '"'):
            __line = __line[0:-1]+"&#8221;"

        ## Parse links.
        for each in findall("\[([^\]]+)\]\(([^\)]*)\)", __line):
            title = each[0]
            url = each[1]

            if (len(url) == 0):
                url = title.replace("<em>", "").replace("</em>", "")+".txt"
            if (url[-4:] == ".txt"):
                url = self.__base_url+"blog/"+url.lower().replace("&#8217;", "").replace(" ", "-").replace(".txt", ".html")

            __line = __line.replace("["+each[0]+"]("+each[1]+")", "<a href=\""+url+"\">"+title+"</a>")

        # Parse footnotes
        for each in findall("(\[\^[0-9]+\])", __line):
            mark = each[2:-1]
            url = """<sup id="fnref"""+mark+""""><a href="#fn"""+mark+"""" rel="footnote">"""+mark+"""</a></sup>"""
            __line = __line.replace(each, url)

        return __line

    # Method: __trimTracker
    # Purpose: Keep tracker lists to a max of three elements.
    # Parameters:
    # - self: Class namespace
    # - __trkr: Reference to tracker to be trimmed.
    # Return: None.
    def __trimTracker(self, __trkr):
        if (len(__trkr) > 3):
            __trkr.pop(0)

    # Method: __updateLineTracker
    # Purpose: Keep track of raw lines.
    # Parameters:
    # - self: Class namespace
    # - __line: Raw Markdown line, mangled.
    # Return: None.
    def __updateLineTracker(self, __line):
        self.__line_tracker.append(__line)
        self.__trimTracker(self.__line_tracker)

    # Method: __updateLineTypeTracker
    # Purpose: Determine type of line, and whether it is part of a larger
    # block-level element, and annotate that in the line type tracker.
    # Parameters:
    # - self: Class namespace
    # - __line: Input line to process, mangled. (String)
    # Return: None.
    def __updateLineTypeTracker(self, __line):
        # Parser tracks leading whitespace, so remove it.
        __line = __line.lstrip(' ')

        if (len(__line.strip()) == 0): # Blank line.
            self.__line_type_tracker.append("blank")
        elif (__line[0] == "<" and (__line[0:4] != "<pre" and __line[0:5] != "</pre")): # Raw HTML
            self.__line_type_tracker.append("raw")
        elif (__line[0] == "#"): # Header.
            self.__line_type_tracker.append("header")
        elif (__line[0:4] == "---" or __line[0:7] == "* * *"): # Horizontal rule.
            self.__line_type_tracker.append("hr")
        elif (__line[0:2] == "!["): # Image.
            self.__line_type_tracker.append("img")
        elif (__line[0] == "{" and self.__pre == False): # Post index, with remote content.
            self.__line_type_tracker.append("idx")
        # Unordered list, as evidenced by a line starting with *, +, or -
        elif (__line[0] in ['*', '+', '-'] and __line[1] == ' '):
            # If the line is indented from the previous one, start a new list
            if (self.__line_indent_tracker[-1] > self.__line_indent_tracker[-2]):
                self.__line_type_tracker.append("ul")
            # If a line is un-indented from the previous one, close out a list.
            elif (self.__line_indent_tracker[-1] < self.__line_indent_tracker[-2]):
                self.__line_type_tracker.append("/ul")
            # If the parser finds a list element preceeded by another list
            # element or an opening list tag, treat this line as a list element
            elif (self.__line_type_tracker[-1] == "ul" or self.__line_type_tracker[-1] == "li"):
                self.__line_type_tracker.append("li")
            # If the line is for an unordered list and there is still an active
            # list, treat it as a list element.
            elif (len(self.__close_out) != 0):
                self.__line_type_tracker.append("li")
            # Otherwise, treat the line as the first in a new list.
            else:
                self.__line_type_tracker.append("ul")
        # Ordered list, as evidenced by [0-9]\. or [0-9]{2}\.
        elif (__line[0].isdigit() and __line[1] == ".") or (__line[0:2].isdigit() and __line[3] == "."):
            # If the line is indented from the previous one, start a new list
            if (self.__line_indent_tracker[-1] > self.__line_indent_tracker[-2]):
                self.__line_type_tracker.append("ol")
            # If a line is un-indented from the previous one, close out a list.
            elif (self.__line_indent_tracker[-1] < self.__line_indent_tracker[-2]):
                self.__line_type_tracker.append("/ol")
            # If the parser finds a list element preceeded by another list
            # element or an opening list tag, treat this line as a list element
            elif (self.__line_type_tracker[-1] == "ol" or self.__line_type_tracker[-1] == "li"):
                self.__line_type_tracker.append("li")
            # If the line is for an unordered list and there is still an active
            # list, treat it as a list element.
            elif (self.__line_type_tracker[-1] == "/ol" and len(self.__close_out) != 0):
                self.__line_type_tracker.append("li")
            # Otherwise, treat the line as the first in a new list.
            else:
                self.__line_type_tracker.append("ol")
        elif (__line[0] == ">"): # Blockquote
            # If the line is preceeded by a blockquote tag or the parser
            # is already in a blockquote, continue parsing the existing
            # blockquote
            if (self.__line_type_tracker[-1] == "blockquote" or self.__line_type_tracker[-1] == "bqt"):
                self.__line_type_tracker.append("bqt")
            # Otherwise, treat this line as the opening of a new blockquote
            else:
                self.__line_type_tracker.append("blockquote")
        elif (__line[0:4] == "```" or __line[0:4] == "<pre" or __line[0:5] == "</pre"): # Preformatted code block
            self.__line_type_tracker.append("pre")
            # Toggle the boolean for tracking if the parser is in a code block
            self.__pre = not self.__pre
        elif (__line[0:2] == "[>"): # Footnote
            self.__line_type_tracker.append("fn")
        else: # Default to handling the line as a paragraph
            self.__line_type_tracker.append("p")

        # Trim the tracker to a max of 3 elements.
        self.__trimTracker(self.__line_type_tracker)

    # Method: __updateIndentTracker
    # Purpose: Keep track of the indentation level.
    # Parameters:
    # - self: Class namespace
    # - __line: Input line to process, mangled. (String)
    # Return: None
    def __updateIndentTracker(self, __line):
        if (__line.strip() == ""):
            self.__line_indent_tracker.append(0)
        # Count leading spaces, and append to the line tracker list
        else:
            self.__line_indent_tracker.append(len(__line) - len(__line.lstrip(' ')))
        self.__trimTracker(self.__line_indent_tracker)

    # Method: __closeOut
    # Purpose: Write closing HTML tags for any open block-level elements.
    # Parameters:
    # - self: Class namespace
    # Return:
    # - String with each closing HTML tag on its own line. (String)
    def __closeOut(self):
        return '\n'.join(self.__close_out)

    # Method: __escapeCharacters
    # Purpose: Escape &, *, <, and > characters in the text before they are
    # processed as Markdown tags.
    # Parameters:
    # - self: Class namespace
    # - __line: Input line, mangled. (String)
    # Return:
    # - Line with &, *, <, and > escaped using their HTML entities. (String)
    def __escapeCharacters(self, __line):
        # Escape ampersands. Replace them with the appropriate HTML entity.
        __line = __line.replace("&", "&#38;")

        for each in findall("`[^`\n]+`", __line):
            __line = __line.replace(each, each.replace("*", "&#42;"))

        # Escape backtick quotes
        __line = __line.replace("\`", "&#8245;")

        # Escape escaped asteriscs, to keep them from being read as bold or
        # italic text.
        __line = __line.replace("\*", "&#42;")

        ## Escape < and > signs
        __line = __line.replace("<", "&lt;").replace(">", "&gt;")

        return __line

    # Method: html
    # Purpose:
    # - 1. Update the trackers with new lines to continue building the HTML
    #      document, and
    # - 2. Ingest raw Markdown line, process it, and return valid HTML.
    # Parameters:
    # - self: Class namespace
    # - __line: Input line, mangled. (String)
    # Return:
    # - Line formatted with HTML. (String)
    def html(self, __line):
        # Remove trailing newline
        __line = __line.rstrip('\n')

        # Update trackers
        self.__updateIndentTracker(__line)
        self.__updateLineTracker(__line)
        self.__updateLineTypeTracker(__line)

        # Print statements, for debugging.
        # print(self.__line_tracker)
        # print(self.__line_type_tracker)
        # print(self.__line_indent_tracker)
        # print()

        # Handle preformatted code blocks. First write the opening <pre> tag,
        # then return the unprocessed line.
        if (self.__line_type_tracker[-1] == "pre"):
            if (self.__pre == True):
                return "<pre>"
                # return "<pre>\n"+__line
            return "</pre>"
        
        if (self.__pre == True):
            return self.__escapeCharacters(__line)

        if (self.__line_type_tracker[-1] == "raw"):
            return __line

        # Parser tracks leading whitespace, so remove it.
        __line = __line.lstrip(' ')

        # Escape &, *, <, and > characters. Also escape inline code blocks.
        __line = self.__escapeCharacters(__line)

        # If the parser finds a blank line, close open block-level elements,
        # reset the block-level element tracker, and return the blank line.
        if (len(__line) == 0):
            __line = self.__closeOut()
            self.__close_out = []
            return __line

        # Handle unorered lists
        ## Write opening tag and append the closing tag to the block-level
        ## element tracker.
        if (self.__line_type_tracker[-1] == "ul"):
            __line = "<ul>"+'\n'+"    <li>"+__line[2:]+"</li>"
            self.__close_out.append("</ul>\n")
        ## Write closing tag and remove a closing tag from the block-level
        ## element tracker.
        elif (self.__line_type_tracker[-1] == "/ul"):
            __line = "</ul>\n<li>"+__line[2:]+"</li>"
            self.__close_out.remove("</ul>\n")
        # Handle ordered lists
        ## Write opening tag and append the closing tag to the block-level
        ## element tracker.
        elif (self.__line_type_tracker[-1] == "ol"):
            __line = "<ol>"+'\n'+"    <li>"+". ".join(__line.split(". ")[1:])+"</li>"
            self.__close_out.append("</ol>\n")
        ## Write closing tag and remove a closing tag from the block-level
        ## element tracker.
        elif (self.__line_type_tracker[-1] == "/ol"):
            __line = "</ol>\n<li>"+__line[2:]+"</li>"
            self.__close_out.remove("</ol>\n")
        # Handle list elements for both unordered and ordered lists.
        elif (self.__line_type_tracker[-1] == "li"):
            __line = "    <li>"+__line[2:]+"</li>"
        # Handle blockquotes, new and a continuation of an existing one.
        elif (self.__line_type_tracker[-1] == "blockquote"):
            __line = "<blockquote>\n    <p>"+self.__parseInlineMD(__line[5:])+"</p>"
            self.__close_out.append("</blockquote>\n")
        elif (self.__line_type_tracker[-1] == "bqt"):
            if (__line[5:] == ''):
                __line = ''
            else:
                __line = "    <p>"+self.__parseInlineMD(__line[5:])+"</p>"
        # Handle header elements
        elif (self.__line_type_tracker[-1] == "header"):
            # Count the number of # at the beginning of the line.
            l = len(__line) - len(__line.lstrip("#"))
            anchor = ''.join(ch for ch in __line.split(":")[0] if ch.isalnum())
            # Write the header with the appropriate level, based on number of #
            __line = "<h"+str(l)+" class=\"headers\" id=\""+anchor+"\">"+__line.strip("#").strip()+"<span>&nbsp;<a href=\"#"+anchor+"\">#</a></span></h"+str(l)+">"
            return __line
        # Handle horizontal rules
        elif (self.__line_type_tracker[-1] == "hr"):
            return "<hr style='margin:50px auto;width:50%;border:0;border-bottom:1px dashed #ccc;background:#999;' />"
        # Handle images
        elif (self.__line_type_tracker[-1] == "img"):
            # This feels a bit clunky, but seems like the best alternative to
            # regex capture groups, which seem unreliable.
            __line = __line.split("]")
            desc = __line[0][2:]
            if (" " in __line[1]):
                url = __line[1].split(" ")[0][1:]
                if ("zacjszewczyk" in url):
                    url = "/assets/"+url.split(".com/")[1]
                alt = __line[1].split(" ", 1)[1][1:-2]
            else:
                url = __line[1][1:-1]
                alt = ""
            return "<div class='image'><img src='%s' alt='%s' title='%s' /></div>" % (url, alt, desc)
        # Handle series index. This is a non-standard Markdown convention that
        # lets the writer reference an external file that contains a list of
        # links to other articles in a related series, and include them
        # automatically.
        elif (self.__line_type_tracker[-1] == "idx"):
            # Open the target file, write the opening <ul> tag, and add each
            # link in the file to the new index.
            if (not isfile("./Content/System/"+__line[1:-1])):
                return "<blink>ERROR: Index file does not exist.</blink>"
            with open("./Content/System/"+__line[1:-1], "r") as fd:
                __line = "<ul style=\"border:1px dashed gray\" id=\"series_index\">\n"
                for each in fd:
                    __line += "    <li>"+each.strip()+"</li>\n"
                __line += "</ul>"
            return __line
        # Handle footnotes
        elif (self.__line_type_tracker[-1] == "fn"):
            # line = line.replace("div ", "div id=\"fn"+str(mark)+"\" ")+"""<a class="fn" title="return to article" href="#fnref"""+str(mark)+"""\">&#x21a9;</a>"""
            mark = __line.split("]", 1)[0][5:]
            __line = "<p id='fn%s'><a class='fn' title='return to article' href='#fnref%s'>&#x21a9;</a>&nbsp;%s</p>" % (mark, mark, self.__parseInlineMD(__line[8:]))
        # Default to treating the line as a paragraph
        else:
            if (__line[-3:] == "   "):
                __line = "<p>"+__line.rstrip(' ')+"</p>\n\n<br />"
            else:
                __line = "<p>"+__line+"</p>"

        # Once all the block-level parsing is done, parse the inline Markdown
        # tags.
        if (self.__line_type_tracker[-1] not in ["blockquote", "bqt", "fn"]):
            __line = self.__parseInlineMD(__line)
        
        return __line

    # Method: clear
    # Purpose: Clear all trackers, so original class instance can be used for
    # multiple files.
    # Parameters:
    # - self: Class namespace
    # Return: none
    def clear(self):
        self.__line_tracker = ["", "", ""] # Last three lines, raw.
        self.__line_type_tracker = ["", "", ""] # Type of last three lines.
        self.__line_indent_tracker = [0, 0, 0] # Indent level of last three lines.
        self.__close_out = [] # List of block-level elements that still need closed out.
        self.__pre = False # Yes/no, is the parser in a <pre> tag?

    # Method: raw
    # Purpose: Return raw line at specified position.
    # Parameters:
    # - self: Class namespace
    # - __pos: Desired position, mangled. (Int)
    # Return:
    # - Raw, unprocessed Markdown line (String)
    def raw(self, __pos):
        return self.__line_tracker(__pos)
