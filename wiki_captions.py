# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import logging
import traceback
import os
import gzip
import requests
import codecs
from argparse import ArgumentParser
from kwiki.dumpparser import parse_lang_links
from kwiki.wiki import url_from_id, get_image_captions, trans_links

log_format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.ERROR)
log = logging.getLogger('wiki_captions')

def get_conf():
    """TODO: Docstring for get_conf.
    :returns: TODO

    """
    def langs(v):
        return set(v.split(','))
    parser = ArgumentParser(description='Crawler for wikipedia, gets captions of elements in articles')
    parser.add_argument('--langs', required=True, type=langs, help='List of languages for saving (eg. en,pl)')
    parser.add_argument('--output', default='./', type=os.path.abspath, help='Directory for saving parallel corpora')
    parser.add_argument('langlinks', help='Path to file with lang links (http://dumps.wikimedia.org/enwiki/latest/enwiki-latest-langlinks.sql.gz - need to download, no need to extract)')
    return parser.parse_args()

def get_html(article_id, langs):
    html = {}
    langs = set(langs)
    non_en_langs = langs - {'en'}
    en_url = url_from_id('en', article_id)
    log.info('Fetching url: %s', en_url)
    html['en'] = requests.get(en_url).content
    trans = dict(trans_links(html['en']))
    if not non_en_langs <= set(trans):
        return None
    for lang in non_en_langs:
        log.info('Fetching translation: %s', trans[lang])
        html[lang] = requests.get(trans[lang]).content
    return html

def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    conf = get_conf()
    files = {}
    with gzip.GzipFile(conf.langlinks) as f:
        articles = parse_lang_links('en', f)
        ids = set(a.orig_id for a in articles if a.tgt_lang in conf.langs)
    for lang in conf.langs:
        files[lang] = codecs.open(os.path.join(conf.output, 'wiki_captions.{}.txt'.format(lang)), 'w', encoding='utf-8')
    log.info('Total articles: %i', len(ids))
    for i, next_id in enumerate(ids):
        try:
            html = get_html(next_id, conf.langs)
            if html is None:
                continue
            captions = {}
            for lang in conf.langs:
                captions[lang] = dict(get_image_captions(html[lang]))
            imgs = set(captions['en'].keys())
            for lang in conf.langs:
                imgs = imgs & set(captions[lang].keys())
            for img in imgs:
                for lang in conf.langs:
                    text = captions[lang][img]
                    text.replace('\n', ' ')
                    files[lang].write(text + '\n')
            log.info('Done: %i/%i', i+1, len(ids))
        except KeyboardInterrupt:
            exit(1)
        except:
            log.error(traceback.format_exc())

if __name__ == '__main__':
    main()
