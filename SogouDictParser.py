# -*- coding: utf-8 -*-
"""
功能：搜狗词库解析器
@Author: padluo
@Date: 2017-09-24
@Last modified by: padluo
@Last Modified time: 2017-09-24
@Email: padluo@gmail.com
"""

import struct
import os
import hashlib
import time
import getCategory


class SogouDictParser(object):
    """搜狗词库解析器"""
    # 拼音表偏移，
    pinyin_table_offset = 0x1540

    # 汉语词组表偏移
    chinese_word_offset = 0x2628

    # 词库名
    dict_name_start = 0x130
    dict_name_end = 0x338

    # 词库类型
    dict_type_start = 0x338
    dict_type_end = 0x540

    # 词库描述
    dict_desc_start = 0x540
    dict_desc_end = 0xD40

    # 词库示例
    dict_sample_start = 0xD40
    dict_sample_end = pinyin_table_offset

    def __init__(self):
        self.dict_name = ""
        self.dict_description = ""
        self.dict_sample = ""
        self.pinyin_table = {}
        self.result_table = []

    def byte2str(self, data):
        """
        将原始字节码转为字符串
        :param data: 原始数据
        :return: 字符串
        """
        i = 0
        length = len(data)
        ret = u''
        while i < length:
            x = data[i] + data[i + 1]
            t = unichr(struct.unpack('H', x)[0])
            if t == u'\r':
                ret += u'\n'
            elif t != u' ':
                ret += t
            i += 2
        return ret

    def get_pinyin_table(self, data):
        """获取拼音表"""
        if data[0:4] != "\x9D\x01\x00\x00":
            return None
        data = data[4:]
        pos = 0
        length = len(data)
        while pos < length:
            index = struct.unpack('H', data[pos] + data[pos + 1])[0]
            pos += 2
            l = struct.unpack('H', data[pos] + data[pos + 1])[0]
            pos += 2
            py = self.byte2str(data[pos:pos + l])
            self.pinyin_table[index] = py
            pos += l

    def get_word_pinyin(self, data):
        """获取一个词组的拼音"""
        pos = 0
        length = len(data)
        ret = u''
        while pos < length:
            index = struct.unpack('H', data[pos] + data[pos + 1])[0]
            ret += self.pinyin_table[index]
            pos += 2
        return ret

    def get_word(self, data):
        """获取一个词组"""
        pos = 0
        length = len(data)
        ret = u''
        while pos < length:
            index = struct.unpack('H', data[pos] + data[pos + 1])[0]
            ret += self.pinyin_table[index]
            pos += 2
        return ret

    def get_chinese(self, data):
        """读取中文表"""
        pos = 0
        length = len(data)
        while pos < length:
            # 同音词数量
            same = struct.unpack('H', data[pos] + data[pos + 1])[0]
            # 拼音索引表长度
            pos += 2
            py_table_len = struct.unpack('H', data[pos] + data[pos + 1])[0]
            # 拼音索引表
            pos += 2
            pinyin = self.get_word_pinyin(data[pos: pos + py_table_len])
            # 中文词组
            pos += py_table_len
            for i in xrange(same):
                # 中文词组长度
                c_len = struct.unpack('H', data[pos] + data[pos + 1])[0]
                # 中文词组
                pos += 2
                word = self.byte2str(data[pos: pos + c_len])
                # 扩展数据长度
                pos += c_len
                ext_len = struct.unpack('H', data[pos] + data[pos + 1])[0]
                # 词频
                pos += 2
                frequency = struct.unpack('H', data[pos] + data[pos + 1])[0]
                # 保存
                self.result_table.append((word, pinyin, frequency))
                # 到下个词的偏移位置
                pos += ext_len

    def get_dict_name(self, data):
        """获取词库名称"""
        data = data[self.dict_name_start:self.dict_name_end]
        source = data.encode("hex")
        while len(source) > 0 and source[
                                  len(source) - 4: len(source)] == "0000":
            source = source[:len(source) - 4]
        return self.byte2str(source.decode("hex"))

    def get_dict_description(self, data):
        """获取词库简介"""
        data = data[self.dict_desc_start:self.dict_desc_end]
        source = data.encode("hex")
        while len(source) > 0 and source[
                                  len(source) - 4: len(source)] == "0000":
            source = source[:len(source) - 4]
        return self.byte2str(source.decode("hex"))

    def get_dict_sample(self, data):
        """获取词库示例"""
        data = data[self.dict_sample_start:self.dict_sample_end]
        source = data.encode("hex")
        while len(source) > 0 and source[
                                  len(source) - 4: len(source)] == "0000":
            source = source[:len(source) - 4]
        return self.byte2str(source.decode("hex"))

    def parser(self, data):
        """解析"""
        self.pinyin_table = {}
        self.result_table = []
        self.get_dict_name(data)
        self.get_dict_description(data)
        self.get_dict_sample(data)
        self.get_pinyin_table(
            data[self.pinyin_table_offset:self.chinese_word_offset])
        self.get_chinese(data[self.chinese_word_offset:])

    def convert_to_textfile(self, source_file, output_file, encode="utf-8"):
        """输出到文件"""
        dict_file = open(source_file, "rb")
        data = dict_file.read()
        print source_file
        self.parser(data)
        print output_file
        f = open(output_file, 'w')
        for word, pinyin, frequency in self.result_table:
            f.write(unicode(word + " " + pinyin + " " + str(frequency)).encode(
                encode))
            f.write('\n')
        f.close()
        dict_file.close()

    def convert(self, directory, output, logFile, encode="utf-8"):
        """
        批量转换词库文件到文本文件
        :param directory: 词库文件目录
        :param output: 输出文件目录
        :param encode: 编码
        :return: None
        """
        print u"批量转换词库文件到文本文件"
        begin = time.time()
        file_count = 0
        for root, dirs, files in os.walk(directory):
            for f in files:
                ext = os.path.splitext(f)[1]
                if ext != ".scel":
                    continue
                file_count += 1
                filename = os.path.splitext(f)[0]
                out_name = filename + ".txt"
                in_path = os.path.join(directory, f)
                out_path = os.path.join(output, out_name)
                try:
                    self.convert_to_textfile(in_path, out_path, encode)
                except (IndexError, KeyError) as e:
                    with open(logFile, 'a') as f:
                        f.write(in_path.encode('utf-8') + ' ' + in_path.encode(
                            'utf-8') + str(e) + '\n')
                continue
        end = time.time()
        dur = end - begin
        print u"处理%d个词库，耗时：%.2f秒" % (file_count, dur)

    def merge(self, directory, result_file="result.sogou"):
        """合并多个解析好的文本文件到一个大文件，去重"""
        print "合并多个解析好的文本文件到一个大文件"
        begin = time.time()
        temp_files = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a",
                      "b", "c", "d", "e", "f"]
        dictionary = {}
        result = {}

        # 打开每个临时文件，准备写入
        for t in temp_files:
            name = t + ".temp"
            path = os.path.join(directory, name)
            dictionary[t] = open(path, "wb")

        # 变量指定文件夹的文件，目前仅编译第一层，将文件的每一行hash到临时文件内
        file_count = 0
        word_count = 0
        for root, dirs, files in os.walk(directory):
            for f in files:
                if os.path.splitext(f)[1] != ".txt":
                    continue

                file_count += 1
                full_name = os.path.join(directory, f)
                handle = open(full_name, "r")
                for line in handle.readlines():
                    split = line.split(" ")
                    if len(split) == 3:
                        word_count += 1
                        word = split[0]
                        word_hash = (hashlib.md5(word)).hexdigest()
                        temp = word_hash[-1:]
                        dictionary[temp].write(line)
                handle.close()

        for t in temp_files:
            dictionary[t].close()

        # 去重
        for t in temp_files:
            name = t + ".temp"
            path = os.path.join(directory, name)
            dictionary[t] = open(path, "rb")
            for line in dictionary[t].readlines():
                split = line.split(" ")
                word = split[0]
                pinyin = split[1]
                freq = split[2]
                result[word] = [pinyin, freq]
            dictionary[t].close()
            name = t + ".temp"
            path = os.path.join(directory, name)
            os.remove(path)

        final_file = os.path.join(directory, result_file)
        handle = open(final_file, "wb")
        for r in result:
            handle.write(r + " " + result[r][0] + " " + result[r][1])
        handle.close()

        word_count_dist = len(result)
        end = time.time()
        dur = end - begin
        print "合并%d个文本文件，处理%d个词组，去重后剩%d个词组，耗时：%.2f秒" % (
            file_count, word_count, word_count_dist, dur)


if __name__ == "__main__":
    bigCateDict, smallCateDict = getCategory.getSogouDictCate()
    parser = SogouDictParser()
    inBaseDir = u'./sogou_dicts'
    outBaseDir = u'./sogou_out'
    logFile = outBaseDir + u'/parse.log'
    for i in bigCateDict:
        for j in smallCateDict[i]:
            inDir = inBaseDir + '/%s/%s/' % (
                bigCateDict[i], smallCateDict[i][j])
            outDir = outBaseDir + '/%s/%s/' % (
                bigCateDict[i], smallCateDict[i][j])
            if not os.path.exists(outDir):
                os.makedirs(outDir)
            parser.convert(inDir, outDir, logFile)
            # try:
            #     parser.convert(inDir, outDir)
            # except (IndexError, KeyError) as e:
            #     with open(logFile, 'a') as f:
            #         f.write(inDir.encode('utf-8') + ' ' + outDir.encode('utf-8') + str(e) + '\n')
            # continue
