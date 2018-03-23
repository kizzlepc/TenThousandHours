import time
from datetime import timedelta
from tornado import httpclient, gen, ioloop, queues
import codecs 
import random
import re
import hashlib
import json
from sqlalchemy.orm import sessionmaker
import mysqloperation
from datetime import datetime
from contextlib import closing
import logging  
from logging.handlers import TimedRotatingFileHandler 


def create_logger():
    logFilePath = "D:\\log\\access_log"  
    logger = logging.getLogger("YouLoggerName")  
    logger.setLevel(logging.INFO)  
    
    handler = TimedRotatingFileHandler(logFilePath,  
                                       when="d",  
                                       interval=1,  
                                       backupCount=7)  
    
    
    formatter = logging.Formatter('%(message)s')  
      
    handler.setFormatter(formatter)  
      
    logger.addHandler(handler)  
    return logger


class AsyMethodGetSpider(object):
    def __init__(self, urls, concurrency):
        self.parseJS = 'http://192.168.100.81:8050'
        self.wait = 10

        self.urls = ['%s/render.html?url=%s&wait=%s'%(self.parseJS, url, self.wait) for url in urls]
        self.concurrency = concurrency
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()
        self.logger = create_logger()
    
    def proxy(self):
        return "http://192.168."+random.choice(['10', '11',])+"."+str(random.randrange(100,200))+":80"  

    def parse_re(self, strs, source):
        try:
            res = re.search(strs, source, re.S).group(1)
            return re.sub(r'<.+?>', '', res)
        except:
            return ''
        
    @gen.coroutine   
    def save_mysql(self, response, md5_url):
        html_source = response.body.decode('utf8')
        html = re.sub(r'\s*', '', html_source)
        html = re.sub(r'负责人：', '法定代表人：', html)
        html = re.sub(r'投资人：', '法定代表人：', html)
        html = re.sub(r'执行事务合伙人:', '法定代表人：', html)
        html = re.sub(r'营业场所：', '住所：', html)
        html = re.sub(r'主要经营场所：', '住所：', html)
        html = re.sub(r'业务范围：', '经营范围：', html)
        html = re.sub(r'成员出资总额：', '注册资本：', html)
        html = re.sub(r'合伙期限自：', '营业期限自：', html)
        html = re.sub(r'合伙期限至：', '营业期限至：', html)
        html = re.sub(r'合&nbsp;&nbsp;&nbsp;伙&nbsp;&nbsp;&nbsp;期&nbsp;&nbsp;&nbsp;限', '营&nbsp;&nbsp;&nbsp;业&nbsp;&nbsp;&nbsp;期&nbsp;&nbsp;&nbsp;限', html)
        html = re.search(r'<divclass=\"bgPop\">(.+?)业务咨询与技术支持联系方式', html, re.S).group(1)
        province_short = response.request.url.split('http://')[2].split('.')[0]
        
        social_code = self.parse_re(r'<dtclass=.+?>统一社会信用代码：</dt>(.+?)</dd>', html)
        enterprise_name = self.parse_re(r'<dtclass=.+?>企业名称：</dt>(.+?)</dd>', html)
        company_type = self.parse_re(r'<dtclass=.+?>类型：</dt>(.+?)</dd>', html)
        legal_person = self.parse_re(r'<dtclass=.+?">法定代表人：</dt>(.+?)</dd>', html)
        reg_capital = self.parse_re(r'<dtclass=.+?>注册资本：</dt>(.+?)</dd>', html) 
        build_date = self.parse_re(r'<dtclass=.+?>成立日期：</dt>(.+?)</dd>', html)
        build_date = re.sub(r'年|月|日', '-', build_date).strip('-')
        period_from = self.parse_re(r'<dtclass=.+?>营业期限自：</dt>(.+?)</dd>', html)
        period_to = self.parse_re(r'<dtclass=.+?>营业期限至：</dt>(.+?)</dd>', html)
        
        period2 = self.parse_re(r'<tdclass=.+?>营&nbsp;&nbsp;&nbsp;业&nbsp;&nbsp;&nbsp;期&nbsp;&nbsp;&nbsp;限</td>(.+?)</td>', html)
        period_from2 = ''
        period_to2 = ''
        if period2:
            period_from2 = period2.split('至')[0]
            period_to2 = period2.split('至')[1]
        
        reg_authority = self.parse_re(r'<dtclass=.+?>登记机关：</dt>(.+?)</dd>', html)
        approved_date = self.parse_re(r'<dtclass=.+?>核准日期：</dt>(.+?)</dd>', html)
        approved_date = re.sub(r'年|月|日', '-', approved_date).strip('-')
        reg_status = self.parse_re(r'<dtclass=.+?>登记状态：</dt>(.+?)</dd>', html)
        address = self.parse_re(r'<dtclass=.+?>住所：</dt>(.+?)</dd>', html)
        range = self.parse_re(r'<dtclass=.+?>经营范围：</dt>(.+?)</dd>', html)
        province = province_short+md5_url
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # 采集时间

        try:
            with closing(sessionmaker(bind=mysqloperation.MysqlOpration.get_engine())()) as session:               
                hot = mysqloperation.HotTable()
                hot.id = 0
                if social_code:
                    hot.social_code = social_code
                if enterprise_name:
                    hot.enterprise_name = enterprise_name 
                if company_type:
                    hot.company_type = company_type
                if legal_person:
                    hot.legal_person = legal_person
                if reg_capital:
                    hot.reg_capital = reg_capital
                if build_date:
                    hot.build_date = build_date
                if period_from:
                    hot.period_from = period_from
                else:
                    if period_from2:
                        hot.period_from = period_from2
                if period_to:
                    hot.period_to = period_to
                else:
                    if period_to2:
                        hot.period_to = period_to2                                       
                if approved_date:
                    hot.approved_date = approved_date
                if reg_authority:
                    hot.reg_authority = reg_authority
                if reg_status:
                    hot.reg_status = reg_status
                if address:
                    hot.address = address
                if range:
                    hot.range = range
                hot.province = province
                hot.create_time = create_time
                hot.update_date = create_time

                query_objs = session.query(mysqloperation.HotTable).filter(mysqloperation.HotTable.enterprise_name==enterprise_name).first()

                if query_objs:
                    shijian = query_objs.create_time
                    delta = (datetime.now()-datetime.strptime(str(shijian), '%Y-%m-%d %H:%M:%S')).days
                    if delta < 360:
                        #print('ok')
                        #(lambda f,d:(f.write(d+'\n'), f.close()))(codecs.open('record.txt', 'a'), enterprise_name)
                        self.logger.info('已存在----------：'+enterprise_name)
                    else:                               
                        self.logger.info('更新记录##########：'+enterprise_name)
                else:
                    session.add(hot)
                    session.commit()  
                    self.logger.info('新记录插入:$$$$$$$$$$:'+enterprise_name)
                
        except Exception as e:
            (lambda f,d:(f.write(d+'\n'), f.close()))(codecs.open('record.txt', 'a'), enterprise_name)
            #(lambda f,d:(f.write(d+'\n'), f.close()))(codecs.open('record.txt', 'a'), str(e))
            self.logger.info('入库异常!!!!!!!!!!：%s %s %s'%(enterprise_name, province))
            pass
   
    @gen.coroutine
    def handle_data(self, response):
        if response.request.url.find('hot-search-list') != -1:
            (lambda f,d:(f.write(d), f.close()))(codecs.open('D:\\gongshang\\'+response.request.url.split('http://')[2].split('.')[0]+'.hot2','w', encoding='utf8'), response.body.decode('utf8'))
            newurls = self.get_per_link(response)
            raise gen.Return(newurls)
        else:
            md5_url = self.md5_str(response.request.url)
            (lambda f,d:(f.write(d), f.close()))(codecs.open('D:\\gongshang\\newperpage\\'+response.request.url.split('http://')[2].split('.')[0]+md5_url+'.per','w', encoding='utf8'), response.body.decode('utf8'))
        self.logger.info('打印GET结果==========：url:%s, bytes:%s'%(response.request.url, len(response.body)))
        yield self.save_mysql(response, md5_url)
        
        
    @gen.coroutine
    def method_get(self, url):
        try:
            response = yield httpclient.AsyncHTTPClient().fetch('%s&proxy=%s'%(url, self.proxy()))
            #self.logger.info('GET请求完成： %s' % url)
            #print(response.body)
        except Exception as e:
            #self.logger.info('GET请求错误: %s %s' % (e, url))
            raise gen.Return('')
        raise gen.Return(response)
    
    
    def get_per_link(self, response):
        per_page = response.body.decode('utf8')
        fixed = '.gsxt.gov.cn'
        per_url_province = response.request.url.split('http://')[2].split('.')[0]
        per_links = re.findall(r'</i><a href=\"(.+?)\"', per_page, re.S)
        abs_links = ['http://%s%s%s'%(per_url_province, fixed, link) for link in per_links]
        return abs_links

    def md5_str(self, _str):
        strs = str(_str)
        m = hashlib.md5(strs.encode('utf8'))
        return m.hexdigest()  
      
    @gen.coroutine
    def _run(self):
        start = time.time()
        @gen.coroutine
        def fetch_url():
            current_url = yield self._q.get()
            try:
                if current_url in self._fetching:
                    return
                #self.logger.info('GET正在请求： %s' % current_url)
                self._fetching.add(current_url)
                response = yield self.method_get(current_url)

                
                if response:
                    if response.body.decode('utf8').find('业务咨询与技术支持联系方式') != -1:

                        newurls = yield self.handle_data(response)
                        self._fetched.add(current_url)
                        
                        if newurls:
                            add_urls = ['%s/render.html?url=%s&wait=%s'%(self.parseJS, url, self.wait) for url in newurls]
                            for add_url in add_urls:
                                yield self._q.put(add_url)

                    else:
                        self._fetching.remove(current_url)
                        yield self._q.put(current_url)                        
                else:
                    self._fetching.remove(current_url)
                    yield self._q.put(current_url)

            finally:
                self._q.task_done()

        @gen.coroutine
        def worker():
            while True:
                yield fetch_url()
  

        for url in self.urls:
            yield self._q.put(url)

        for _ in range(self.concurrency):
            worker()
        yield self._q.join()   
        assert self._fetching == self._fetched
        self.logger.info('GET完成共用： %d 秒, 完成请求的url个数: %s.' % (time.time() - start, len(self._fetched)))

    def get(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)


def main():
    base_url = 'http://{0}/corp-query-entprise-info-hot-search-list.html?province={1}'
    province_home = {'www.gsxt.gov.cn': 100000, 'bj.gsxt.gov.cn': 110000, 'tj.gsxt.gov.cn': 120000, 
                     'he.gsxt.gov.cn': 130000, 'sx.gsxt.gov.cn': 140000, 'nm.gsxt.gov.cn': 150000, 
                     'ln.gsxt.gov.cn': 210000, 'jl.gsxt.gov.cn': 220000, 'hl.gsxt.gov.cn': 230000, 
                     'sh.gsxt.gov.cn': 310000, 'js.gsxt.gov.cn': 320000, 'zj.gsxt.gov.cn': 330000, 
                     'ah.gsxt.gov.cn': 340000, 'fj.gsxt.gov.cn': 350000, 'jx.gsxt.gov.cn': 360000, 
                     'sd.gsxt.gov.cn': 370000, 'gd.gsxt.gov.cn': 440000, 'gx.gsxt.gov.cn': 450000, 
                     'hi.gsxt.gov.cn': 460000, 'ha.gsxt.gov.cn': 410000, 'hb.gsxt.gov.cn': 420000, 
                     'hn.gsxt.gov.cn': 430000, 'cq.gsxt.gov.cn': 500000, 'sc.gsxt.gov.cn': 510000, 
                     'gz.gsxt.gov.cn': 520000, 'yn.gsxt.gov.cn': 530000, 'xz.gsxt.gov.cn': 540000, 
                     'sn.gsxt.gov.cn': 610000, 'gs.gsxt.gov.cn': 620000, 'qh.gsxt.gov.cn': 630000, 
                     'nx.gsxt.gov.cn': 640000, 'xj.gsxt.gov.cn': 650000}

    urls = [base_url.format(*n) for n in province_home.items()]
    s = AsyMethodGetSpider(urls, 100)
    s.get()
    
if __name__ == '__main__':
    main()   
    
#GET完成共用： 965 秒, 完成请求的url个数: 301.
#GET完成共用： 3231 秒, 完成请求的url个数: 301.
#GET完成共用： 15359 秒, 完成请求的url个数: 9610.
