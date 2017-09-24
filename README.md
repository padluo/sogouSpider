# 搜狗词库爬虫
用Python实现的搜狗词库爬虫。各模块对应的内容如下

`getCategory.py`，提取词库分类ID和名字，以字典形式返回。

`SpiderMan.py`，爬虫调度器。

`UrlManager.py`，URL管理器。

`HtmlDownloader.py`，网页下载器。

`HtmlParser.py`，网页解析器。

`DataOutput.py`，数据存储器。

`SogouDictParser.py`，搜狗词库解析器。

使用方法：把主函数中的下载词库的基目录baseDir和解析词库的输出基目录outBaseDir改成自己的目录即可，注意目录末尾不能有/。

关于实现的具体细节可参考如下文章。

[搜狗词库爬虫（1）：基础爬虫架构和爬取词库分类](http://blog.csdn.net/padluo/article/details/78066791)

[搜狗词库爬虫（2）：基础爬虫框架的运行流程](http://blog.csdn.net/padluo/article/details/78077416)