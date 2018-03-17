import time
from datetime import timedelta
from tornado import httpclient, gen, ioloop, queues
import codecs 
import random
import re
import hashlib


class AsyMethodGetSpider(object):
    def __init__(self, urls, concurrency):
        self.parseJS = 'http://192.168.100.81:8050'
        self.wait = 10

        self.urls = ['%s/render.html?url=%s&wait=%s'%(self.parseJS, url, self.wait) for url in urls]
        self.concurrency = concurrency
        self._q = queues.Queue()
        self._fetching = set()
        self._fetched = set()
    
    def proxy(self):
        return "http://192.168."+random.choice(['10', '11', '13', '14'])+"."+str(random.randrange(100,200))+":80"  
    
    @gen.coroutine
    def handle_data(self, response):
        if response.request.url.find('hot-search-list') != -1:
            (lambda f,d:(f.write(d), f.close()))(codecs.open('D:\\gongshang\\'+response.request.url.split('http://')[2].split('.')[0]+'.hot','w', encoding='utf8'), response.body.decode('utf8'))
            newurls = self.get_per_link(response)
            raise gen.Return(newurls)
        else:
            md5_url = self.md5_str(response.request.url)
            (lambda f,d:(f.write(d), f.close()))(codecs.open('D:\\gongshang\\perpage\\'+response.request.url.split('http://')[2].split('.')[0]+md5_url+'.per','w', encoding='utf8'), response.body.decode('utf8'))
        print('打印GET结果：url:%s, bytes:%s'%(response.request.url, len(response.body)))
        

    @gen.coroutine
    def method_get(self, url):
        try:
            response = yield httpclient.AsyncHTTPClient().fetch('%s&proxy=%s'%(url, self.proxy()))
            print('GET请求完成： %s' % url)
        except Exception as e:
            print('GET请求错误: %s %s' % (e, url))
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
                print('GET正在请求： %s' % current_url)
                self._fetching.add(current_url)
                response = yield self.method_get(current_url)

                
                if response:
                    if len(response.body) > 10000:

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
        print('GET完成共用： %d 秒, 完成请求的url个数: %s.' % (time.time() - start, len(self._fetched)))

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
    #urls = ['http://bj.gsxt.gov.cn/corp-query-entprise-info-hot-search-list.html?province=110000',]
    s = AsyMethodGetSpider(urls, 100)
    s.get()

if __name__ == '__main__':
    main()
    
    
#GET完成共用： 965 秒, 完成请求的url个数: 301.
