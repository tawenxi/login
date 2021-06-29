import scrapy

from ..items import DocumentspiderItem
import pymysql
import time
import scrapy,re
import urllib.request
from scrapy.http import Request,FormRequest
import os
import sys
from login.items import BmwItem

from urllib import request
import re
from datetime import datetime
from PIL import Image

fpath = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
ffpath = os.path.abspath(os.path.join(fpath,".."))

sys.path.append(fpath)
from spiders.fpymysql.gettext import *
import spiders.fpymysql.libmysql as mysqlhelper




class LoadSpider(scrapy.Spider):
	name = 'load'
	allowed_domains = ['10.177.9.37:81/suichuan']
	start_urls = ['http://10.177.9.37:81/suichuan/']
	login_url = 'http://10.177.9.37:81/suichuan/loginJian.do'
	cookies = None
	mydoc = None

	headers={'Accept': 'text/html, application/xhtml+xml, */*','Referer': 'http://10.177.9.37:81/suichuan/index.do','Accept-Language': 'zh-CN','User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko','Accept-Encoding': 'gzip, deflate','Host': '10.177.9.37:81','Connection': 'Keep-Alive','Pragma': 'no-cache'} 


	def __init__(self, mydoc=None, *args, **kwargs):
	    super(LoadSpider, self).__init__(*args, **kwargs)

	    if mydoc:
	    	self.mydoc = mydoc.split('.')
	    pass


	def parse(self, response):
		# 拼凑当前验证码对应的 url
		print("*"*20)
		img_url = 'http://10.177.9.37:81/suichuan/validateCode'
		yield scrapy.Request(url=img_url, meta={'cookiejar': 1}, callback=self.parse_postdata,dont_filter=True,headers=self.headers)

	def parse_postdata(self, response):

		print("正在登录...................")
		form_data = {
			'loginName': 'liuxiaoyong',
			'password': 'lml1989',

		}

		# 保存验证码图片 并且自动打开后 人工输入验证码
		fp = open('验证码.png', 'wb')
		fp.write(response.body)
		fp.close()

		captcha = gettext()
		captcha = captcha.replace('B', "8") 
		print("识别验证码为："+captcha)



		# captcha = input("请输入验证码： ")
		# 完善 formdata中空着的 numcode
		form_data['validateCode'] = captcha

		#return [FormRequest.from_response(response, url=self.login_url, meta={'cookiejar': response.meta['cookiejar']}, headers=self.headers, formdata=form_data, callback=self.parse_afterlogin)]
		yield scrapy.FormRequest(url=self.login_url, meta={'cookiejar': response.meta['cookiejar']}, headers=self.headers, formdata=form_data, callback=self.parse_afterlogin,dont_filter=True)


	# 登录后继续使用该cookie信息去访问登录后才能访问的页面，就不会被拦截到登录页面了
	def parse_afterlogin(self, response):
		# 访问登陆后才能访问的页面http://i.mooc.chaoxing.com/settings/info?t=1594542872701
		yield Request("http://10.177.9.37:81/suichuan/index.do", meta={'cookiejar': True}, callback=self.parse_manager,dont_filter=True)


	# 保存文件
	def parse_manager(self, response):
		tuichu = response.xpath('//a[@href="loginForm.do"]/text()').get()
		if tuichu == '退出':
			print('登录成功')
			# temp = response.request.headers.getlist('Cookie')[0]
			# cookies = {i.split('=')[0]: i.split('=')[1] for i in temp.split(';')}
			# self.cookies = cookies
			# print(Cookie)




		url='http://10.177.9.37:81/suichuan/document/list_doLogin.jsp?sysUserID=63904&sysUserCurrentEntityId=120204&sysUserBelongedEntityId=120104'


		yield scrapy.Request(url=url,callback=self.parse20,meta={'cookiejar': 1},dont_filter=True,headers=self.headers)



	def parse20(self, response):


		if not self.mydoc:
			node_list=response.xpath('//tr[@class="idx_item2a"]')

			print('新到来文数据',len(node_list))


			for node in node_list:

				docid = node.xpath('.//a/@href').get()

				docidstr=docid[(docid.index("&NDOCID=")+8):docid.index("&NDOCSORTID")]

				link = self.downloadby(docidstr)

				yield scrapy.Request(url=link,callback=self.parse2,dont_filter=True,meta={'cookiejar': 1},headers=self.headers)
		else:

			for docidstr in self.mydoc:
				link = self.downloadby(docidstr)

				yield scrapy.Request(url=link,callback=self.parse2,dont_filter=True,meta={'cookiejar': 1},headers=self.headers)
				pass

	def downloadby(self, docidstr):
		link = 'http://10.177.9.37:81/suichuan/document/ifr_docinfo_file.jsp?NDOCID={}&NDOCSORTID=2&subFrame=doWaiting&NPROCID=19&showCPQB=&newCPQB=0'.format(docidstr)
		return link
		


	def parse2(self, response):



		#biaoti = response.meta['biaoti']
		file_nodes = response.xpath('//tr[@class="secondRightContent"]')
		#print(len(file_nodes))
		re_result = re.search(r"(202\d{1}-\d{2}-\d{2})",response.text)
		date_time = '['+re_result.group(0)+']'
		print(date_time)
		for index, node in enumerate(file_nodes):
			wenjianming = node.xpath('.//a/text()').get()
			if index == 0:
				biaoti = date_time+wenjianming
				pass
			filepagelink = node.xpath('.//a/@href').get()
			wenjianming = node.xpath('.//a/text()').get()
			filepagelink = 'http://10.177.9.37:81/suichuan/document/'+filepagelink


			yield scrapy.Request(url=filepagelink,callback=self.parse3,dont_filter=True,meta={'date_time':date_time,'biaoti':biaoti,'wenjianming':wenjianming,'cookiejar': response.meta['cookiejar']},headers=self.headers)
		pass


	def parse3(self, response):
		print('==============================')

		biaoti = response.meta['biaoti']
		date_time = response.meta['date_time']
		wenjianming = response.meta['wenjianming']

		#print('=================='+str(wenjianming)+'==================')

		body = str(response.text)

		file=body[(body.index('//方正打印')+152):(body.index('var URLPath = igrpUrlHeader'))]

		if len(file)>50:
			file=file[(file.index('FILENAME=')+9):(file.index('&flag='))]
			pass
		file = file.rstrip('";\r\n\t')
		# print(file)
		file = 'http://10.177.9.37:81/suichuan/downLoadFileServlet?FILENAME='+file
		partname = biaoti
		urls = [file]

		# print(partname)
		# print(urls)
		item = BmwItem(partname=partname, urls=urls,wenjianming = wenjianming )


		print('#'*100)

		print(item)

		print('#'*100)
		



		filepath = os.path.join(os.path.dirname(__file__),"images")
		if not os.path.exists(filepath):
			os.mkdir(filepath)

		datefd = os.path.join(filepath,time.strftime("%Y%m%d"))
		if not os.path.exists(datefd):
			os.mkdir(datefd)


		partname = item['partname']
		urls = item['urls']



		partpath = os.path.join(datefd,partname)
		if not os.path.exists(partpath):
			os.mkdir(partpath)
		for url in urls:

			imagename = item['wenjianming']

			filetype = url[(url.index('NAME=')+5):]
			filetype = filetype[(filetype.index('.')):]
			imagename = imagename+filetype
			#print(url)
			# print(self.path,imagename)

			print(item['partname'],imagename)
			request.urlretrieve(url,os.path.join(partpath,imagename))


			print('下载成功')
