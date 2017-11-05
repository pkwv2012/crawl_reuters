#!/usr/bin/python3

import pprint
import random
import requests

from bs4 import BeautifulSoup
from MagicGoogle import MagicGoogle
from selenium import webdriver

class GoogleSearch:
    def __init__(self, logger):
        service_args = [
            '--proxy=162.105.146.128:65434',
            '--proxy-type=http',
            '--proxy-auth=lcq:lcq123',
        ]
        self.browser = webdriver.PhantomJS(service_args=service_args)

        self.magic_google_tool = MagicGoogle()

        self.logger = logger

    def __del__(self):
        # close the brower
        self.browser.close()

    def search(self, query):
        '''

        :param query: keywords filled in Google
        :return: url list of reuters
        '''
        url = self.magic_google_tool.get_url_from_query(query=query)
        url = url.replace('https', 'http')
        self.browser.get(url)
        self.logger.info(url)
        reuters_url = list()
        for element in self.browser.find_elements_by_class_name('r'):
            a = element.find_element_by_tag_name('a')
            href = a.get_attribute('href')
            self.logger.info(href)
            '''
            :href is like
            http://www.google.com.hk/url?
            q=http://www.reuters.com/article/us-htc-earnings-idUSBREA0403F20140105
            &sa=U&ved=0ahUKEwj_tLuOo6fXAhUQ1WMKHX_8CosQFggUMAA&usg=AOvVaw3bKHvO8BEtJDYQ3uMvsrSj
            '''
            href = href[href.find('q=') + 2 : href.find('&')]
            if 'reuters' in href:
                reuters_url.append(href)
        return reuters_url