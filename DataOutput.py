# -*- coding: utf-8 -*-
"""
功能：数据存储器
@Author: padluo
@Date: 2017-09-24
@Last modified by: padluo
@Last Modified time: 2017-09-24
@Email: padluo@gmail.com
"""

import codecs
import os
import urllib
import re


def Schedule(blocknum, blocksize, totalsize):
    """
    当连接上服务器及相应的数据块传输完毕时触发该回调函数，显示当前的下载进度。
    :param blocknum: 已经下载的数据块
    :param blocksize: 数据块的大小
    :param totalsize: 远程文件的大小
    :return:
    """
    per = 100.0 * blocknum * blocksize / totalsize
    if per > 100:
        per = 100
    print u'当前下载进度：%d' % (per)


class DataOutput(object):
    def __init__(self):
        self.datas = []

    def store_data(self, data):
        if data is None:
            return
        # self.datas.append(data)
        for data_single in data:
            if data_single in self.datas:
                continue
            else:
                self.datas.append(data_single)

    def output_html(self, dir, logFile):
        for data in self.datas:
            fileStr = re.findall('name=(.*)$', data)[0]
            filename = urllib.unquote(fileStr.encode('utf-8')).decode('utf-8')
            filename = filename.replace('/', '-').replace('*', '-').replace("'",
                                                                            '-') + '.scel'
            filePath = os.path.join(dir, filename)
            if not os.path.exists(dir):
                os.makedirs(dir)
            # urllib.urlretrieve(data, filename=filePath)
            try:
                with open(filePath, 'wb') as f:
                    urllib.urlretrieve(data, filename=filePath,
                                       reporthook=Schedule)
                print data + ' ' + filePath + ' has downloaded!'
            except:
                with open(logFile, 'a') as f:
                    f.write(
                        'unexcepted error while downloading file of ' + data.encode(
                            'utf-8') + ' ' + filePath.encode('utf-8') + '\n')
                return
