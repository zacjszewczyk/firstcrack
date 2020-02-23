#!/usr/local/bin/python3

# Imports
from concurrent.futures import ProcessPoolExecutor # Multiprocessing
from os import listdir, stat, mkdir, utime # File/folder operations
from os.path import isfile, isdir # File/folder operations
from time import localtime, strftime, strptime, mktime, gmtime # Mod time operations
from datetime import datetime # Runtime
from locale import getpreferredencoding # Speed up file opens
from CLI import * # FirstCrack's command-line interface
from Markdown import Markdown # Markdown parser
from random import choices # Explore page

# Constants
## BASE_DIR: Base working directory, with trailing / (String)
## MAX_PROCESSES: Process limit (Int)
## ENCODING: File system encoding (String)
## MONTHS: A map of month numbers to names (Dictionary)
BASE_DIR = "/Users/zjszewczyk/Dropbox/Code/Standalone/"
MAX_PROCESSES = 16
ENCODING = getpreferredencoding()
MONTHS = {"01":"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August","09":"September","10":"October","11":"November","12":"December"}

# Method: BuildByYear
# Purpose: Facilitate multiprocessing of year indexes
# Parameters:
# - year: Year index to build (String)
# Return: True (Operation completes), False (Operation fails)
def BuildByYear(year):
    # For each year in which a post was made, generate a 'year' file, that
    # contains links to each month in which a post was published.

    # Clear the 'year' file
    open("./html/blog/"+year+".html", "w", encoding=ENCODING).close()
    year_fd = open("./html/blog/"+year+".html", "a", encoding=ENCODING)
    # Write the opening HTML tags
    year_fd.write(template[0].replace("{{META_DESC}}", f"{year} Post Archives", 1).replace("{{TITLE}}", f"{year} Post Archives", 2).replace("{{BODYID}}", "year_archive",1))
    # Display the months listed.
    year_fd.write(f"<article>\n    <h2>\n        {year}. {stats[year]['count']} {'post' if stats[year]['count'] == 1 else 'posts'}.\n    </h2>\n</article>\n")
    # Sort the sub-dictionaries by keys, months, then iterate over it. For each
    # month in which a post was made, generate a 'month' file that contains all
    # posts made during that month.
    for month in sorted(files[year], reverse=True):
        # Add a link to the month, to the year file it belongs to.
        year_fd.write(f"<article>\n    <p>\n        <a href=\"{year}"+"-"+month+f".html\">{MONTHS[month]}</a> - {stats[year][month]['count']} {'post' if stats[year][month]['count'] == 1 else 'posts'}.\n    </p>\n</article>\n")
        # Clear the 'month' file
        open("./html/blog/"+year+"-"+month+".html", "w", encoding=ENCODING).close()
        month_fd = open("./html/blog/"+year+"-"+month+".html", "a", encoding=ENCODING)
        # Write the opening HTML tags
        month_fd.write(template[0].replace("{{META_DESC}}", f"{year}/{month} Post Archives", 1).replace("{{TITLE}}", f"{MONTHS[month]}, {year} Post Archives", 2).replace("{{BODYID}}", "month_archive",1))
        month_fd.write("<article>\n<p>\n    <h2>\n        "+MONTHS[month]+", <a href=\""+year+".html\">"+year+f"</a>. {stats[year][month]['count']} {'post' if stats[year][month]['count'] == 1 else 'posts'}.\n    </h2>\n</p>\n</article>\n")

        # Sort the sub-dictionaries by keys, days, then iterate over it.
        for day in sorted(files[year][month], reverse=True):
            # Sort the sub-dictionaries by keys, timestamps, then iterate over it
            for timestamp in sorted(files[year][month][day], reverse=True):
                fd = open(BASE_DIR+"Content/"+files[year][month][day][timestamp], "r", encoding=ENCODING)
                article_title = fd.readlines()[1][7:]
                fd.close()
                # For each article made in the month, add an entry on the appropriate
                # 'month' structure file.
                month_fd.write(f"<article>\n    <p>{year}/{month}/{day} {timestamp}: <a href=\""+files[year][month][day][timestamp].lower().replace(" ", "-")[0:-3]+f"html\">{article_title.strip()}</a></p>\n</article>\n")

        # Write closing HTML tags to the month file.
        month_fd.write(template[1])
        month_fd.close()

    # Write closing HTML tags to the year file.
    year_fd.write(template[1])
    year_fd.close()

    # Cleanup
    del article_title, year_fd, month_fd
    return True

# Method: BuildFromTemplate
# Purpose: Build a static structure file based on a template.
# Parameters:
# - content_file: Name of the source file (String)
# - title: Output page title. Optional (String)
# Return: True (Operation completes), False (Operation fails)
def BuildFromTemplate(content_file,title):
    if (title == "Index"): title = "Home" # Fix title for home page
    # Clear, then open output file
    open(f"./html/{content_file}", "w", encoding=ENCODING).close()
    o_fd = open(f"./html/{content_file}", "a", encoding=ENCODING)
    # Write opening HTML tags, after inserting page title and meta description.
    o_fd.write(template[0].replace("{{TITLE}}", title, 2).replace("{{META_DESC}}", title, 1).replace("{{BODYID}}", title.lower(),1))

    # Write content from source file to output file
    s_fd = open(f"./templates/{content_file}", encoding=ENCODING)
    o_fd.write("<article>\n"+s_fd.read()+"\n</article>")
    s_fd.close()

    # Write closing HTML tags
    o_fd.write(template[1])
    # Close file and return success
    o_fd.close()
    return True

# Method: GetContent
# Purpose: Get title, link, mod time, structure file, and first paragraph of
# original post or entire linkpost.
# Parameters:
# - content_file: Target content file (String)
# Return: [title, link, mtime, structure_file, content]
def GetContent(content_file):
    structure_file = content_file.lower().replace(' ', '-')[0:-3]+'html'
    # Open structure file
    fd = open(f"./html/blog/{structure_file}", "r", encoding=ENCODING)

    # Skip to <article>
    for i,line in enumerate(fd):
        if (line.strip() == "<article>"):
            break

    # Start recording content (content), and keep track of article type (t)
    content = "<article>\n"
    t = ""
    # Retrieve title and first paragraph of original article, or entire linkpost
    for i,line in enumerate(fd):
        line = line.strip()
        content += line+"\n"
        if (i == 1):
            title = line.split("\">")[1].replace("</a>", "")
            link = line.split("href=\"")[1].split("\">")[0]
            t = line.split("class=\"")[1].split("\" ")[0]
        elif (i == 3):
            mtime = line.split("datetime=\"")[1].split("\"",1)[0]
        elif (t == "original" and i == 4): 
            content += "</article>\n"
            break
        else:
            if (line == "</article>"): break
    # Close, clean, and return
    fd.close()
    del fd, t
    return [title,link,mtime,structure_file,content]

# Method: Migrate
# Purpose: For files without the header information in their first five lines, generate
# that information, insert it into the file, and revert the update time.
# Parameters
# - content_file: Path to content file. (String)
def Migrate(content_file):
    # Store mod time for later
    mtime = stat(content_file).st_mtime

    # Open the target file and read the first line.
    fd = open(content_file, "r", encoding=ENCODING)
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
        article_url = content_file.replace(".txt", ".html").replace(" ", "-").replace("'","").lower()
        article_content = fd.readline()

    # Read the rest of the article's content from the file.
    article_content = fd.read()
    fd.close()

    # Clear the target file, then write it's contents into it after the header information.
    fd = open(content_file, "w", encoding=ENCODING)
    fd.write(f"Type: {article_type}\nTitle: {article_title.strip()}\nLink: {article_url.strip()}\nPubdate: {mod_time}\nAuthor: {config['byline']}\n\n{article_content.strip()}")
    fd.close()

    # Cleanup and revert the update time for the content file
    del fd, article_content, article_title, article_url
    utime(content_file, (mtime,mtime))

# Method: Revert
# Purpose: Check file timestamp against article timestamp. Correct if necessary.
# Parameters:
# - content_file: Path to content file (String)
def Revert(content_file):
    fd = open(content_file, "r", encoding=ENCODING)
    fd.readline()
    fd.readline()
    fd.readline()
    mtime = mktime(strptime(fd.readline()[9:].strip(), "%Y/%m/%d %H:%M:%S"))
    fd.close()

    if (mod_time != stat(content_file).st_mtime):
        print("Does not match for",content_file)
        print("Reverting to",mtime)
        utime(content_file, (mtime, mtime))

    # Cleanup
    del fd, mtime

# Method: TestAndBuild
# Purpose: Test for existence and equivalence of content and structure files,
# and (re)build the structure file if necessary.
# Parameters:
# - content_file: Name of file to check (String)
# - mtime: Modtime of file to check (Int)
# Return: True (No change), False (File rebuilt)
def TestAndBuild(content_file,mtime):
    md = Markdown(config["meta_baseurl"])
    # Transform content file name into structure file name
    structure_file = content_file.lower().replace(" ", "-")[0:-3]+"html"

    # (Re)build structure files that either do not exist, or whose mod time does
    # not match that of their corresponding content file
    if ((isfile(f"./html/blog/{structure_file}")) and (mtime == stat(f"./html/blog/{structure_file}").st_mtime)): return True

    # Open input (content_fd), then open and clear output (structure_fd) file.
    content_fd = open(f"{BASE_DIR}Content/{content_file}", "r", encoding=ENCODING)
    open(f"./html/blog/{structure_file}", "w", encoding=ENCODING).close()
    structure_fd = open(f"./html/blog/{structure_file}", "a", encoding=ENCODING)

    # Add header if necessary, with Revert()
    header = {}
    line = content_fd.readline()
    if ("Type: " not in line):
        content_fd.close()
        Migrate(content_file)
        content_fd = open(f"{BASE_DIR}Content/{content_file}", "r", encoding=ENCODING)
    else:
        line = line.split(":", 1)
        header[line[0].lower()] = line[1].strip()

    # Capture header info from each content file
    for i,line in enumerate(content_fd):
        line = line.strip()
        if (line == ""):
            break
        line = line.split(":", 1)
        header[line[0].lower()] = line[1].lstrip()

    # Conver to struct_time to include timestamp
    mtime = localtime(mtime)

    # Enumerate rest of each content file
    for i,line in enumerate(content_fd):
        if (i == 0): # First paragraph in file.
            structure_fd.write(template[0].replace("{{META_DESC}}", line.strip().replace("\"", "&#8243;")).replace("{{TITLE}}", header["title"], 2))
            if (header["type"] == "original"):
                structure_fd.write(f"""<article>\n<h2 id='article_title'>\n<a class=\"original\" href=\"/blog/{structure_file}\">{header["title"]}</a>\n</h2>\n""")
            else:
                structure_fd.write("<article>\n<h2 id='article_title'>\n<a class=\"linkpost\" href=\""+header["link"]+"\">"+header["title"]+"</a>\n</h2>\n")
            structure_fd.write(f"""<time id='article_time' datetime="{mtime.tm_year}-{mtime.tm_mon}-{mtime.tm_mday} {mtime.tm_hour}:{mtime.tm_min}:{mtime.tm_sec}-0400" pubdate="pubdate">By <link rel="author">{header["author"]}</link> on <a href="/blog/{mtime.tm_year}.html">{mtime.tm_year}</a>/<a href="/blog/{mtime.tm_year}-{mtime.tm_mon if mtime.tm_mon > 9 else "0"+str(mtime.tm_mon)}.html">{mtime.tm_mon}</a>/{mtime.tm_mday} {mtime.tm_hour}:{mtime.tm_min}:{mtime.tm_sec} EST</time>\n""")
            structure_fd.write(md.html(line)+"\n")
        else:
            structure_fd.write(md.html(line)+"\n")
    else:
        structure_fd.write("\n"+md.html("{EOF}"))

    # Write closing HTML tags and close files
    structure_fd.write(f"\n</article>\n<p>\n<a href=\"/blog/{structure_file}\">Permalink.</a>\n</p>\n{template[1]}")
    content_fd.close()
    structure_fd.close()

    # Convert back to seconds since the epoch for setting mod time, then set
    mtime = mktime(mtime)
    utime(f"./html/blog/{structure_file}", (mtime, mtime))

    # Cleanup and return
    del structure_file, content_fd, structure_fd, header
    return False

# If run as a standalone script, build the website
if (__name__ == "__main__"):
    ActivateInterface()

    # Record start time
    t1 = datetime.now()

    # Check and, if necessary, mend directory structure. See README for info.
    if (not isdir("./templates")):
        mkdir("./templates")
    if (not isdir("./html")):
        mkdir("./html")
    if (not isdir("./html/blog")):
        mkdir("./html/blog")

    # Check for key files, i.e. those listed above. Exit on fail.
    for each in ["./Config.json", "./templates/main.html", "./html/assets/main.css"]:
        if (not isfile(each)):
            print(f"{c.FAIL}Error:{c.ENDC} {each} does not exist.")
            exit(0)
    # Check for additional key files listed above. Warn on fail.
    for each in ["./html/assets/manifest.json", "./html/assets/images/favicon.ico"]:
        if (not isfile(each)):
            print(f"{c.WARNING}Warning:{c.ENDC} {each} does not exist.")

    # Load main template file
    # template[0]: Opening HTML tags up to opening article tag, inclusive.
    # template[1]: Closing article tag to closing HTML tag.
    fd = open("./templates/main.html", "r", encoding=ENCODING)
    template = fd.read().split("<!-- DIVIDER -->")
    fd.close()

    # Read Config.json file into config dictionary
    config = {}
    fd = open("./Config.json", "r", encoding=ENCODING)
    for each in fd.readlines()[1:-1]:
        each = each.strip().split(" : ")
        config[each[0].replace("\"", "")] = each[1].rstrip(",").replace("\"", "")
    fd.close()

    # Make replacements in template based on config file
    template[0] = template[0].replace("{{byline}}", config["byline"], 5).replace("{{meta_appname}}", config["meta_appname"], 1).replace("{{meta_keywords}}", config["meta_keywords"], 1).replace("{{meta_baseurl}}", config["meta_baseurl"], 1).replace("{{full_name}}", config["full_name"], 1)
    template[1] = template[1].replace("{{twitter_url}}", config["twitter_url"], 1).replace("{{insta_url}}", config["insta_url"], 1).replace("{{full_name}}", config["full_name"], 1)

    # Build list of files (files), track stats (stats), and track success
    # or failure of generator function (results)
    files = {}
    stats = {}
    stats["total_count"] = 0
    results = []

    # Instantiate the multiprocessing orchestrator to use at most MAX_PROCESSES
    orchestrator = ProcessPoolExecutor(max_workers=MAX_PROCESSES)
    
    # Enumerate the "Content" directory
    for file in listdir(BASE_DIR+"Content"):
        if (file[-4:] != ".txt"): continue # Exclude non-text files
        stats["total_count"] += 1 # Increment total count
        
        # Get mod time, then test for existence and equivalence of structure
        # file with TestAndBuild. Multiprocessed.
        mtime = stat(f"{BASE_DIR}Content/{file}").st_mtime
        # TestAndBuild(file,mtime)
        results.append(orchestrator.submit(TestAndBuild,file,mtime))

        # Convert mtime to YYYY/MM/DD/HH:MM:SS format for dictionary indexing 
        mtime = strftime("%Y/%m/%d/%H:%M:%S", localtime(mtime)).split("/")

        # Build files dictionary {year: {month: {day: {time ...} ...} ...} ...}
        if (mtime[0] not in files):
            stats[mtime[0]] = {"count":0}
            files[mtime[0]] = {}
        if (mtime[1] not in files[mtime[0]]):
            stats[mtime[0]][mtime[1]] = {"count":0}
            files[mtime[0]][mtime[1]] = {}
        if (mtime[2] not in files[mtime[0]][mtime[1]]):
            stats[mtime[0]][mtime[1]][mtime[2]] = {"count":0}
            files[mtime[0]][mtime[1]][mtime[2]] = {}
        if (mtime[3] not in files[mtime[0]][mtime[1]][mtime[2]]):
            files[mtime[0]][mtime[1]][mtime[2]][mtime[3]] = {}
        stats[mtime[0]]["count"] += 1 # Add one to year count
        stats[mtime[0]][mtime[1]]["count"] += 1 # Add one to month count
        stats[mtime[0]][mtime[1]][mtime[2]]["count"] += 1 # Add one to day count
        files[mtime[0]][mtime[1]][mtime[2]][mtime[3]] = file
    
    # Wait for all article and static pages to build before proceeding
    orchestrator.shutdown(wait=True)

    # Don't rebuild if nothing has changed
    if (not all([x.result() for x in results])):
        orchestrator = ProcessPoolExecutor(max_workers=MAX_PROCESSES)

        # Build index, projects, and disclaimers pages based on template files
        for file in listdir("./templates/"):
            if (file != "main.html"): # Exclude main template file
                results.append(orchestrator.submit(BuildFromTemplate,file,file.split(".")[0].title()))

        # Build all year and month indexes
        for year in files:
            results.append(orchestrator.submit(BuildByYear,year))

        # Build blog and archives pages, and RSS feed
        paragraphs = []
        for year in sorted(files, reverse=True):
            for month in sorted(files[year], reverse=True):
                for day in sorted(files[year][month], reverse=True):
                    for time in sorted(files[year][month][day], reverse=True):
                        paragraphs.append(orchestrator.submit(GetContent, files[year][month][day][time]))
        orchestrator.shutdown(wait=True)

        # Clear blog, archives, and feed files, then write opening tags
        open("./html/blog.html", "w", encoding=ENCODING).close()
        blog_fd = open("./html/blog.html", "a", encoding=ENCODING)
        blog_fd.write(template[0].replace("{{META_DESC}}", f"{config['byline']}'s Blog").replace("{{TITLE}}", "Blog", 2).replace("{{BODYID}}", "blog", 1))
        open("./html/archives.html", "w", encoding=ENCODING).close()
        archives_fd = open("./html/archives.html", "a", encoding=ENCODING)
        archives_fd.write(template[0].replace("{{META_DESC}}", f"{config['byline']}'s Post Archive").replace("{{TITLE}}", "Post Archive", 2).replace("{{BODYID}}", "postarchives", 1))
        # Clear and initialize the RSS feed
        open("./html/rss.xml", "w", encoding=ENCODING).close()
        feed_fd = open("./html/rss.xml", "a", encoding=ENCODING)
        feed_fd.write(f"""<?xml version='1.0' encoding='ISO-8859-1' ?>\n<rss version="2.0" xmlns:sy="http://purl.org/rss/1.0/modules/syndication/" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n    <title>{config['byline']}</title>\n    <link>{config['meta_baseurl']}</link>\n    <description>RSS feed for {config['byline']}'s website, found at {config['meta_baseurl']}/</description>\n    <language>en-us</language>\n    <copyright>Copyright 2012-2020, {config['byline']}. All rights reserved.</copyright>\n    <atom:link href="{config['meta_baseurl']}rss.xml" rel="self" type="application/rss+xml" />\n    <lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %I:%M:%S")} GMT</lastBuildDate>\n    <ttl>5</ttl>\n    <generator>First Crack</generator>\n""")
        
        # Add the first 32 posts to the home page, and the rest to the archive
        for i,each in enumerate(paragraphs):
            each = each.result()
            if (i < 32):
                blog_fd.write(each[-1].replace("</article>", f"<p><a class='read_more_link' href='/blog/{each[3]}'>Read more</a><span class='logo'>&#x24E9;</span></p>\n</article>"))
            else:
                archives_fd.write(each[-1].replace("</article>", f"<p><a class='read_more_link' href='/blog/{each[3]}'>Read more</a><span class='logo'>&#x24E9;</span></p>\n</article>"))
            
            each = [x.replace("&", "&amp;") for x in each]
            # Add all posts to the feed
            feed_fd.write(f"{' '*8}<item>\n{' '*12}<title>{each[0]}</title>\n{' '*12}<link>{each[1] if each[1][0] != '/' else config['meta_baseurl']+each[1][1:]}</link>\n{' '*12}<guid isPermaLink='true'>{each[1] if each[1][0] != '/' else config['meta_baseurl']+each[1][1:]}</guid>\n{' '*12}<pubDate>{strftime('%a, %d %b %Y %H:%M:%S',gmtime(mktime(strptime(each[2], '%Y-%m-%d %H:%M:%S-0400'))))} GMT</pubDate>\n{' '*12}<description>\n")
            if ("<html>" in each[-1]): feed_fd.write(f"{' '*16}&lt;p&gt;This post must be viewed online.&lt;/p&gt;\n")
            else: feed_fd.write(f"{' '*16}"+'\n'.join(each[-1].split('\n')[5:-2]).replace('href=\"/','href=\"'+config["meta_baseurl"]).replace('src=\'/','src=\''+config["meta_baseurl"]).replace('<', '&lt;').replace('>', '&gt;')+"\n")
            feed_fd.write(f"{' '*12}</description>\n{' '*8}</item>\n")
        
        # Write closing HTML/XML and close the files
        blog_fd.write(template[1])
        blog_fd.close()
        archives_fd.write(template[1])
        archives_fd.close()
        feed_fd.write("""\n</channel>\n</rss>""")
        feed_fd.close()

        # Finally, build Explore page
        fd = open("./html/explore.html", "w", encoding=ENCODING).close()
        fd = open("./html/explore.html", "a", encoding=ENCODING)
        fd.write(template[0].replace("{{META_DESC}}", f"{config['byline']}'s Explore Page").replace("{{TITLE}}", "Explore", 2).replace("{{BODYID}}","explore",1))
        for each in choices(paragraphs, k=3):
            fd.write(each.result()[-1])
        fd.write(template[1])
        fd.close()

    # Record end time
    t2 = datetime.now()

    # Output execution time, and if run with verbose flag "-v", output stats
    print(f"Execution time: {c.BOLD}{(t2-t1).total_seconds()}s{c.ENDC}")
    if ("-v" in argv):
        print(f"-- Years: {len(stats.keys())-1}")
        print(f"-- Months: {sum([len(files[x]) for x in files])}")
        print(f"-- Days: {sum([sum(z) for z in [[len(files[x][y]) for y in files[x]] for x in files]])}")
        print(f"-- Posts: {stats['total_count']}")
        if (all([x.result() for x in results])): print(f"{c.OKGREEN}No update necessary.{c.ENDC}")
        else: print(f"{c.WARNING}Site updated and rebuilt.{c.ENDC}")