

BOT_NAME = 'login'

SPIDER_MODULES = ['login.spiders']
NEWSPIDER_MODULE = 'login.spiders'



ROBOTSTXT_OBEY = False

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'

COOKIES_ENABLED = True


USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'


DEFAULT_REQUEST_HEADERS = {
'Host': '10.177.9.37:81',
'Connection': 'keep-alive',
'Upgrade-Insecure-Requests': 1,
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'Referer': 'http://10.177.9.37:81/suichuan/document/operation_form.jsp?NDOCID=148654004&NDOCSORTID=1&NPROCID=20&subFrame=doLogin&Page=0&dir=&newCPQB=&leaderId=0&nbfw=',
'Accept-Encoding': 'gzip, deflate',
'Accept-Language': 'zh-CN,zh;q=0.9'
}

ITEM_PIPELINES = {
   'login.pipelines.LoginPipeline': 300,
   # 'login.pipelines.BmwPipeline': 299,
}
