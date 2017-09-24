# -*- coding: utf-8 -*-
"""
功能：HTML下载器，注意网页编码
@Author: padluo
@Date: 2017-09-24
@Last modified by: padluo
@Last Modified time: 2017-09-24
@Email: padluo@gmail.com
"""

import requests


class HtmlDownloader(object):
    def download(self, url):
        if url is None:
            return None
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            r.encoding = 'utf-8'
            return r.text
        return None
