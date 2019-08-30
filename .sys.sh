#!/bin/bash

HEADER=$'\033[95m' # Pink
OKBLUE=$'\033[94m' # Purple
OKGREEN=$'\033[92m' # Green
WARNING=$'\033[93m' # Yellow
FAIL=$'\033[91m' # Red
ENDC=$'\033[0m' # None
BOLD=$'\033[1m' # Blue
UNDERLINE=$'\033[4m' # Underline

function migrate_python () {
    #echo "To search for: "$1
    #echo "To replace with: "$2
    sed -i '' "s|$1|$2|g" colors.py 2> /dev/null || sed -i "s|$1|$2|g" colors.py
    sed -i '' "s|$1|$2|g" blog.py 2> /dev/null || sed -i "s|$1|$2|g" blog.py
    sed -i '' "s|$1|$2|g" ModTimes.py 2> /dev/null || sed -i "s|$1|$2|g" ModTimes.py
    sed -i '' "s|$1|$2|g" Markdown2.py 2> /dev/null || sed -i "s|$1|$2|g" Markdown2.py
    sed -i '' "s|$1|$2|g" Hash.py 2> /dev/null || sed -i "s|$1|$2|g" Hash.py
}

printf "Searching for: Python 3 ... "
if which python3 | grep -q 'python3'; then
  printf $OKGREEN"found.\n"$ENDC
  if which python3 | grep -q '/usr/local/bin/python3'; then
    echo $OKGREEN"Path to Python 3 executable matches. No script modifications necessary."$ENDC
  else
    printf $WARNING"Path to Python 3 executable does not match. Modifying ... "$ENDC
    search="#!/usr/local/bin/python3"
    replace="#!"$(which python3)
    migrate_python $search $replace
    printf $OKGREEN"Done.\n"$ENDC
  fi
else
  printf $FAIL"Not found.$ENDC\n"
  printf $WARNING"Searching for: generic Python ... "$ENDC
  if which python | grep -q 'python' ; then
    printf $OKGREEN"Found.\n"$ENDC
    printf $WARNING"Editing path to executable ... "$ENDC
    search="#!/usr/local/bin/python3"
    replace="#!"$(which python)
    migrate_python $search $replace
    printf $OKGREEN"Done.\n"$ENDC

    echo "Searching for: generic Python version ... "
    out=$(python -c "from sys import version; print version")
    if [[ $out == *"3."* ]] ; then
        printf $OKGREEN"Found 3.\n No further modifications necessary.\n"$ENDC
    else
        if [[ $out == *"2."* ]] ; then
            printf $OKGREEN"Found 2.\n"$ENDC
            printf $WARNING"Script modification necessary ... "$ENDC
            search='print('
            replace='print ('
            migrate_python "$search" "$replace"
            search=' input('
            replace=' raw_input('
            migrate_python "$search" "$replace"
            printf $OKGREEN"Done.\n"$ENDC
        fi
    fi
  else
    echo $FAIL"Python not found. Please install Python."$ENDC
  fi
fi