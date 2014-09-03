#! /usr/bin/python

from bs4 import BeautifulSoup
from sys import stdin

for tag in filter(lambda t: "href" in t.attrs,
                  BeautifulSoup(stdin.read()).find_all("a")):
    print(tag["href"])
