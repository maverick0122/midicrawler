#-*- coding:utf-8 -*-	#允许文档中有中文
import urllib2,urllib,cookielib,threading
import os
import re
import bs4
import socket

import sys
reload(sys)
sys.setdefaultencoding('utf-8')	#允许打印unicode字符


indexurl = 'http://www.dugukeji.com/'
databasepath = './midi/linklist'
path = './midi/dugukeji/'
totalresult = {}	#map:key:link,:value:songname

def crawl(url):
	content = ''
	try:
		socket.setdefaulttimeout(50)
		headers = {	#伪装为浏览器抓取
	    	'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
		}
		req = urllib2.Request(url,headers=headers)
		content = urllib2.urlopen(req).read()
		content = bs4.BeautifulSoup(content,from_encoding='GB18030')
	except:
		print 'Error:Crawl time out!,link:',url,'\n'
	return content


def crawlframe(sourceurl,target):
	global indexurl
	content = crawl(sourceurl)
	#match = re.compile(r'(?<=target=["]'+target+'["] src=["]).*?(?=["])')	#正则表达式方法
	#frameurl = re.findall(match,content)
	frameurl = content.findAll('frame',target=target)	#beautifulsoup方法
	result = indexurl+frameurl[0]['src']
	return result

def crawllv1(frameurl,st=-1,en=-1):
	global indexurl
	content = crawl(frameurl)
	#match = re.compile(r'(?<=href=["]).*?(?=["])')
	#rawlv2 = re.findall(match,content)
	rawlv2 = content.findAll(href=re.compile(r'.htm$'))
	result = []
	if st==-1 and en==-1:
		for i in range(len(rawlv2)):
			result.append(indexurl+rawlv2[i]['href'])
	else:
		for i in range(st,en):
			result.append(indexurl+rawlv2[i]['href'])
	#dele = []
	#for i in range(len(result)):
	#	if result[i][-4:]!='.htm' and result[i][-5:]!='.html':
	#		dele.append(i)
#		else:
#			result[i]=indexurl+result[i]
#	if len(dele)>0:
#		for deli in dele:
#			del result[deli]

	#result.sort()
	return result

def crawllv2(lv2url):
	global indexurl
	global totalresult
	content = crawl(lv2url)
	#match = re.compile(r'(?<=href=["]\.\.\/).*?[">].*?(?=[<])')
	#rawlv3 = re.findall(match,content)
	rawlv3 = content.findAll(href=re.compile(r'[..].*?[0-9].htm|.mid$'))
	#print rawlv3
	result = {}	#结果字典，key：链接，value：歌曲名
	for i in range(len(rawlv3)):
		tmp = str(rawlv3[i]['href'])
		#print tmp
		link = indexurl + tmp[tmp.rfind('..')+3:]	#有多个'..'，找到最后一个

		songname = ''
		if tmp[-4:]=='.htm':	#需要访问3级页
			try:
				conlv3 = crawl(link)
			except:
				print 'WARNING: visit lv3 url failed!\n'
			else:
				rawlv4 = conlv3.findAll(href=re.compile(r'.mid$'))
				if not rawlv4:	#4级页没有.mid下载链接，略过
					continue
				else:
					tmp = str(rawlv4[0]['href'])
					link = indexurl + tmp[tmp.rfind('..')+3:]
		if totalresult.has_key(link):	#如果链接已保存，略过
			print 'LINK:',link,' exist, pass.'
			continue

		songname = str(rawlv3[i].text)	#将unicode类型的text转化为string
		#songname.decode('GBK')
		#songname.encode('utf-8')
		songname = songname.replace(' ','_')	#将songname中空格和换行转化为下划线
		songname = songname.replace('\n','_')	
		
		
		#if totalresult.has_key(link) and len(songname)<len(totalresult[link]):	#如果链接已保存且歌曲名长度比当前的长，略过
		#	continue
		totalresult[link] = songname
		result[link] = songname		#加入字典
	#result.sort()
	return result

def download(totalresult):
	for link in totalresult.keys():
		filepath = path + totalresult[link] + '.mid'
		print 'download: ',link,' -> ',filepath
		filepath = unicode(filepath,'utf8')
		urllib.urlretrieve(link, filepath)


def readdata(databasepath):
	global totalresult
	datafile = open(databasepath,'r')	#读数据文件
	link = datafile.readline()
	while link:
		totalresult[link[:-1]]=''
		link = datafile.readline()
	datafile.close()

def writedata(databasepath,result):
	datafile = open(databasepath,'a')	#追加打开数据文件，将新链接写入文件尾
	for link in result.keys():
		datafile.write(link+'\n')
	datafile.close()

if __name__ == '__main__':
	try:
		readdata(databasepath)	#访问文件，记录已下载的链接
	except:
		print 'WARNING:read database file failed!\n'
	else:
		print 'There is ',len(totalresult),' links in database.\n'

	try:
		frameurl1 = crawlframe(indexurl,'rtop')	#抓取主页中一级页url所在frame的url
	except:
		print 'WARNING: crawl lv1 frameurl failed!\n'
	try:
		urllv1 = crawllv1(frameurl1,4,20)		#抓取一级页url
	except:
		print 'WARNING: crawl lv1 url failed!\n'

	addnum = 0
	for i in urllv1:
		print 'lv1 url:',i
		try:
			frameurl2 = crawlframe(i,'rbottom')	#抓取一级页中二级页url所在frame的url
		except:
			print 'WARNING: crawl lv2 frameurl failed!\n'
		else:
			print '\tlv2 frameurl:',frameurl2
			try:
				urllv2 = crawllv1(frameurl2)	#抓取二级页url
			except:
				print 'WARNING: crawl lv2 url failed!\n'
			else:
				for j in urllv2:
					print '\t\tlv2 url:',j
					try:
						urllv3 = crawllv2(j)
					except:
						print 'WARNING: crawl lv3 url failed!\n'
					else:
						for k in urllv3.keys():
							print '\t\t\tlv3 url:',k,'\tname:',urllv3[k]
							addnum+=1
						print '\nbegin to download...\n'
						download(urllv3)
						print '\nWrite database...\n'
						writedata(databasepath,urllv3)
							
	print 'new added midi num:',addnum
	#print '\nbegin to download...\n'
	#download(totalresult)
	#print '\nWrite database...\n'
	#writedata(databasepath)
	print '\n\nDone!\n'