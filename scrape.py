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
IGNORE = {
	"goo.gl/ZV63Cr",
	"goo.gl/1nToQ4",
	"goo.gl/q7wKp8",
	"goo.gl/dDZIsO",
	"goo.gl/R1jVTj",
	"goo.gl/B92rvj",
	"goo.gl/Au49Um",
	"goo.gl/uQvdDQ",
	"goo.gl/KBXDW9",
	"goo.gl/m3uwvU",
	"goo.gl/bhLDq0",
	"goo.gl/gdEknO",
	"goo.gl/8AUTRP",
	"goo.gl/5nz6cg",
	"goo.gl/T3mzjk",
	"goo.gl/5FwCJy",
	"goo.gl/3QGGK0",
	"goo.gl/K6E7l8",
	"goo.gl/xZM9jt",
	"goo.gl/rMFYNX",
	"goo.gl/F3noUV",
	"goo.gl/JYSlLQ",
	"goo.gl/hmgbrW",
	"goo.gl/0gNnSE",
	"goo.gl/Tw6kP9",
	"goo.gl/RB2zhx",
	"goo.gl/kJPqT3",
	"goo.gl/qllLsG",
	"goo.gl/zj9bO0",
	"goo.gl/bjAPLg",
	"goo.gl/7tKTyd",
	"goo.gl/eXeVao",
	"goo.gl/Dpoyqi",
	"goo.gl/iztHMd",
	"goo.gl/HACUad",
	"goo.gl/oJDnYs",
	"goo.gl/ia7jLd",
	"goo.gl/AJRPcI",
	"goo.gl/bS7lhD",
	"goo.gl/lyBKa0",
	"goo.gl/OmM6DN",
	"goo.gl/puUsyX",
	"goo.gl/Gc8Dsd",
	"goo.gl/P3cEUu",
	"goo.gl/9lT4ZV",
	"goo.gl/HNA9YG",
	"goo.gl/xjP4Ke",
	"goo.gl/ykmzUC",
	"goo.gl/EOiis9",
	"goo.gl/wgzU7N",
	"goo.gl/5ixjt4",
	"goo.gl/L2N5sY",
	"goo.gl/SWNo61",
	"goo.gl/06Hov3",
	"goo.gl/JOzJ9j",
	"goo.gl/8JoXn0",
	"goo.gl/y1y9Lh",
	"goo.gl/FDTdEx",
	"goo.gl/LgqaL0",
	"goo.gl/OQwgds",
	"goo.gl/hZWUau",
	"goo.gl/wfkUr7",
	"goo.gl/sK6kAA",
	"goo.gl/DpYUwO",
	"goo.gl/vLppsl",
	"goo.gl/KVDTVy",
	"goo.gl/dGrMwY",
	"goo.gl/YOTeO1",
	"goo.gl/PltckZ",
	"goo.gl/sUJ1r7",
	"goo.gl/okXi4W",
	"goo.gl/ENWVvN",
	"goo.gl/BcLOM9",
	"goo.gl/R9MgF3",
	"goo.gl/egnhgc",
	"goo.gl/Jca6KP",
	"goo.gl/1AiXEk",
	"goo.gl/iMmkIj",
	"goo.gl/E1vTJk",
	"goo.gl/pikTTi",
	"goo.gl/9KK0k0",
	"goo.gl/Oof8mG",
	"goo.gl/X1R54k",
	"goo.gl/ykH2OP",
	"goo.gl/cuSgmK",
	"goo.gl/I6Lpbz",
	"goo.gl/JFKDGw",
	"goo.gl/o0YxL2",
	"goo.gl/cCpQrU",
	"goo.gl/sWHuKQ",
	"goo.gl/FhGPJW",
	"goo.gl/v6jFEL",
	"goo.gl/hBKyB5",
	"goo.gl/mH9rXs",
	"goo.gl/3QXZ9r",
	"goo.gl/6M31VD",
	"goo.gl/ZaQQyr",
	"goo.gl/FbPhW1",
	"goo.gl/EePxH9",
	"goo.gl/LLy4UO",
	"goo.gl/yGQsaV",
	"goo.gl/MtXamT",
	"goo.gl/SaKrk1",
	"goo.gl/Jtc6vr"
};

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
				if goo_link not in IGNORE:
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
