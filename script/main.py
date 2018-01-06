#!/usr/bin/python3

import logging
import os
import pprint
import random
import requests
import sys
import time
import yaml

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from google_search import GoogleSearch
from MagicGoogle import MagicGoogle
from selenium import webdriver

PROXIES = [{
    'http': 'http://lcq:lcq123@162.105.146.128:65434',
    'https': 'https://lcq:lcq123@162.105.146.128:65434',
}]

def InitLogging():
    now = datetime.now()
    global logger
    logger = logging.getLogger('reuters_monitor')
    logger.setLevel(logging.INFO)
    print(os.path.realpath(__file__))
    reuters_handler = logging.FileHandler(os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../logs_{}'.format(now.strftime("%Y_%m_%d_%H_%M_%S"))
    ))
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    reuters_handler.setFormatter(formatter)
    logger.addHandler(reuters_handler)

# key words used in searching
keys_file = '/path/to/key_file'

output_dir = '/path/to/output/dir'

def GetKeyList(filename):
    key_list = []
    with open(filename, 'r') as fin:
        key_list = fin.readlines();
        for i in range(len(key_list)):
            key_list[i] = key_list[i].strip()
    return key_list

def DownloadFromReuters(output_dir, url):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    res = requests.get(url=url, proxies=PROXIES[0])
    soup = BeautifulSoup(res.text)

    timestamp = soup.findAll('div', {'class': 'ArticleHeader_date_V9eGk'})
    if len(timestamp) == 1:
        timestamp = timestamp[0].text
    else:
        timestamp = None

    title = soup.findAll('h1', {'class': 'ArticleHeader_headline_2zdFM'})
    if len(title) >= 1:
        title = title[0].text
    else:
        title = None

    body_class_list = ['StandardArticleBody_body_1gnLA', 'ArticleBody_body_2ECha']
    for body_class in body_class_list:
        body = soup.findAll('div', {'class': body_class})
        if len(body) > 0:
            body = body[0].text
            break
        else:
            body = None

    editor = soup.findAll('div', {'class': 'Attribution_attribution_o4ojT'})
    if len(editor) > 0:
        editor = editor[0].text
    else:
        editor = None

    head_list = [title, editor, timestamp, url]
    filename = url[url.rfind('/') + 1:]
    logger.info('outpur_file={}'.format(os.path.join(output_dir, filename)))
    with open(os.path.join(output_dir, filename), 'w') as fout:
        for item in head_list:
            fout.write('-- {}\n'.format(item))
        fout.write('{}\n'.format(body))

def Main(**kwargs):
    '''
    :param kwargs:
        start_date:
        end_date:
        keywords_file:
        output_dir:
    :return:
    '''
    start_date = kwargs['start_date'] if 'start_date' in kwargs else '2017-01-01'
    end_date = kwargs['end_date'] if 'end_date' in kwargs else '2017-02-01'
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    InitLogging()

    keys_file = kwargs['keywords_file']
    key_list = GetKeyList(keys_file);
    assert len(key_list) > 0

    output_dir = kwargs['output_dir']
    mg = MagicGoogle(PROXIES)
    global logger
    searcher = GoogleSearch(logger)
    while start_date < end_date:
        for key in key_list:
            q = 'www.reuters.com/article/{} {}'.format(
                start_date.strftime("%Y/%m/%d"),
                key)
            print(q)
            logger.info('info:date={}||key_word=\'{}\'\n'.format(
                start_date.strftime("%Y-%m-%d"),
                key.lower()))
            reuters_url = searcher.search(query=q)
            print(reuters_url)
            for url in reuters_url:
                if start_date.strftime('%Y%m%d') not in url:
                    continue;
                print(url)
                DownloadFromReuters(
                    os.path.join(output_dir, start_date.strftime('%Y_%m_%d')),
                    url)

            time.sleep(random.randint(60, 120))
        start_date += timedelta(days=1)


if __name__ == '__main__':
    #
    if len(sys.argv) != 2:
        pprint.pprint("usage: python main.py /path/to/config.yaml")
        sys.exit(-1)
    config_file = sys.argv[1]
    with open(config_file, 'r') as fin:
        try:
            raw_config = yaml.load(fin)
            config = dict()
            for kw in raw_config.split(' '):
                k, v = kw.split('=')
                config[k] = v
            print(config)
            Main(**config)
        except yaml.YAMLError as e:
            global logger
            logger.error("yaml parsing error {}".format(e))
            sys.exit(-2)

