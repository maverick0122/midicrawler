midicrawler
===========

Python抓取网页&批量下载文件方法初探（正则表达式+BeautifulSoup） 

最近两周都在学习Python抓取网页方法，任务是批量下载网站上的文件。对于一个刚刚入门python的人来说，在很多细节上都有需要注意的地方，以下就分享一下我在初学python过程中遇到的问题及解决方法。




一、用Python抓取网页

基本方法：

import urllib2,urllib

url = 'http://www.baidu.com'
req = urllib2.Request(url)
content = urllib2.urlopen(req).read()


1)、url为网址，需要加'http://'

2)、content为网页的html源码



问题：

1、网站禁止爬虫，不能抓取或者抓取一定数量后封ip

解决：伪装成浏览器进行抓取，加入headers：


import urllib2,urllib

headers = {	#伪装为浏览器抓取
    	'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
	}

req = urllib2.Request(url,headers=headers)
content = urllib2.urlopen(req).read()


更复杂的情况（需要登录，多线程抓取）可参考：http://www.pythonclub.org/python-network-application/observer-spider，很不错的教程 




2、抓取网页中的中文为乱码问题

解决：用BeautifulSoup解析网页（BeautifulSoup是Python的一个用于解析网页的插件，其安装及使用方法下文会单独讨论）


首先需要介绍一下网页中的中文编码方式，一般网页的编码会在<meta>标签中标出，目前有三种，分别是GB2312，GBK，GB18030，三种编码是兼容的，

从包含的中文字符个数比较：GB2312 < GBK < GB18030，因此如果网页标称的编码为GB2312，但是实际上用到了GBK或者GB18030的中文字符，那么编码工具就会解析错误，导致编码退回到最基本的windows-2152了。所以解决此类问题分两种情况。

1)、若网页的实际的中文编码和其标出的相符的话，即没有字符超出所标称的编码，下面即可解决


import urllib,urllib2,bs4
	
req = urllib2.Request(url)
content = urllib2.urlopen(req).read()
content = bs4.BeautifulSoup(content)
return content

2)、若网页中的中文字符超出所标称的编码时，需要在BeautifulSoup中传递参数from_encoding，设置为最大的编码字符集GB18030即可 


import urllib,urllib2,bs4
	
req = urllib2.Request(url)
content = urllib2.urlopen(req).read()
content = bs4.BeautifulSoup(content,from_encoding='GB18030')
return content



详细的中文乱码问题分析参见：http://againinput4.blog.163.com/blog/static/1727994912011111011432810/


二、用Python下载文件

使用Python下载文件的方法有很多，在此只介绍最简单的一种


import urllib

urllib.urlretrieve(url, filepath)

url为下载链接，filepath即为存放的文件路径+文件名 

更多Python下载文件方法参见：http://outofmemory.cn/code-snippet/83/sanzhong-Python-xiazai-url-save-file-code



三、使用正则表达式分析网页

将网页源码抓取下来后，就需要分析网页，过滤出要用到的字段信息，通常的方法是用正则表达式分析网页，一个例子如下：

import re

content = '<a href="http://www.baidu.com">'
match = re.compile(r'(?<=href=["]).*?(?=["])')
rawlv2 = re.findall(match,content)


用re.compile()编写匹配模板，用findall查找，查找content中所有与模式match相匹配的结果，返回一个列表，上式的正则表达式意思为匹配以‘href="'起始，以'"'结束的字段，使用非贪婪的规则，只取中间的部分 

关于正则表达式，系统的学习请参见：http://www.cnblogs.com/huxi/archive/2010/07/04/1771073.html

或 http://wiki.ubuntu.org.cn/Python%E6%AD%A3%E5%88%99%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%93%8D%E4%BD%9C%E6%8C%87%E5%8D%97

个人推荐第一篇，条理清晰，不重不漏

在此就不赘述正则表达式的学习，只总结一下我在实际写正则时的认为需要注意的几个问题：

1)、一定要使用非贪婪模式进行匹配，即*?,+?（后加?），因为Python默认使用贪婪模式进行匹配，例如'a.*b'，它会匹配文档中从第一个a和最后一个b之间的文本，也就是说如果遇到一个b，它不会停止，会一直搜索至文档末尾，直到它确认找到的b是最后一个。而一般我们只想取某个字段的值，贪婪模式既不能返回正确的结果，还大大浪费了时间，所以非贪婪是必不可少的

2)、raw字符串的使用：如果要匹配一个.,*这种元字符，就需要加'\'进行转义，即要表示一个'\'，正则表达式需要多加一个转义，写成'\\'，但是Python字符串又需要对其转义，最终变成re.compile('\\\\')，这样就不易理解且很乱，使用raw字符串让正则表达式变得易读，即写成re.compile(r'\\')，另一个方法就是将字符放到字符集中，即[\]，效果相同

3)、()特殊构造的使用：一般来说，()中的匹配模式作为分组并可以通过标号访问，但是有一些特殊构造为例外，它们适用的情况是：我想要匹配href="xxxx"这个模式，但是我只需要xxxx的内容，而不需要前后匹配的模式，这时就可以用特殊构造(?<=)，和(?=)来匹配前后文，匹配后不返回()中的内容，刚才的例子便用到了这两个构造。

4)、逻辑符的使用：如果想匹配多个模式，使用'|'来实现，比如

re.compile(r'.htm|.mid$')

匹配的就是以.htm或.mid结尾的模式，注意没有'&'逻辑运算符 



四、使用BeautifulSoup分析网页

BeautifulSoup是Python的一个插件，用于解析HTML和XML，是替代正则表达式的利器，下文讲解BS4的安装过程和使用方法

1、安装BS4

下载地址：http://www.crummy.com/software/BeautifulSoup/#Download

下载 beautifulsoup4-4.1.3.tar.gz，解压：linux下 tar xvf beautifulsoup4-4.1.3.tar.gz，win7下直接解压即可

linux:

进入目录执行：


 1, python setup.py build 

 2, python setup.py install 

或者easy_install BeautifulSoup

win7:

cmd到控制台 -> 到安装目录 -> 执行上面两个语句即可


2、使用BeautifulSoup解析网页

本文只介绍一些常用功能，详细教程参见BeautifulSoup中文文档：http://www.crummy.com/software/BeautifulSoup/bs3/documentation.zh.html

1)、包含包：import bs4

2)、读入：

req = urllib2.Request(url)
content = urllib2.urlopen(req).read()
content = bs4.BeautifulSoup(content,from_encoding='GB18030')

3)、查找内容 

a、按html标签名查找：


frameurl = content.findAll('frame')

framurl为存储所有frame标签内容的列表，例如frame[0] 为 <framename="m_rtop" target="m_rbottom"src="tops.htm"> 

b、按标签属性查找

frameurl = content.findAll(target=True)

查找所有含target属性的标签 

frameurl = content.findAll(target=‘m_rbottom’)

查找所有含target属性且值为'm_rbottom'的标签 

c、带有正则表达式的查找

rawlv2 = content.findAll(href=re.compile(r'.htm$'))

查找所有含href属性且值为以'.htm'结尾的标签 

d、综合查找

frameurl = content.findAll('frame',target=‘rtop’)


查找所有frame标签，且target属性值为'rtop'


4)、访问标签属性值和内容

a、访问标签属性值

rawlv2 = content.findAll(href=re.compile(r'.htm$'))
href = rawlv2[i]['href']

通过[属性名]即可访问属性值，如上式返回的便是href属性的值 


b)、访问标签内容

rawlv3 = content.findAll(href=re.compile(r'.mid$'))
songname = str(rawlv3[i].text)
上式访问了<a href=...>(内容)</a>标签的实际内容，由于text为unicode类型，所以需要用str()做转换 
