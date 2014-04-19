#!/usr/bin/env python
"""
This is a image web scraper written in python.
"""

import os
import argparse
import urllib2
import re
import datetime
import webbrowser
from bs4 import BeautifulSoup

BASE_URL = 'http://developers.google.com'
AGE = 2


def modified(date_modified, allowed_margin):
    """
    Returns True if and only if the date is within the allowed
    margin of days of the current date.

    Parameters
    ----------
    date_modified (string): The date to test ("Tue, 15 Nov 1994 12:45:26 GMT")
    allowed_margin (int): The allowed number of days

    Returns
    -------
    True if the modified date is within the correct range
    """
    margin = datetime.timedelta(days=allowed_margin)
    today = datetime.date.today()

    modified_date = datetime.datetime.strptime(
        date_modified, "%a, %d %b %Y %H:%M:%S %Z").date()
    return today - margin <= modified_date <= today + margin


def is_valid_image_tag(tag):
    """
    Returns whether or not the tag is a valid image tag with a src
    and a (png|jpg|svg) file extension.

    Parameters
    ----------
    tag (BeautifulSoup tag): The tag to test

    Returns
    -------
    True if the tag is a valid iamge tag and False otherwise
    """

    return (tag.has_attr('src') and tag['src'].startswith('/')
        and (tag['src'].endswith('png') or tag['src'].endswith('svg')
            or tag['src'].endswith('jpg')))


def process_image_tags(soup):
    """
    Processes all of the images on a page.

    Parameters
    ----------
    soup (BeautifulSoup soup): The soup of the page to process

    Returns
    -------
    Nothing
    """
    for tag in soup.find_all('img'):
        try:
            if is_valid_image_tag(tag):
                parts = tag['src'].split('/')
                path = 'img/'+ parts[len(parts) - 1]
                if not os.path.isfile(path): # Don't download the same image
                    image_file = open(path, 'wb')
                    image = urllib2.urlopen(BASE_URL + tag['src'])
                    image_file.write(image.read())
                    image_file.close()
        except:
            continue


def process_a_tags(soup, links, visited):
    """
    Processes all of the a tags (links) on a page.

    Parameters
    ----------
    soup (BeautifulSoup soup): The soup of the page to process
    links (list): The list of current links to process
    visited (set): The set of links already processed

    Returns
    -------
    Nothing
    """
    for tag in soup.find_all('a'):
        if (tag.has_attr('href') and tag['href'].startswith('/')
                and '?' not in tag['href'] and tag['href'] not in visited):
            links.insert(0, tag['href'])
            visited.add(tag['href'])


def main():
    """
    Runs the image scraper on the BASE_URL
    """
    # Visited sites
    visited = set()

    # Set up command line args
    parser = argparse.ArgumentParser(
        description='Scrapes a sub directory of BASE_URL')
    parser.add_argument('dir',
        help="The input website directory starting with '/'")
    arguments = parser.parse_args()

    # Current sites to crawl
    links = [arguments.dir]
    visited.add(arguments.dir)

    while links:
        link = links.pop()
        try:
            response = urllib2.urlopen(BASE_URL + link)
            text = response.read()
            soup = BeautifulSoup(text)

            goo_links = re.findall('goo.gl\/[a-zA-Z0-9]{6}', text)
            for goo_link in goo_links:
                webbrowser.open('http://' + goo_link, new=2)

            if ('last-modified' not in response.headers.dict
                    or modified(response.headers.dict['last-modified'], AGE)):
                # print "Visited: " + str(len(visited)) + " pages"
                # print "To Do: " + str(len(links)) + " pages"
                process_image_tags(soup)
            process_a_tags(soup, links, visited)

        except:
            continue

if __name__ == '__main__':
    main()
