#! /usr/bin/python

"""
A few convenient transformations for Pandoc HTML 5 output.
"""

from typing import List
import subprocess
import re

from bs4 import BeautifulSoup, Tag


_ELEMENT_OF_INTEREST = re.compile('^dt|h[1-6]$')


def xfrm_ids(name: str) -> str:
    """
    Coerce some text into something suitable for a fragment identifier.
    """
    return ''.join(filter(lambda c: c.isalnum() or c in '_-',
                          name.lower().translate({ord(c): '-'
                                                  for c in '\N{EM DASH}'
                                                           '\N{EN DASH}'
                                                           '\N{SPACE}'
                                                           '\N{LINE FEED}'})))


def autoid_elements(soup: Tag) -> Tag:
    """
    Add an id to all definition term and headers based on their contents.


    For example, there is no *nice* way to let Pandoc still parse markdown
    inside the following div:

        <div class="slide">
          <h1>Foo</h1>
          […]
        </div>
    """
    for element in soup.find_all(_ELEMENT_OF_INTEREST):
        if 'id' not in element.attrs:
            element.attrs['id'] = xfrm_ids(str(element.string))
    return soup


def figure_hyperlink(soup: Tag) -> Tag:
    """
    Make figures out of images in links.

    By default, pandoc transforms

        [![foo](bar)](baz)

        ![foo](bar)

    into (minus whitespace)

        <p><a href="baz"><img alt="bar" /></p>
        <figure>
          <img alt="foo" src="bar" />
          <figcaption>foo</figcaption>
        </figure>

    We want the first to also be a figure.
    """
    # BeautifulSoup 4, as of this writing, doesn't support these
    # pseudo-classes.
    #for img in soup.select('p > a:only-child > img:only-child[alt]'):
    for img in soup.select('p > a > img[alt]'):
        # <p><a><img alt='not blank' /></a></p>
        a = img.parent
        p = a.parent
        if len(a.contents) != 1 or \
           len(p.contents) != 1:
            continue
        figure = soup.new_tag('figure')
        figcaption = soup.new_tag('figcaption')
        figcaption.append(img.attrs['alt'])
        a.append(figcaption)
        figure.append(a)
        p.replaceWith(figure)

    return soup


def dot(txt: str) -> str:
    '''
    Replace <code class="dot"> blocks generated by fenced dot code with SVGs.

    For example:

        ```dot
        digraph {
            A -> B
        }
        ```
    '''
    return subprocess.run(['dot', '-Tsvg', '/dev/stdin'],
                          check=True,
                          stdout=subprocess.PIPE,
                          input=txt,
                          universal_newlines=True).stdout


def find_dot_code(soup: Tag) -> List[Tag]:
    return soup.select('code.dot')


def replace_dot_code(dot_code: Tag) -> None:
    svg = BeautifulSoup(dot(dot_code.text), 'xml').svg
    dot_code.clear()
    dot_code.append(svg)


def replace_all_dot_code(soup: Tag) -> None:
    for dot_code in find_dot_code(soup):
        replace_dot_code(dot_code)


if __name__ == '__main__':
    from argparse import ArgumentParser, FileType, OPTIONAL
    from sys import stdin, stdout

    argument_parser = ArgumentParser()
    argument_parser.add_argument('html', type=FileType(mode='rb'),
                                default=stdin, nargs=OPTIONAL)

    args = argument_parser.parse_args()
    soup = BeautifulSoup(args.html, 'html5lib')

    # TODO: Replace with functools.reduce
    autoided = autoid_elements(soup)
    figured = figure_hyperlink(autoided)
    replace_all_dot_code(soup)

    stdout.write(str(figured))
