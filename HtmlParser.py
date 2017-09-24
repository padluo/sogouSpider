# -*- coding: utf-8 -*-
"""
功能：HTML解析器，提供一个parser对外接口，输入参数为当前页面的URL和HTML下载器返回的网页内容。
解析出新的URL交给URL管理器，解析出有效数据交给数据存储器。
@Author: padluo
@Date: 2017-09-24
@Last modified by: padluo
@Last Modified time: 2017-09-24
@Email: padluo@gmail.com
"""

from bs4 import BeautifulSoup
import re
import urlparse


class HtmlParser(object):
    def parser(self, page_url, html_cont):
        """
        用于解析网页内容，抽取URL和数据
        :param page_url: 下载页面的URL
        :param html_cont: 下载的网页内容
        :return: 返回URL和数据
        """
        if page_url is None or html_cont is None:
            return
        # soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        soup = html_cont
        new_urls = self._get_new_url(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data

    def _get_new_url(self, page_url, soup):
        """
        抽取新的URL集合
        :param page_url: 下载页面的URL
        :param soup: soup
        :return: 返回新的URL集合
        """
        # 非贪婪匹配,查找跳转到其他页面的url
        new_urls = set()
        pagePattern = re.compile(r'href="/dict/cate/index/\d+/default(.*?)"')
        pageResult = re.findall(pagePattern, soup)
        pageBasePattern = re.compile(
            r'(http://pinyin.sogou.com/dict/cate/index/\d+)')
        pageBaseUrl = re.match(pageBasePattern, page_url).group(0)
        for i in range(len(pageResult)):
            new_urls.add(pageBaseUrl + '/default' + pageResult[i])
        return new_urls

    def _get_new_data(self, page_url, soup):
        """
        抽取有效数据
        :param page_url: 下载页面的URL
        :param soup:
        :return: 返回有效数据
        """
        # 非贪婪匹配,查找可下载的文件
        data = []
        fileBaseUrl = 'http://download.pinyin.sogou.com'
        filePattern = re.compile(
            r'href="http://download.pinyin.sogou.com(.*?)"')
        fileResult = re.findall(filePattern, soup)
        for later in fileResult:
            fileURL = fileBaseUrl + later
            data.append(fileURL)
        return data
