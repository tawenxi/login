import scrapy

from ..items import DocumentspiderItem
import pymysql
import time
import scrapy,re
import urllib.request
from scrapy.http import Request,FormRequest
import os
import sys


from PIL import Image
fpath = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
ffpath = os.path.abspath(os.path.join(fpath,".."))

sys.path.append(fpath)
from spiders.fpymysql.gettext import *
import spiders.fpymysql.libmysql as mysqlhelper




class LinkspiderSpider(scrapy.Spider):
	name = 'linkspider'
	allowed_domains = ['10.177.9.37:81/suichuan']
	start_urls = ['http://10.177.9.37:81/suichuan/']
	login_url = 'http://10.177.9.37:81/suichuan/loginJian.do'
	cookies = None

	headers={'Host': '10.177.9.37:81','Connection': 'keep-alive','User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko','Accept': 'text/html, application/xhtml+xml, */*','Referer': 'http://10.177.9.37:81/suichuan/document/operation_form.jsp?NDOCID=148654004&NDOCSORTID=1&NPROCID=20&subFrame=doLogin&Page=0&dir=&newCPQB=&leaderId=0&nbfw=','Accept-Encoding': 'gzip, deflate','Accept-Language': 'zh-CN'}  



	def parse(self, response):
		# 拼凑当前验证码对应的 url
		print("*"*20)
		img_url = 'http://10.177.9.37:81/suichuan/validateCode'
		yield scrapy.Request(url=img_url, meta={'cookiejar': 1}, callback=self.parse_postdata,dont_filter=True,headers=self.headers)

	def parse_postdata(self, response):

		print("正在登录...................")
		form_data = {
			'loginName': 'liuxiaoyong',
			'password': 'xy965589',

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
		yield Request("http://10.177.9.37:81/suichuan/index.do", meta={'cookiejar': True}, callback=self.parse_manager,dont_filter=True,headers=self.headers)


	# 保存文件
	def parse_manager(self, response):
		tuichu = response.xpath('//a[@href="loginForm.do"]/text()').get()
		if tuichu == '退出':
			print('登录成功')
			# temp = response.request.headers.getlist('Cookie')[0]
			# cookies = {i.split('=')[0]: i.split('=')[1] for i in temp.split(';')}
			# self.cookies = cookies
			# print(Cookie)




		try:
			self.conn = pymysql.Connect(host='127.0.0.1', port=3306, user='root', password='', db='study8', charset='utf8')
			print('连接成功>')
		except Exception as e:
			print(f'连接失败!!>{e}')
			exit()  # 可以直接结束运行，按需求来设定

		self.cursor = self.conn.cursor()

		try:
			row_count = self.cursor.execute("select docid,biaoti from documents WHERE `chengbanren` = '无' limit 3000;")
			print("SQL 语句查询的行数%d" % row_count)
			
			for line in self.cursor.fetchall():
				url = 'http://10.177.9.37:81/suichuan/document/ifr_docinfo_msg.jsp?NDOCID='+line[0]+'&NDOCSORTID=2&subFrame=doWaiting&NPROCID=19'

				# url=self.url.format(j)
				# print('begin')
				yield scrapy.Request(url=url,callback=self.parse2,meta={'docid':line[0],'cookiejar': True},dont_filter=True,headers=self.headers)
				# print(url)

		except Exception as e:
			print(f">>查询失败>>{e}")
			self.conn.rollback()
		# for x in range(1,60,1):
		# 	url='http://10.177.9.37:81/suichuan/document/ifr_list_query.jsp?subFrame=queryReceive&Page={}&CFWDW=&beginDate=&endDate=&CZTC=&CBT=&CWENHAO=&doctype=&gwSDate=&gwEDate=&year=2014&docFrom=&docStatus=3&sort=default&archiveType='.format(x)
		# 	temp = ' JSESSIONID='+self.cookies
		# 	cookies = {i.split('=')[0]: i.split('=')[1] for i in temp.split(';')}
		# 	# url=self.url.format(j)
		# 	yield scrapy.Request(url=url,callback=self.parse,cookies=cookies)
		# 	pass



	def parse2(self, response):

		chengbanren=response.xpath("//font[contains(text()[2],'(收文)承办')]/text()").get()
		chengbanren=chengbanren[(chengbanren.index(":")+7):chengbanren.index("同志")]


		docid = response.meta['docid']

		

		if chengbanren == '刘小勇':
			chengbanren = '办公室'
		if chengbanren == '郭爱华':
			chengbanren = '人事股'
		if chengbanren == '黄频':
			chengbanren = '规财股'
		if chengbanren == '张文军':
			chengbanren = '医政股'
		if chengbanren == '蒋琳':
			chengbanren = '法监股'
		if chengbanren == '刘海山':
			chengbanren = '基妇股'
		if chengbanren == '李玲':
			chengbanren = '人口股'
		if chengbanren == '肖明桂':
			chengbanren = '老年股'
		if chengbanren == '杨路生':
			chengbanren = '疾控股'
		if chengbanren == '李剑华':
			chengbanren = '科教股'
		if chengbanren == '李海香':
			chengbanren = '协会办'
		if chengbanren == '黄少琼':
			chengbanren = '党办'
		if chengbanren == '邱天翰':
			chengbanren = '党办'
		print(chengbanren,docid)

		
		try:
			self.conn = pymysql.Connect(host='127.0.0.1', port=3306, user='root', password='', db='study8', charset='utf8')
			# print('连接成功>')
		except Exception as e:
			print(f'连接失败!!>{e}')
			exit()  # 可以直接结束运行，按需求来设定

		self.cursor = self.conn.cursor()

		try:
			sql = "update documents set chengbanren = '{}' where docid = '{}'".format(chengbanren,docid)
			print(sql)
			row_count = self.cursor.execute(sql)
			# print("SQL 语句更新的行数%d" % row_count)
			self.conn.commit()
		except Exception as e:
			print(f">>更新失败>>数据<{docid}>{e}")
			self.conn.rollback()


