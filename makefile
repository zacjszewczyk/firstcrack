# Reference document: https://www.gnu.org/software/make/manual/make.html

# PHONY declarations
## default - Update the website.
## author  - Enter First Crack's "Authoring" mode.
## rebuild - Rebuild all structure files.
## preview - Try to open the website in the browser.
## deploy  - Deploy with Google Firebase, and commit changes
##           to remote source control repository.
## help	- Display the help menu.
## pull	- Pull changes from remote repo.
.PHONY: default
.PHONY: author
.PHONY: rebuild
.PHONY: preview
.PHONY: deploy
.PHONY: help
.PHONY: pull

# Rule: default
# Purpose: Update the website.
# Prerequisites:
# - .config: Create the hidden config file on first run.
default: .config
	@./blog.py

# Rule: author
# Purpose: Enter First Crack's "Authoring" mode.
# Prerequisites: none
author:
	@./blog.py -a

# Rule: rebuild
# Purpose: Rebuild all structure files.
# Prerequisites: none
rebuild:
	@./blog.py -R

# Rule: preview
# Purpose: Try to open the website in the browser.
# Prerequisites: none
preview:
	-@(open ./local/index.html || firefox ./local/index.html) || echo `date`": No browser found."

# Rule: deploy
# Purpose: Deploy with Google Firebase, and commit changes
#          to remote source control repository.
# Prerequisites: none
deploy:
	-@firebase deploy 2> /dev/null || echo `date`": No Firebase deployment found."
	-@(git add . 2> /dev/null && git commit -m "Deployment commit on `date`" && git push) || echo `date`": No local repo found."

# Rule: help
# Purpose: Display the help menu.
# Prerequisites: none
help:
	@echo "To update your website:                   make"
	@echo "To rebuild all structure files:           make rebuild"
	@echo "To enter First Crack's 'Authoring' mode:  make author"
	@echo "To preview the website in your browser:   make preview"
	@echo "To deploy with Firebase and update the                "
	@echo "remote repo:                              make deploy"
	@echo "To view this help menu again:             make help"

# Rule: .config
# Purpose: On first run, 1) Display help menu, and
#                        2) create hidden config file.
# Prerequisites: none
.config:
	@make help
	@echo
	@echo "This menu will appear until you finish setup. Use 'make help' to see it again."
	@echo
	@echo "Checking system requirements."
	@./.sys.sh
	@echo "Done checking system requirements."
	@echo
	@echo "First Crack will now prompt you to create the config file. Enter 'y'."
	@echo
	@chmod 755 blog.py
	@touch -m -t 200012312359.59 "./Content/Test Linkpost.txt" 2> /dev/null

# Rule: pull
# Purpose: Pull changes from remote repo.
# Prerequisites: none
pull:
	git pull https://github.com/zacjszewczyk/Standalone-FirstCrack.git