# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function


import re
from bs4 import BeautifulSoup

def get_image_captions(html):
    """TODO: Docstring for get_image_captions.

    :html: TODO
    :returns: TODO

    """
    bs = BeautifulSoup(html)
    img_divs = bs.find_all('div', class_='thumbinner')
    for div in img_divs:
        try:
            img_src = div.find('img')['src']
            caption = ' '.join(div.find('div', class_='thumbcaption').stripped_strings)
            yield img_src, caption
        except (AttributeError, KeyError):
            pass

lang_re = re.compile(r'.*(..)\.wikipedia.org.*')
def lang_from_url(url):
    """TODO: Docstring for lang_from_url.

    :url: TODO
    :returns: TODO

    """
    return lang_re.match(url).group(1)

def url_from_id(lang, article_id):
    """TODO: Docstring for url_from_id.

    :lang: TODO
    :article_id: TODO
    :returns: TODO

    """
    return 'https://{}.wikipedia.org/wiki?curid={}'.format(lang, article_id)

def trans_links(html):
    """TODO: Docstring for trans_links.

    :html: TODO
    :returns: TODO

    """
    bs = BeautifulSoup(html)
    li_list = bs.find_all('li', class_='interlanguage-link')
    for li in li_list:
        try:
            a = li.find('a')
            lang = a['lang']
            href = a['href']
            if href.startswith('//'):
                href = href[2:]
            if not href.startswith('http'):
                href = 'https://' + href
            yield lang, href
        except (AttributeError, KeyError):
            pass
