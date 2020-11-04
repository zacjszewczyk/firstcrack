First Crack - A simple static blogging engine written in Python
===============================================================

Given a directory of a thousand [Markdown](http://daringfireball.net/projects/markdown/) files, First Crack will generate a full-featured, lightweight, static website in less than two seconds. For a live demo, check out [my website](https://zacs.site/). I have used First Crack exclusively since 2011.

## Table of Contents
* [Front-End Features](#front-end-features)
* [Back-End Features](#back-end-features)
* [Dependencies](#dependencies)
* [Installation](#installation)
* [Directory Structure](#directory-structure)
* [Setup](#setup)
* [Usage](#usage)
* [Website Structure](#website-structure)
* [Advanced Usage](#advanced-usage)
* [Making a New Post](#making-a-new-post)
* [Editing an Existing Post](#editing-an-existing-post)
* [Editing an Existing Page](#editing-an-existing-page)
* [Deploying Your Website](#deploying-your-website)
* [Background and Motivation](#background-and-motivation)
* [License](#license)

## Front-End Features

* **Lightweight** - First Crack builds a lightweight, minimalist website. A typical page loads less than 10KB of data, including the page itself--for comparison, a typical Medium post loads over 3000KB.
* **Full-featured** - Who says a static site generator can't have cool features? One of my favorites is the Post Archives. This page makes finding a certain article easy by displaying every post you have ever published. It also allows you to view a list of posts by year and month, too. Each post's byline also includes links to the year and month it was published, so you can easily narrow your search with just a few clicks.
* **Beautiful blog** - I built First Crack to be a blogging engine, and it remains true to that core today. The blog it builds presents clean articles in an aesthetically pleasing manner, whether viewed on a large desktop computer of a small mobile phone. I designed the default layout to remove the need for "Reader Views", by showing you exactly what you need and nothing you don't.
* **Custom landing page** - I like to think of personal websites as a public resume. As such, they ought to help you put your best foot forward--and First Crack allows you to do just that, with a custom landing page. Use this page to talk about yourself, your projects, and anything else--and let your viewers check out your blog later. Don't make your thoughts on Agile the first thing a new employer sees.

## Back-End Features

* **No dependencies** - I wrote First Crack in vanilla Python. First Crack has no dependencies. 
* **Fast** - I put a lot of work into optimizing every single operation First Crack executes, and it shows: given a thousand unique Markdown files, First Crack will generate individual pages for each article, and archive pages broken up by month and year published, in less than two seconds. As of February 2020, First Crack does this in around 1.25 seconds.
* **Easy to use** - To build a website with First Crack, drop a few Markdown files into the `content` directory and run `blog.py`. That's it, First Crack takes care of the rest.
* **Platform-agnostic** - Don't worry about spinning up a special server if you use First Crack: even the most basic, bare-bones, underpowered web server can handle serving the static site it builds.

## Dependencies

First Crack does not rely on any third-party tools, code, or frameworks. It uses Python 3. 

## Installation

Because First Crack has no dependencies, installation is a breeze: just clone the repository. Open a shell and type the following commands:

```
$ git clone https://zjszewczyk@bitbucket.org/zjszewczyk/firstcrack-public.git FirstCrack
$ cd FirstCrack
```

That's it.

## Directory Structure

On install, First Crack consists of this README, two Python scripts, a `templates` directory that houses content for static pages and the main content file, a `Content` directory with two example content files, and a `html` directory where First Crack will store all structure files. 

```
FirstCrack
|__ blog.py # Main script.
|__ CLI.py # Command-line interface code.
|__ Config.json # Configuration file.
|
|__ templates # Dir. Template folder.
|  |__ main.html # Main template file.
|
|__ content # Dir. Content folder.
|  |__ *.txt # Content files.
|
|__ html # Dir. Website files.
|  |__ *.html # Main pages.
|  |__ blog # Dir. All articles.
|  |  |__ *.html # Article files.
|  |__ assets # Dir. Webpage resources.
|  |  |__ main.css # Main CSS file.
|  |  |__ manifest.json # JSON mainifest.
|  |  |__ images # Dir. All images.
|  |     |__ * # Image files.
```

## Setup

First Crack requires that you set up a configuration file before it will generate your site. This allows it to customize the site to your domain name and your niche, and build a copyright and disclaimers page with your name as the content owner. First Crack will walk you through this process the first time you run it. Do this with the following command:

```
$ make
```

First Crack will detect that this is the first time you have run it, then prompt you to answer several questions. These help customize the website it builds for you. If one does not apply to you, enter `None`. 

The config file, `Config.json`, looks like this:

```
{
    "meta_baseurl" : "Base URL for your site",
    "byline" : "Default article byline",
    "full_name" : "Full name, user for copyright disclaimer",
    "meta_keywords" : "Search engine keywords",
    "meta_appname" : "Title of your website, should it be added as an app to a mobile device",
    "twitter_url" : "URL to your Twitter profile",
    "insta_url" : "URL to your Instagram profile"
}
```

You can go back and change these values at any time. First Crack will update your site to reflect that change the next time you run `make` or `./blog.py`. Once you finish filling them out for the first time, First Crack will build your site. Check it out with `make preview`, which will start a local web server and open a local copy of your website in your default browser. 

## Usage

To build a website with First Crack, enter the following command:

```
$ make
```

You can also just run the Python file, with this command:

```
$ ./blog.py
```

That's it. First Crack ships with two example content files, which it uses to build an example website. View that site by opening the `index.html` file in the `html` directory, or by entering the following command:

```
$ make preview
```

## Website Structure

First Crack builds five pages and one RSS feed out of the box. The diagram below depicts the default site structure, which grows as you make new blog posts. First Crack updates the blog, RSS feed, and archives every time you post something new, but refers to the HTML files in the `system` folder for the content of the home and projects pages. To make this new site yours, you will need to start by editing those two documents, then wrap up by posting your first article.

```
YourDomain.com
|__Home (index.html)
|__Blog (blog.html)
| |____ Test Original Article (test-original-article.html)
| |____ Test Linkpost (test-linkpost.html)
| |____ ...
|__RSS (rss.html)
|__Post Archives (archives.html)
|__Projects (projectx.html)
|__Disclaimers (disclaimers.html)
```

## Advanced Usage

First Crack has a few advanced features that make managing a website easier, which are accessible in the command line interface. To enter the CLI, use one of the following commands:

```
$ make cli
$ ./blog.py -a
```

First Crack will display a menu of available commands, along with an explanation of each. Enter `-h` at any time to view the help menu. First Crack will continue prompting you for input in this mode until you exit it with either `exit` or `!exit`. You can also run any of these commands directly from the terminal. For example, to clear all structure files and rebuilt the entire site, use one of the following commands:

```
$ make rebuild
$ ./blog.py -R
```

## Making a New Post

Like everything else, the process for making a new post is simple. See the files in the Content directory for examples of a linkpost and an original article. To make a new post, save a text file in the `content` directory and build the site. First Crack will only build files that have changed since you last ran it, and then re-build the blog and archive pages as necessary. 

## Editing an Existing Post

To edit an existing post, just edit the text file in the `content` directory, then build the site. First Crack will now show this post at the top of the blog page, since it is now the most recently updated post. To make updates without affecting post order, update posts and then use `make timestamp` to revert post update times to that of their original publication. You can change the original publication date, title, and author by editing the file's header, and then rebuilding the site. 

## Editing an Existing Page

First Crack ships with a handful of static pages that live in the `templates` folder: `index.html`, `projects.html`, `disclaimers.html`, and `main.html`. When it builds a website, First Crack gets content for the home page from `index.html`, content for the projects page from `projects.html`, and content for the disclaimers page from `disclaimers.html`. If you want to change any of them, just edit those files.

## Deploying Your Website

If you followed [my guide to running your own website for free with First Crack and Google Firebase](https://zacs.site/blog/how-to-own-your-platform.html), you can use the simple `make deploy` command to deploy it. This command will also check for a local source control repository and update it with a generic timestamped commit message. My workflow for a new post looks something like this:

```
$ make # Once I add a new article to the Content folder, this updates the site.
$ make preview # One last check for spelling or other formatting errors. This command starts a local private web server, then opens the home page in my default browser.
$ make deploy # Deploy the updated site, update the local source control repository, and push that change to GitHub and Bitbucket.
```

## Background and Motivation

I started this project in 2011. After trying many of the day's most popular content management systems, I decided to roll my own. I began running my website on something I called First Crack a few months later. Over the years, that project morphed into the one you see before you today.

I designed First Crack with ease of use, speed, and versatility in mind. I believe these goals are evident in the engine's dead-simple setup, its ability to build over one thousand pages in less than two seconds, and the lightweight website it produces.

After almost a decade, content management systems have gotten much better since I started this project. I have yet to find anything First Crack cannot do, though, or an engine that wins out in the design goals I mentioned above. I like working on First Crack, and I look forward to adding more features in the future.

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/). Read more about the license, and my other disclaimers, [at my website](https://zacs.site/disclaimers.html).
