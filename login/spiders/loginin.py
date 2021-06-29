import scrapy

from ..items import DocumentspiderItem
import pymysql
import time
import scrapy,re
import urllib.request
from scrapy.http import Request,FormRequest
import os
import sys
import datetime

from PIL import Image
fpath = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
ffpath = os.path.abspath(os.path.join(fpath,".."))

sys.path.append(fpath)

import spiders.fpymysql.libmysql as mysqlhelper
from spiders.fpymysql.gettext import *



class LogininSpider(scrapy.Spider):
    name = 'document'
    allowed_domains = ['10.177.9.37:81/suichuan']
    start_urls = ['http://10.177.9.37:81/suichuan/']
    login_url = 'http://10.177.9.37:81/suichuan/loginJian.do'
    cookies = None

    headers={'Accept': 'text/html, application/xhtml+xml, */*','Referer': 'http://10.177.9.37:81/suichuan/index.do','Accept-Language': 'zh-CN','User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko','Accept-Encoding': 'gzip, deflate','Host': '10.177.9.37:81','Connection': 'Keep-Alive','Pragma': 'no-cache'} 
    


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




        dbconn = mysqlhelper.MYSQL(dbhost = '127.0.0.1', dbuser = 'root', dbpwd = '', dbname = 'study8', dbcharset = 'utf8')

        try:
            sql = 'select max(shijian) from documents;'
            res = dbconn.query(sql)

            startdate = res[0]['max(shijian)'][:10]

        except Exception as e:
            print(f">>存储-失败>>数据<>{e}")
            dbconn.rollback()
        pass

        now = datetime.datetime.now()
        delta = datetime.timedelta(days=15)
        n_days = now - delta
       

        enddate = time.strftime("%Y-%m-%d")

        print(f"{startdate}到{enddate}")

        for x in range(1,25,1):
            url='http://10.177.9.37:81/suichuan/document/ifr_list_query.jsp?subFrame=queryReceive&Page={}&CFWDW=&beginDate={}&endDate={}&CZTC=&CBT=&CWENHAO=&doctype=&gwSDate=&gwEDate=&year=&docFrom=&docStatus=&sort=default&archiveType='.format(x,n_days,enddate)
                
            print(url)
            yield scrapy.Request(url=url,callback=self.parse2,dont_filter=True,meta={'cookiejar': response.meta['cookiejar']},headers=self.headers)
            pass

        for x in range(1,25,1):
            url='http://10.177.9.37:81/suichuan/document/ifr_list_query.jsp?subFrame=queryReceive&Page={}&CFWDW=&beginDate=&endDate=&CZTC=&CBT=&CWENHAO=&doctype=&gwSDate=&gwEDate=&year=&docFrom=&docStatus=0&sort=default&archiveType='.format(x)

            print(url)
            yield scrapy.Request(url=url,callback=self.parse2,dont_filter=True,meta={'cookiejar': response.meta['cookiejar']},headers=self.headers)
            pass

    def parse2(self, response):

        # with open('itcast.html', 'wb') as f:
        #   f.write(response.body)
        # print(response.body)

        #print(response.text)
        
        node_list=response.xpath('//tr[@class="underline1"]')


        print(len(node_list))
        for node in node_list:
            items=DocumentspiderItem()
            items['bianhao']=node.xpath('./td/span[@class="rowSndisplay"]/@title').get()
            items['shijian']=node.xpath('./td/span[@class="rowDate"]/@title').get()
            items['danwei']=node.xpath('./td/span[@class="rowEntity"]/@title').get()
            items['wenhao']=node.xpath('./td/span[@class="rowWenHao"]/@title').get()
            # print(items)
            items['biaoti']=node.xpath('./td/a/span[@class="rowTitle"]/@title').get()
            items['zhuangtai']=node.xpath('./td/span[@id="f6"]/text()').get()
            items['leixing']=node.xpath('./td/span[@id="f7"]/text()').get()



            docid_str=node.xpath('./td[@class="idx_item2a"]/a/@href').get()
            docid_str=docid_str[(docid_str.index("&NDOCID=")+8):docid_str.index("&NDOCSORTID")]

            items['docid']=docid_str
            
            yield items

        