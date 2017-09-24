# -*- coding: utf-8 -*-
"""
功能：爬虫调度器，协调管理其他模块，首先初始化各个模块，然后通过crawl(root_url)
方法传入入口URL，方法内部实现按照运行流程控制各个模块的工作。
@Author: padluo
@Date: 2017-09-24
@Last modified by: padluo
@Last Modified time: 2017-09-24
@Email: padluo@gmail.com
"""

from UrlManager import UrlManager
from HtmlDownloader import HtmlDownloader
from HtmlParser import HtmlParser
from DataOutput import DataOutput
import getCategory
from SogouDictParser import SogouDictParser
import os


class SpiderMan(object):
    def __init__(self):
        self.manager = UrlManager()
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        self.output = DataOutput()

    def crawl(self, root_url, dir, logFile):
        # 添加入口URL
        self.manager.add_new_url(root_url)
        # 判断url管理器中是否有新的url，同时判断抓取了多少个url
        while (
                # self.manager.has_new_url() and self.manager.old_url_size() < 2):
                self.manager.has_new_url()):
            try:
                # 从URL管理器中获取新的url
                new_url = self.manager.get_new_url()
                # HTML下载器下载网页
                html = self.downloader.download(new_url)
                # HTML解析器抽取网页数据
                new_urls, data = self.parser.parser(new_url, html)
                # 将抽取的url添加到URL管理器中
                self.manager.add_new_urls(new_urls)
                # 数据存储器存储文件
                self.output.store_data(data)
                print u"已经抓取%s个链接" % (self.manager.old_url_size())
            except Exception, e:
                print e
                print "crawl failed"
        # 数据存储器将文件输出成指定格式
        self.output.output_html(dir, logFile)


if __name__ == '__main__':
    # 提取分类ID和名字
    bigCateDict, smallCateDict = getCategory.getSogouDictCate()
    # 下载词库的基目录
    baseDir = u'./sogou_dicts'
    # 爬虫日志文件
    logFile = baseDir + u'/spider.log'
    for i in bigCateDict:
        for j in smallCateDict[i]:
            spider_man = SpiderMan()
            # 按分类存储词库文件
            downloadDir = baseDir + '/%s/%s/' % (
                bigCateDict[i], smallCateDict[i][j])
            pageUrl = 'http://pinyin.sogou.com/dict/cate/index/%s' % int(j)
            spider_man.crawl(pageUrl, downloadDir, logFile)
    # spider_man.crawl("http://pinyin.sogou.com/dict/cate/index/2",
    #                  u'./sogou_dicts/自然科学/数学/')
    print u'爬虫完毕，开始解析'
    parser = SogouDictParser()
    # 解析词库的输入基目录，即是下载词库的基目录
    inBaseDir = u'./sogou_dicts'
    # 解析词库的输出基目录
    outBaseDir = u'./sogou_out'
    # 解析日志文件
    parselogFile = outBaseDir + u'/parse.log'
    for i in bigCateDict:
        for j in smallCateDict[i]:
            inDir = inBaseDir + '/%s/%s/' % (
                bigCateDict[i], smallCateDict[i][j])
            outDir = outBaseDir + '/%s/%s/' % (
                bigCateDict[i], smallCateDict[i][j])
            if not os.path.exists(outDir):
                os.makedirs(outDir)
            parser.convert(inDir, outDir, parselogFile)
