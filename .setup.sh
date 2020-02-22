#!/bin/bash

echo "{" > Config.json
read -p "Enter base URL, with trailing /: " meta_baseurl
echo "    \"meta_baseurl\" : \"$meta_baseurl\"," >> Config.json
read -p "Enter byline: " byline
echo "    \"byline\" : \"$byline\"," >> Config.json
read -p "Enter full name: " full_name
echo "    \"full_name\" : \"$full_name\"," >> Config.json
read -p "Enter site keywords: " meta_keywords
echo "    \"meta_keywords\" : \"$meta_keywords\"," >> Config.json
read -p "Enter site name: " meta_appname
echo "    \"meta_appname\" : \"$meta_appname\"," >> Config.json
read -p "Enter twitter profile URL: " twitter_url
echo "    \"twitter_url\" : \"$twitter_url\"," >> Config.json
read -p "Enter Instagram profile URL: " insta_url
echo "    \"insta_url\" : \"$insta_url\"" >> Config.json
echo "}" >> Config.json